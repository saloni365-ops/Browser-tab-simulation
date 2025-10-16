# Browser-tab-simulation

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-%20-orange?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![pandas](https://img.shields.io/badge/pandas-%20-lightblue?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![matplotlib](https://img.shields.io/badge/matplotlib-%20-orange?logo=matplotlib&logoColor=white)](https://matplotlib.org/)
[![pytest](https://img.shields.io/badge/pytest-%20-blue?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](./LICENSE)

OS Project – Working Set Model for Browser Tabs

Operating System · C2P2 Project

## Overview

Working Set Model for Browser Tab Simulation

**Title:** Dynamic Memory Management for Multi-Tab Browser Environments with Predictive Tab Restoration

Modern web browsers manage dozens of tabs with varying memory requirements and access patterns. Efficient memory management using working set principles can optimize tab suspension/restoration while maintaining user experience, but requires sophisticated prediction and caching strategies.

## Project Phases

### Phase 1
- Implement per-tab working set tracking with memory usage monitoring and basic tab suspension/restoration mechanisms.
- Create realistic web browsing simulators with different tab usage patterns and measure memory footprint, restoration latency, and user experience impact under memory pressure.

### Phase 2
- Develop predictive models for tab access probability and implement intelligent prefetching mechanisms anticipating tab switches.
- Create advanced caching strategies optimizing tab restoration speed and memory utilization while considering user behaviour patterns and system constraints.

## Implementation (concept)

- Browser -> windows -> tabs
- Each window can have dozens of tabs
- Tabs use memory (RAM); the computer has limited RAM so the browser suspends tabs you're not using and restores them when you click again.
- If not done properly, too many active tabs can slow the system; suspending the wrong tabs can cause delays when the user switches back.

Project – simulate tab suspension & restoration using the working set model (an OS memory management concept).

Working set model: the set of memory pages a process has accessed recently.

## Phase 1 – Requirements (Python simulator)

1. Track memory usage of each tab
   - Each tab has:
     - Base memory (minimum required)
     - Extra memory (changes with user interaction)
     - Working set (pages used recently)
2. Decide when to suspend a tab
   - If memory is full
   - Suspension frees memory (temporarily)
   - Policies to try:
     - No suspension (baseline)
     - LRU (Least Recently Used)
     - Working Set (suspend tab with smallest/oldest working set)
3. Restore suspended tab when user clicks it
   - With snapshot: fast restore
   - Without snapshot: full reload (slower)
   - Measure latency for restores

## Outputs

1. Memory footprint (RAM used over time)
2. Restoration latency (time taken to restore suspended tabs)
3. Number of suspensions/restorations
4. Comparison between policies
5. Visuals:
   - Memory usage vs time
   - Latency distribution
   - Suspension count per policy

## Work Distribution

### Aditya
- Tab & Memory Model
  - Implement the `Tab` class/object with base memory, extra memory, and a working set
  - Add functions to simulate browsing activity and provide APIs like `get_memory_usage()` and `update_working_set()`

### Shreta
- Memory Manager & Suspension Policies
  - Implement a global Memory Manager that monitors all tabs
  - Implement suspension decision logic for Baseline, LRU and Working Set
  - Handle memory pressure and triggers

### Savani
- Suspension & Restoration Logic
  - Implement `suspend()` for tabs (save state, free memory)
  - Implement `restore()` with snapshot/no-snapshot behavior and simulated latency

### Saloni
- Simulation, Metrics & Testing
  - Build simulation scenarios (10–20 tabs with varied patterns)
  - Collect metrics (total memory, suspensions/restorations, latency)
  - Run tests comparing policies

## Project Structure

/browser_simulation
│
├── `tab.py`             # Tab & Memory Model
├── `memory_manager.py`  # Policies & Global Memory Manager
├── `suspend_restore.py` # Suspend & Restore + Latency
├── `simulation.py`      # Main driver + scenarios + metrics
└── `README.md`          # Project documentation

## Contributors

- Saloni Bhimellu
- Shreta Das
- Aditya Patil
- Savani Bhimellu

