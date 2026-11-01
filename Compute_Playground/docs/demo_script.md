# Five-minute demonstration: Compute Playground / CDEF Computing
0:00 Explain the three simulated nodes and units. Reset with latency_first and queue off.
0:25 Submit 2 CPU, 1 GB, high sensitivity, 80 work. Show 40 ms compute + 5 ms network, then stop its VM and show resource release.
1:00 Load queue demonstration (fresh queue-enabled world). Show wait-success and urgent-expiry in Timeline. Play or advance 50 ms; explain waiting-inclusive response and why an urgent task can expire.
1:45 Open Decision explorer. Inspect the saved capacity, QoS, score and energy values for wait-success before/after resource release.
2:15 Reset. Choose seed 7 and 40 tasks, schedule workload, play timeline, then run until complete. Explain reproducibility.
2:50 Load baseline samples after reset. Switch to tenant_b and request T01 in Security demonstration. Show view/stop denial.
3:20 Open Experiments: original policy/capacity/latency comparisons, queue comparison, ten paired seeds and the energy chart.
4:15 Explain that watts are hypothetical incremental coefficients, all hardware is simulated, and real execution requires an unimplemented adapter.
4:45 State actual team contributions and invite questions.
