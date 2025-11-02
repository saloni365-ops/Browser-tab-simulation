import streamlit as st
import pandas as pd
import time
from simulation import run_simulation

st.set_page_config(page_title="Browser Tab Simulation Dashboard", layout="wide")
st.title("Browser Tab Simulation — Phase 2")
st.write("Working Set Model with Predictive Tab Restoration (High-accuracy mode)")

st.sidebar.header("Simulation Controls")
num_tabs = st.sidebar.slider("Number of Tabs", 20, 50, 30)
num_steps = st.sidebar.slider("Total Steps (warmup + test)", 200, 2000, 1000)
hotspot_size = st.sidebar.slider("Hotspot size (active tabs)", 2, 10, 5)
memory_limit = st.sidebar.slider("Memory limit (MB)", 500, 5000, 1200)
run = st.sidebar.button("Run Simulation (High-accuracy)") 

if run:
    st.info("Running simulation (this will pretrain the predictor and measure accuracy)...")
    progress = st.progress(0)
    # run simulation (pretraining inside the function)
    summary = run_simulation(num_tabs=num_tabs, steps=num_steps, memory_limit_mb=memory_limit, hotspot_size=hotspot_size, warmup_frac=0.6, log_csv='metrics.csv', show_terminal_output=False)
    for i in range(100):
        time.sleep(0.003)
        progress.progress(i+1)
    st.success("Simulation complete")

    st.header("📊 Summary Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg latency (ms)", f"{summary['avg_latency_ms']:.2f}")
    col2.metric("Top-1 Accuracy", f"{summary['prediction_accuracy_top1']*100:.2f}%")
    col3.metric("Top-3 Accuracy", f"{summary['prediction_accuracy_top3']*100:.2f}%")

    st.write("Prefetch hit rate:", f"{summary['prefetch_hit_rate']*100:.2f}%")
    st.write("Total accesses (test period):", summary['total_accesses'])

    st.write("---")
    st.subheader("Hotspot tabs (active set)")
    st.write(", ".join(summary['hotspot']))

    st.subheader("Tab sizes (MB)")
    ts = pd.DataFrame(list(summary['tab_sizes'].items()), columns=['Tab', 'Size_MB']).set_index('Tab')
    st.bar_chart(ts)

    st.write("---")
    st.write("Detailed per-step metrics were saved to metrics.csv (in project folder).")
else:
    st.info("Configure simulation parameters in the sidebar and click Run Simulation.")
