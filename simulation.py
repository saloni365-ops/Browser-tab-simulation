# simulation.py
# High-accuracy simulation driver using EnhancedPredictor + MemoryManager.

import random
import csv
import time
from predictive_model import EnhancedPredictor
from memory_manager import MemoryManager

def generate_synthetic_user_pattern(tab_ids, steps=1000, hotspot_size=5, hotspot_stay_prob=0.95):
    """
    Generate a sequence with strong locality (hotspot set).
    - hotspot_size: how many tabs are 'hot' (user focuses on these)
    - hotspot_stay_prob: probability to remain within hotspot (high for predictable cycles)
    Returns: seq (list of tab ids), hotspot (set)
    """
    if hotspot_size < 1:
        hotspot_size = max(1, len(tab_ids) // 10)
    hotspot = set(random.sample(tab_ids, min(hotspot_size, len(tab_ids))))
    hotspot_list = list(hotspot)
    # start in a hotspot tab to ensure warmup learns hotspot patterns
    cur = random.choice(hotspot_list)
    seq = []
    for _ in range(steps):
        if random.random() < hotspot_stay_prob:
            # If current not in hotspot_list (maybe chosen earlier randomly), pick one deterministically
            if cur not in hotspot_list:
                cur = random.choice(hotspot_list)
            else:
                # pick next in deterministic cycle with small jitter
                idx = hotspot_list.index(cur)
                if random.random() < 0.85:
                    cur = hotspot_list[(idx + 1) % len(hotspot_list)]
                else:
                    cur = random.choice(hotspot_list)
        else:
            # occasional jump to any tab
            cur = random.choice(tab_ids)
        seq.append(cur)
    return seq, hotspot

def run_simulation(num_tabs=30,
                   steps=1000,
                   memory_limit_mb=1200,
                   hotspot_size=5,
                   warmup_frac=0.6,
                   log_csv='metrics.csv',
                   show_terminal_output=False):
    """
    Run the simulation:
      - num_tabs: total number of tabs (20-50 recommended)
      - steps: total sequence length (warmup + test)
      - memory_limit_mb: RAM limit for MemoryManager
      - hotspot_size: number of hot tabs (small to keep pattern predictable)
      - warmup_frac: fraction of steps used to pretrain predictor (default 0.6)
    Returns:
      summary dict with avg_latency_ms, prediction_accuracy_top1, prediction_accuracy_top3, prefetch_hit_rate, tab_sizes, hotspot
    """
    # Initialize tab ids and sizes
    tab_ids = [f"tab_{i}" for i in range(num_tabs)]
    tab_sizes = {tid: random.randint(60, 300) for tid in tab_ids}

    # Setup memory manager and predictor
    mm = MemoryManager(tab_sizes, memory_limit_mb=memory_limit_mb)
    predictor = EnhancedPredictor()

    # Generate synthetic sequence
    seq, hotspot = generate_synthetic_user_pattern(tab_ids, steps=steps, hotspot_size=hotspot_size, hotspot_stay_prob=0.95)

    # Split into warmup (train) and test
    warmup_len = int(len(seq) * warmup_frac)
    if warmup_len < 1:
        warmup_len = max(1, len(seq)//2)
    train_seq = seq[:warmup_len]
    test_seq = seq[warmup_len:]

    # Warm-up: feed sequence into predictor with decay weighting
    predictor.feed_sequence(train_seq, decay=0.995)

    # Also simulate prefetch & memory interactions during warmup so caches are realistic
    prev = None
    for cur in train_seq:
        preds = predictor.predict_topk(prev, None, top_k=3, all_tabs=tab_ids)
        if preds:
            mm.prefetch(preds)
        mm.access_tab(cur)
        # update predictor online to reflect warmup transitions as well
        predictor.update(prev, cur)
        prev = cur

    # Test / measurement
    total_accesses = 0
    correct_top1 = 0
    correct_top3 = 0
    total_latency = 0.0
    total_prefetch_hits = 0

    # CSV logging of per-step metrics (test period)
    with open(log_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            'step', 'current_tab', 'predicted_top1', 'predicted_top3',
            'prediction_match_top1', 'prediction_match_top3', 'prefetched', 'latency_ms'
        ])
        writer.writeheader()

        # Initialize prev for test as last element of train_seq
        prev = train_seq[-1] if train_seq else None
        # For second-order predictor, we can derive prev_prev from history: but we keep a local prev_prev variable
        prev_prev = None
        if len(train_seq) >= 2:
            prev_prev = train_seq[-2]
        # Iterate test sequence and measure
        for i, cur in enumerate(test_seq, start=1):
            preds = predictor.predict_topk(prev, prev_prev, top_k=3, all_tabs=tab_ids)
            predicted_top3 = preds
            predicted_top1 = preds[0] if preds else None

            # Prefetch predicted top3
            if preds:
                mm.prefetch(preds)

            latency, prefetch_hit = mm.access_tab(cur)
            latency_ms = latency * 1000.0
            total_latency += latency
            if prefetch_hit:
                total_prefetch_hits += 1

            match1 = int(predicted_top1 == cur)
            match3 = int(cur in predicted_top3)
            correct_top1 += match1
            correct_top3 += match3
            total_accesses += 1

            writer.writerow({
                'step': i,
                'current_tab': cur,
                'predicted_top1': predicted_top1,
                'predicted_top3': ','.join(predicted_top3),
                'prediction_match_top1': match1,
                'prediction_match_top3': match3,
                'prefetched': int(prefetch_hit),
                'latency_ms': round(latency_ms, 3)
            })

            # Online update after observing the real transition prev -> cur
            predictor.update(prev, cur)

            # shift prev_prev / prev
            prev_prev = prev
            prev = cur

            # optional lightweight terminal progress
            if show_terminal_output and (i % 100 == 0 or i == 1 or i == len(test_seq)):
                print(f"Test step {i}/{len(test_seq)}: current={cur}, predicted_top1={predicted_top1}, prefetched={prefetch_hit}, latency_ms={latency_ms:.2f}")

    # Compute summary metrics
    avg_latency_ms = (total_latency / total_accesses) * 1000.0 if total_accesses else 0.0
    top1_acc = correct_top1 / total_accesses if total_accesses else 0.0
    top3_acc = correct_top3 / total_accesses if total_accesses else 0.0
    prefetch_hit_rate = total_prefetch_hits / total_accesses if total_accesses else 0.0

    summary = {
        'avg_latency_ms': round(avg_latency_ms, 3),
        'prediction_accuracy_top1': round(top1_acc, 4),
        'prediction_accuracy_top3': round(top3_acc, 4),
        'prefetch_hit_rate': round(prefetch_hit_rate, 4),
        'total_accesses': total_accesses,
        'tab_sizes': tab_sizes,
        'hotspot': list(hotspot)
    }

    if show_terminal_output:
        print("\nSimulation complete. Summary:")
        for k, v in summary.items():
            if k == 'tab_sizes':
                print("Tab sizes (MB):")
                for t, s in v.items():
                    print(f"  {t}: {s}")
            else:
                print(f"  {k}: {v}")

    return summary
