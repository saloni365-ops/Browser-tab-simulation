# memory_manager.py
from typing import Dict, List, Optional
from tab import Tab
import suspend_restore

class MemoryManager:
    def __init__(self, system_limit_mb: int = 4096):
        self.tabs: Dict[str, Tab] = {}
        self.system_limit_mb = system_limit_mb

    def add_tab(self, tab: Tab):
        self.tabs[tab.tab_id] = tab

    def total_memory_usage(self) -> int:
        return sum(t.get_memory_usage_mb() for t in self.tabs.values())

    def enforce_policy(self, policy: str = 'working_set', protect_tab_id: Optional[str] = None, simulate_sleep: bool = False) -> List[str]:
        suspended = []
        if policy == 'none':
            return suspended

        # Keep suspending until memory under limit or no candidates left
        while self.total_memory_usage() > self.system_limit_mb:
            candidate = None
            if policy == 'lru':
                oldest_ts = None
                for t in self.tabs.values():
                    if t.is_suspended or t.tab_id == protect_tab_id:
                        continue
                    # estimate last access time: from working set last item
                    if t.working_set:
                        last_pid = t.working_set[-1]
                        last_ts = t.last_access.get(last_pid, 0)
                    else:
                        last_ts = 0
                    if oldest_ts is None or last_ts < oldest_ts:
                        oldest_ts = last_ts
                        candidate = t
            elif policy == 'working_set':
                min_ws = None
                for t in self.tabs.values():
                    if t.is_suspended or t.tab_id == protect_tab_id:
                        continue
                    ws = t.working_set_size_pages()
                    if min_ws is None or ws < min_ws:
                        min_ws = ws
                        candidate = t

            if not candidate:
                break
            # Use suspend_restore to suspend (so snapshot latency computed here)
            suspend_restore.suspend_tab(candidate, save_snapshot=True, simulate_sleep=simulate_sleep)
            suspended.append(candidate.tab_id)
        return suspended
