# simulation.py
from tab import Tab
from memory_manager import MemoryManager
import suspend_restore
import random, time, csv
import sys

def make_tabs(n):
    tabs = []
    for i in range(n):
        base = random.randint(30, 300)
        extra = random.randint(0, 200)
        t = Tab(tab_id=f"tab_{i+1}", base_memory_mb=base, extra_memory_mb=extra)
        for _ in range(random.randint(0, 8)):
            t.update_working_set(random.randint(1, 500))
        tabs.append(t)
    return tabs

def run_simulation(n_tabs=12, ticks=200, system_limit_mb=1000, policy='working_set'):
    manager = MemoryManager(system_limit_mb=system_limit_mb)
    tabs = make_tabs(n_tabs)
    for t in tabs:
        manager.add_tab(t)

    memory_trace = []
    suspend_events = 0
    restore_events = 0
    latency_values = []

    for tick in range(ticks):
        active = random.choice(tabs)
        # Randomly decide to switch to a suspended tab (simulate user click)
        if active.is_suspended and random.random() < 0.5:
            latency = suspend_restore.restore_tab(active, use_snapshot=True, simulate_sleep=False)
            restore_events += 1
            latency_values.append(latency)
            continue

        # simulate activity on active tab
        active.simulate_activity(intensity=random.choice(['low','normal','high']))

        # enforce policy (protect active tab)
        suspended = manager.enforce_policy(policy=policy, protect_tab_id=active.tab_id, simulate_sleep=False)
        suspend_events += len(suspended)

        memory_trace.append(manager.total_memory_usage())

    # summary
    summary = (
        f"=== Simulation summary ===\n"
        f"Final memory usage (MB): {manager.total_memory_usage()}\n"
        f"Tabs total: {len(tabs)}\n"
        f"Total suspensions: {suspend_events}\n"
        f"Total restores: {restore_events}\n"
    )
    if latency_values:
        summary += (
            f"Avg restore latency (s): {sum(latency_values)/len(latency_values)}\n"
            f"Max restore latency (s): {max(latency_values)}\n"
        )
    else:
        summary += "No restores recorded\n"

    print(summary)

    # write trace CSV
    with open("memory_trace.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tick","mem_mb"])
        for i, m in enumerate(memory_trace):
            writer.writerow([i, m])

if __name__ == "__main__":
    # Support command-line arguments for Streamlit frontend
    if len(sys.argv) > 1:
        try:
            n_tabs = int(sys.argv[1])
            ticks = int(sys.argv[2])
            system_limit_mb = int(sys.argv[3])
            policy = sys.argv[4]
            run_simulation(n_tabs, ticks, system_limit_mb, policy)
        except Exception as e:
            print(f"Error parsing arguments: {e}")
            print("Running with default parameters...")
            run_simulation()
    else:
        run_simulation()
