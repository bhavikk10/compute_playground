# Compute Playground extensions: approved implementation plan

Scope: virtual timeline, protected decision explorer, optional deadline queue, seeded workloads and illustrative compute energy comparisons. Keep legacy baseline admission mode and reports reproducible. No real execution adapter is implemented.

1. Add tests for queued admission/release, deadlines, waiting-inclusive response, simultaneous events, stop dispatch, protected decisions/timeline, energy accounting and seeded reproducibility.
2. Extend Engine with optional queue, structured node evaluations, event log and incremental compute energy. Preserve current public methods and default queue=False. Deadline = arrival + sensitivity budget; FIFO tie-break within earliest deadline. Complete events first, then queue admission, then expiration at equal timestamps. Queue only statically feasible tasks. No VM until allocation. Predicted response includes waiting. Energy = allocated CPU x illustrative watts/CPU x elapsed processing seconds; no idle/network energy.
3. Add seeded_workload(seed,count) using a private random.Random instance, deterministic ordering and varied arrival times. Add 10 paired seeds x 3 policies under identical queue settings, plus queue/no-queue comparison and trace exports.
4. Add Streamlit timeline, owned decision explorer, queued demo, workload seed controls and energy policy. Keep identity protection and existing tests.
5. Refresh README/interactive edition, 7-8 page report, 7-slide deck, demo/viva, all evidence and ZIP. Explicitly explain that actual hardware requires a separate execution adapter.
6. Run engine/UI regression, paired experiments, report/deck checks, browser smoke and extraction tests. Independently review final engine.

Review focus: equal-time release and expiry; repeated release; queued VM absence; unauthorized decisions; energy after stop; no retrospective event mutation; permanently impossible work never waits forever.
