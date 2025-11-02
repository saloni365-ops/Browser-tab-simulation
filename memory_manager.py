from collections import OrderedDict
import time
from suspend_restore import SuspendRestoreManager

class MemoryManager:
    COMPRESSION_RATIO = 0.5
    COMPRESSED_OVERHEAD_MB = 5.0

    def __init__(self, tab_sizes=None, memory_limit_mb=1200):
        self.tab_sizes = dict(tab_sizes) if tab_sizes else {}
        self.memory_limit = memory_limit_mb
        self.active = OrderedDict()
        self.compressed = set()
        self.disk = set(self.tab_sizes.keys())
        self.sr = SuspendRestoreManager()
        for t in self.tab_sizes:
            self.sr.set_tier(t, "disk")
        self.total_active_mem = 0.0
        self.total_compressed_mem = 0.0

    def get_tab_size(self, tab_id, tier):
        base = self.tab_sizes.get(tab_id, 100)
        if tier == "active":
            return base
        if tier == "compressed":
            return base * self.COMPRESSION_RATIO + self.COMPRESSED_OVERHEAD_MB
        return 0.0

    def ensure_memory_within_limit(self):
        while (self.total_active_mem + self.total_compressed_mem) > self.memory_limit:
            if not self.active:
                break
            lru_tab, info = next(iter(self.active.items()))
            self._compress_tab(lru_tab)

    def _compress_tab(self, tab_id):
        if tab_id not in self.active:
            return
        info = self.active.pop(tab_id)
        size_active = info['size']
        size_comp = self.get_tab_size(tab_id, "compressed")
        self.total_active_mem -= size_active
        self.compressed.add(tab_id)
        self.total_compressed_mem += size_comp
        self.sr.suspend_to_compressed(tab_id)

    def access_tab(self, tab_id, cur_time=None):
        if cur_time is None:
            cur_time = time.time()
        tier = self.sr.get_tier(tab_id)
        prefetch_hit = tier in ("active", "compressed")
        latency = self.sr.simulate_restore_latency(tab_id)
        if tab_id in self.active:
            self.active.move_to_end(tab_id)
            self.active[tab_id]['last_access'] = cur_time
            return latency, prefetch_hit
        if tab_id in self.compressed:
            size_comp = self.get_tab_size(tab_id, "compressed")
            self.compressed.remove(tab_id)
            self.total_compressed_mem -= size_comp
        elif tab_id in self.disk:
            self.disk.remove(tab_id)
        size_active = self.get_tab_size(tab_id, "active")
        self.active[tab_id] = {'size': size_active, 'last_access': cur_time}
        self.total_active_mem += size_active
        self.ensure_memory_within_limit()
        return latency, prefetch_hit

    def prefetch(self, predicted_tabs):
        """
        predicted_tabs: list of tab_ids (or list of tuples (tab_id,prob))
        Bring disk->compressed for predicted tabs
        """
        for entry in predicted_tabs:
            tab_id = entry[0] if isinstance(entry, tuple) else entry
            tier = self.sr.get_tier(tab_id)
            if tier == "disk":
                if tab_id in self.disk:
                    self.disk.remove(tab_id)
                if tab_id not in self.compressed:
                    self.compressed.add(tab_id)
                    self.total_compressed_mem += self.get_tab_size(tab_id, "compressed")
                    self.sr.suspend_to_compressed(tab_id)
                self.ensure_memory_within_limit()

    def current_memory_usage(self):
        return {
            'active_mb': self.total_active_mem,
            'compressed_mb': self.total_compressed_mem,
            'disk_count': len(self.disk),
            'active_count': len(self.active),
            'compressed_count': len(self.compressed)
        }
