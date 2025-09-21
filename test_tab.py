# test_tab.py
from tab import Tab

def test_suspend_restore_basic():
    t = Tab("t1", base_memory_mb=50, extra_memory_mb=10)
    t.access_page(1)
    assert not t.is_suspended
    t.suspend(save_snapshot=True)
    assert t.is_suspended
    latency = t.restore(use_snapshot=True)
    assert not t.is_suspended
    assert latency >= 0.0
