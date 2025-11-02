import time

RESTORE_PENALTIES = {
    "active": 0.0,
    "compressed": 0.02,
    "disk": 0.10
}

class SuspendRestoreManager:
    VALID = ("active", "compressed", "disk")
    def __init__(self):
        self.tier_map = {}

    def set_tier(self, tab_id, tier):
        if tier not in self.VALID:
            raise ValueError("Invalid tier")
        self.tier_map[tab_id] = tier

    def get_tier(self, tab_id):
        return self.tier_map.get(tab_id, "disk")

    def simulate_restore_latency(self, tab_id):
        tier = self.get_tier(tab_id)
        penalty = RESTORE_PENALTIES.get(tier, RESTORE_PENALTIES["disk"])
        if penalty > 0:
            time.sleep(penalty)
        self.set_tier(tab_id, "active")
        return penalty

    def suspend_to_compressed(self, tab_id):
        self.set_tier(tab_id, "compressed")

    def suspend_to_disk(self, tab_id):
        self.set_tier(tab_id, "disk")
