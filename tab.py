# tab.py
"""
Tab class for Browser Tab Simulation (ADITYA)
- Tracks base + extra memory
- Maintains working set (recent page ids) + last access timestamps
- Provides APIs used by MemoryManager / suspend_restore modules
"""

import time
import random
from collections import deque
from typing import Deque, Dict, List, Optional

DEFAULT_PAGE_SIZE_MB = 4
DEFAULT_WS_CAPACITY = 50

class Tab:
    def __init__(self,
                 tab_id: str,
                 base_memory_mb: int = 50,
                 extra_memory_mb: int = 0,
                 page_size_mb: int = DEFAULT_PAGE_SIZE_MB,
                 ws_capacity: int = DEFAULT_WS_CAPACITY):
        self.tab_id = tab_id
        self.base_memory_mb = base_memory_mb
        self.extra_memory_mb = extra_memory_mb
        self.page_size_mb = page_size_mb

        # working set: deque of page_ids (most-recent at right)
        self.working_set: Deque[int] = deque(maxlen=ws_capacity)
        # last access timestamps for pages
        self.last_access: Dict[int, float] = {}

        self.is_suspended = False
        self.has_snapshot = False
        self.snapshot_size_mb: Optional[int] = None
        self.suspended_at: Optional[float] = None

        # metrics
        self.suspend_count = 0
        self.restore_count = 0
        self.total_time_suspended = 0.0

    # --- memory / working-set APIs ---
    def get_memory_usage_mb(self) -> int:
        return 0 if self.is_suspended else (self.base_memory_mb + self.extra_memory_mb)

    def update_working_set(self, page_id: int):
        ts = time.time()
        if page_id in self.last_access:
            # remove previous occurrence from deque (if present)
            try:
                self.working_set.remove(page_id)
            except ValueError:
                pass
        self.working_set.append(page_id)
        self.last_access[page_id] = ts

    def get_working_set_pages(self) -> List[int]:
        return list(self.working_set)

    def working_set_size_pages(self) -> int:
        return len(self.working_set)

    def working_set_age_oldest(self) -> Optional[float]:
        if not self.working_set:
            return None
        oldest_pid = self.working_set[0]
        return time.time() - self.last_access.get(oldest_pid, time.time())

    # --- simulate activity ---
    def access_page(self, page_id: Optional[int] = None):
        if page_id is None:
            page_id = random.randint(1, 2000)
        if self.is_suspended:
            raise RuntimeError(f"Tab {self.tab_id} is suspended.")
        self.update_working_set(page_id)
        # simulate extra memory change
        delta = random.randint(-5, 10)
        self.extra_memory_mb = max(0, self.extra_memory_mb + delta)

    def simulate_activity(self, intensity: str = "normal"):
        if self.is_suspended:
            return
        repeats = 1
        if intensity == "low":
            repeats = 1
        elif intensity == "high":
            repeats = random.randint(3, 6)
        else:
            repeats = random.randint(1, 3)
        for _ in range(repeats):
            self.access_page()

    # --- suspend / restore state changes (no sleeping here) ---
    def create_snapshot(self) -> int:
        ws_pages = self.working_set_size_pages()
        size_mb = int(ws_pages * self.page_size_mb * 0.6) + 5
        self.has_snapshot = True
        self.snapshot_size_mb = size_mb
        return size_mb

    def suspend(self, save_snapshot: bool = True):
        if self.is_suspended:
            return
        if save_snapshot:
            self.create_snapshot()
        self.is_suspended = True
        self.suspended_at = time.time()
        self.suspend_count += 1

    def restore(self, use_snapshot: bool = True) -> float:
        if not self.is_suspended:
            return 0.0
        if use_snapshot and self.has_snapshot:
            latency = 0.05 + (self.snapshot_size_mb or 0) / 1000.0
        else:
            latency = 0.5 + (self.base_memory_mb + self.extra_memory_mb) / 1000.0
        self.is_suspended = False
        self.restore_count += 1
        if self.suspended_at:
            self.total_time_suspended += time.time() - self.suspended_at
        self.suspended_at = None
        return latency

    def __repr__(self):
        state = "SUSPENDED" if self.is_suspended else "ACTIVE"
        return (f"<Tab {self.tab_id} | {state} | mem={self.get_memory_usage_mb()}MB | "
                f"ws={self.working_set_size_pages()}>")
