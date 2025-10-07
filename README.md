# Browser-tab-simulation
OS Project – Working Set Model for Browser Tabs

Operating System
C2P2 Project

Working Set Model for Browser Tab Simulation
Title: Dynamic Memory Management for Multi-Tab Browser Environments with Predictive Tab Restoration

Problem Statement: Modern web browsers manage dozens of tabs with varying memory requirements and access patterns. Efficient memory management using working set principles can optimize tab suspension/restoration while maintaining user experience, but requires sophisticated prediction and caching strategies.

Phase 1: Implement per-tab working set tracking with memory usage monitoring and basic tab suspension/restoration mechanisms. Create realistic web browsing simulators with different tab usage patterns and measure memory footprint, restoration latency, and user experience impact under memory pressure.

Phase 2: Develop predictive models for tab access probability and implement intelligent prefetching mechanisms anticipating tab switches. Create advanced caching strategies optimizing tab restoration speed and memory utilization while considering user behaviour patterns and system constraints. 

Implementation: 
Browser -> windows -> tabs 
each window can have dozens of tabs 
Tabs use memory(RAM) -> comp has limited RAM -> browser suspends tabs u r not using and restores them when u click again 
If not done – too much RAM used -> system slow down & if wrong tab suspended -> u click it -> delay in opening 

Project – simulate tab suspension & restoration using Working set model (OS memory management concept) 

Working set model : set of memory pages that a process has accessed recently 

Phase 1: 
Py sim requirements: 
1.	Track memory usage of each tab 
i.	Each tab has: 
a.	Base memory (min reqd) 
b.	Extra memory (changes with user interaction) 
c.	Working set (pages used recently)
2.	Decide when to suspend a tab 
i.	If mem is full
ii.	Suspension frees mem (closing temporarily) 
iii.	Policies to try 
a.	No suspension (bad baseline) 
b.	LRU( Least Recently Used tabs suspended first) 
c.	Working Set (tab with smallest/oldest working set suspended first) 
3.	Restore suspended tab when user clicks it 
i.	When user reopens tab: 
a.	Snapshot saved -> fast restore 
b.	No snapshot -> full reload -> slow
ii.	Latency measure (time taken to restore) 

Outputs we need: 
1.	Memory footprint(ram used overtime) 
2.	Restoration latency(time taken to restore suspended tabs) 
3.	Number of suspensions/restorations
4.	Comparison bw policies
5.	Visual of graphs 
a.	Memory usage vs time 
b.	Latency distribution 
c.	Suspension count per policy
<br>
Work Distribution:
<br>
ADITYA: <br>
Tab + Memory Model<br>
•	Implement the Tab class/object with:<br>
o	Base memory<br>
o	Extra memory (grows/shrinks with activity)<br>
o	Working set (recently used pages)<br>
•	Add functions to simulate browsing activity (e.g., open/close pages, add/remove from working set).<br>
•	Provide APIs like getMemoryUsage(), updateWorkingSet().<br>
👉 Deliverable: A working simulator of individual tab memory behavior.<br>
<br>
SHRETA: <br>
Memory Manager + Suspension Policies<br>
•	Implement global Memory Manager that monitors all tabs.
•	Write suspension decision logic:
o	Baseline: no suspension.
o	LRU: track access order, suspend least recently used.
o	Working Set: suspend tab with smallest/oldest working set.
•	Handle memory pressure (e.g., when total usage > system limit, trigger suspension).
👉 Deliverable: A module that can decide which tab to suspend under different policies.
<br>
SAVANI: 
Suspension & Restoration Logic
•	Implement suspend() for tabs (save state, free memory).
•	Implement restore():
o	With snapshot: fast restore (low latency).
o	Without snapshot: full reload (high latency).
•	Add latency simulation (e.g., sleep or timer to show difference).
👉 Deliverable: Reliable suspend/restore system with measurable latency.
<br>
Saloni: 
Simulation + Metrics + Testing
•	Build simulation scenarios:
o	Open 10–20 tabs with different usage patterns (e.g., video tab, static news tab, shopping tab with interactions).
o	Random user clicks to switch tabs.
•	Collect metrics:
o	Total memory footprint.
o	Number of suspensions/restorations.
o	Latency values (avg, max).
•	Test with each policy (Baseline vs LRU vs Working Set).
👉 Deliverable: Simulation driver + results collection.
<br>
Workflow Structure: 
/browser_simulation
│
├── tab.py                                     # ADITYA → Tab + Memory Model
├── memory_manager.py                          # SHRETA → Policies + Global Memory Manager
├── suspend_restore.py                         # SAVANI → Suspend + Restore + Latency
├── simulation.py                              # SALONI → Main driver + scenarios + metrics
└── README.md                                  # For explanation (everyone adds here)

# Contributor
SALONI BHIMELLU
SHRETA DAS
ADITYA PATIL
SAVANI BHIMELLU


