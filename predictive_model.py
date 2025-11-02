# predictive_model.py
# Enhanced predictor: second-order Markov + recency weighting + safe fallbacks.

from collections import defaultdict, Counter, deque
import random

class EnhancedPredictor:
    """
    Combines first-order and second-order Markov counts with recency weighting.
    Methods:
      - feed_sequence(seq, decay=0.995) : warm-up training on a sequence (weights recent transitions more)
      - update(prev_tab, next_tab) : online update after observing a transition
      - predict_topk(prev_tab, prev_prev_tab=None, top_k=3, all_tabs=None) : return list of predicted tab ids
      - sample_next(prev_tab, prev_prev_tab=None, all_tabs=None) : probabilistic sample
    """

    def __init__(self):
        self.first = defaultdict(Counter)   # prev -> Counter(next)
        self.second = defaultdict(Counter)  # (prev2, prev1) -> Counter(next)
        self.history = deque(maxlen=1000)   # store recent tabs for building second-order counts

    def update(self, prev_tab, next_tab):
        """Record a single observed transition prev_tab -> next_tab (online)."""
        if prev_tab is None:
            # nothing to update
            # still push next_tab into history for future second-order updates
            self.history.append(next_tab)
            return
        self.first[prev_tab][next_tab] += 1
        # second-order: use last element in history as prev2 if available
        # history stores previous tabs in order of arrival
        if len(self.history) >= 1:
            prev2 = self.history[-1]
            # Only update second-order if prev2 and prev_tab are both valid and distinct
            if prev2 is not None:
                self.second[(prev2, prev_tab)][next_tab] += 1
        # push prev_tab to history for next calls
        self.history.append(prev_tab)

    def feed_sequence(self, seq, decay=0.995):
        """
        Warm-up: feed a long sequence (list) of tab ids.
        Applies exponential decay weights so recent transitions get larger weight.
        """
        if not seq or len(seq) < 2:
            # nothing to feed
            for t in seq:
                self.history.append(t)
            return

        n = len(seq)
        # weights: earliest small, latest large. We use decay^(n-1-i) so later have higher weight.
        weights = [decay ** (n - 1 - i) for i in range(n - 1)]
        # normalize so max weight = 1.0 (keeps counts in reasonable ranges)
        max_w = max(weights)
        if max_w > 0:
            weights = [w / max_w for w in weights]

        # apply weighted updates
        for i in range(n - 1):
            prev = seq[i]
            nxt = seq[i + 1]
            w = weights[i]
            # fractional counts
            self.first[prev][nxt] += w
            if i >= 1:
                prev2 = seq[i - 1]
                self.second[(prev2, prev)][nxt] += w
            # maintain history (append prev)
            self.history.append(prev)

        # append last element to history for future updates
        self.history.append(seq[-1])

    def predict_topk(self, prev_tab, prev_prev_tab=None, top_k=3, all_tabs=None):
        """
        Return up to top_k predictions ordered by combined score.
        Scoring: second-order matches weighted higher than first-order.
        If no history exists, fall back to global popularity or random sampling (if all_tabs provided).
        """
        scores = Counter()

        # second-order contribution (higher weight)
        if prev_prev_tab is not None:
            key = (prev_prev_tab, prev_tab)
            if key in self.second and self.second[key]:
                for t, c in self.second[key].items():
                    scores[t] += c * 2.0

        # first-order contribution
        if prev_tab in self.first and self.first[prev_tab]:
            for t, c in self.first[prev_tab].items():
                scores[t] += c * 1.0

        # fallback: if scores empty, use global popularity from first-order aggregated counts
        if not scores:
            global_counts = Counter()
            for prev, ctr in self.first.items():
                global_counts.update(ctr)
            if global_counts:
                return [t for t,_ in global_counts.most_common(top_k)]
            # else fallback to random sample from all_tabs
            if all_tabs:
                return random.sample(list(all_tabs), min(top_k, len(all_tabs)))
            return []

        return [t for t,_ in scores.most_common(top_k)]

    def sample_next(self, prev_tab, prev_prev_tab=None, all_tabs=None):
        """Sample a probabilistic next-tab from combined counts."""
        scores = Counter()
        if prev_prev_tab is not None:
            key = (prev_prev_tab, prev_tab)
            if key in self.second:
                scores.update(self.second[key])
        if prev_tab in self.first:
            scores.update(self.first[prev_tab])

        if not scores:
            if all_tabs:
                return random.choice(list(all_tabs))
            return None

        tabs, counts = zip(*scores.items())
        total = sum(counts)
        probs = [c / total for c in counts]
        return random.choices(tabs, weights=probs, k=1)[0]
