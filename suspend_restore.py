# suspend_restore.py
"""
Helpers to centralize suspend/restore timing and optional sleeping.
This keeps sleep/time simulation in one place.
"""

import time
from tab import Tab

def suspend_tab(tab: Tab, save_snapshot: bool = True, simulate_sleep: bool = False) -> float:
    """
    Suspend tab and return simulated snapshot write latency (seconds).
    If simulate_sleep is True, actually sleep for that duration.
    """
    snapshot_size_mb = tab.create_snapshot() if save_snapshot else 0
    # simple model: snapshot write = snapshot_size / 1000 + fixed overhead
    latency = 0.02 + (snapshot_size_mb / 1000.0)
    tab.suspend(save_snapshot=False)  # state change: save_snapshot already handled
    if simulate_sleep and latency > 0:
        time.sleep(latency)
    return latency

def restore_tab(tab: Tab, use_snapshot: bool = True, simulate_sleep: bool = False) -> float:
    """
    Restore tab and return latency. Optionally sleep to simulate real time.
    """
    latency = tab.restore(use_snapshot=use_snapshot)
    if simulate_sleep and latency > 0:
        time.sleep(latency)
    return latency
