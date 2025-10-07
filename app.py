# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from simulation import run_simulation  # Import the function directly

# Title
st.title("Browser Tab Memory Simulation")

# Sidebar inputs
st.sidebar.header("Simulation Parameters")
n_tabs = st.sidebar.slider("Number of Tabs", 1, 50, 12)
ticks = st.sidebar.slider("Simulation Ticks", 50, 1000, 200)
system_limit_mb = st.sidebar.slider("System Memory Limit (MB)", 500, 5000, 1000)
policy = st.sidebar.selectbox("Memory Management Policy", ["working_set", "lru", "random"])

# Run simulation
if st.button("Run Simulation"):
    with st.spinner("Running simulation... please wait"):
        # Redirect print output to capture summary
        import sys
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()

        # Run the simulation
        run_simulation(n_tabs, ticks, system_limit_mb, policy)

        # Reset stdout and get summary
        sys.stdout = old_stdout
        summary = buffer.getvalue()

        st.success("Simulation completed!")

        # Display summary
        st.subheader("Simulation Summary")
        st.text(summary)

        # Load and plot memory trace
        try:
            df = pd.read_csv("memory_trace.csv")
            st.subheader("Memory Usage Over Time")
            fig, ax = plt.subplots()
            ax.plot(df["tick"], df["mem_mb"], label="Memory Usage (MB)")
            ax.set_xlabel("Tick")
            ax.set_ylabel("Memory (MB)")
            ax.legend()
            st.pyplot(fig)
        except FileNotFoundError:
            st.error("memory_trace.csv not found. Please check the simulation output.")
else:
    st.info("Adjust parameters and click 'Run Simulation' to begin.")
