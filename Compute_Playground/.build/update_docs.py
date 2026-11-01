from pathlib import Path
p=Path('app.py');s=p.read_text();s=s.replace("waiting=(start if start is not None else min(e.clock,r['deadline_ms']))-r['arrival']", "waiting=(start-r['arrival']) if start is not None else ((e.clock-r['arrival']) if r['status']=='queued' else r['wait_ms'])");p.write_text(s)
p=Path('tests/test_ui.py');s=p.read_text().replace("if __name__=='__main__': unittest.main()",''' def test_queue_demo_explorer_and_completion(self):
  a=AppTest.from_file('app.py',default_timeout=15).run()
  next(b for b in a.button if b.label=='Load queue demonstration').click().run()
  self.assertFalse(a.exception);self.assertTrue(a.session_state.engine.queue_enabled)
  self.assertEqual(a.session_state.engine.get_task('tenant_a','wait-success')['status'],'queued')
  next(b for b in a.button if b.label=='Run until complete').click().run()
  self.assertFalse(a.exception)
  self.assertEqual(a.session_state.engine.get_task('tenant_a','wait-success')['status'],'completed')
  self.assertEqual(a.session_state.engine.get_task('tenant_a','urgent-expiry')['status'],'expired')
 def test_scheduled_seeded_workload(self):
  a=AppTest.from_file('app.py',default_timeout=15).run()
  next(b for b in a.button if b.label=='Schedule seeded workload').click().run()
  self.assertFalse(a.exception);self.assertTrue(a.session_state.pending)
  next(b for b in a.button if b.label=='Run until complete').click().run()
  self.assertFalse(a.exception);self.assertEqual(a.session_state.pending,[])
  self.assertEqual(sum(len(a.session_state.engine.records(t)) for t in ('tenant_a','tenant_b')),40)
if __name__=='__main__': unittest.main()''');p.write_text(s)
p=Path('README.md');s=p.read_text(encoding='utf-8')
s=s.replace('| Prepare the presentation and viva |', '| Try timelines, queues, seeded and energy experiments | [13. The bigger playground](#13-the-bigger-playground) |\n| Understand real-resource integration | [14. Could we plug in real computers?](#14-could-we-plug-in-real-computers) |\n| Prepare the presentation and viva |')
s=s.replace('      baseline.json','      baseline.json')
s=s.replace('    engine.py                  Tasks, policies, clock, VMs, ownership, accounting','    engine.py                  Tasks, three policies, queue, clock, VMs, energy, ownership\n    workloads.py               Repeatable workload generator using a private random seed')
s=s.replace('    run_experiments.py         Creates workloads, runs scenarios, saves evidence','    run_experiments.py         Original scenarios plus the extension experiments\n    extended_experiments.py    Queue comparison and ten paired seeds across three policies')
s=s.replace('    test_ui.py                 Two interface behaviour tests','    test_ui.py                 Four interface behaviour tests\n    test_extensions.py         Nine queue, deadline, energy and explorer checks')
s=s.replace('    summary.csv                One row per performance scenario','    summary.csv                Original five performance scenarios\n    seeded_runs.csv            Thirty paired seed/policy run records\n    seeded_summary.csv         Mean and sample SD across ten seeds\n    queue_comparison.csv       Same 14 tasks with queue off and on\n    seed7_<policy>_*.csv        Detailed seeded task, timeline and utilization traces\n    queue_<on/off>_*.csv        Detailed queue comparison traces')
s=s.replace('      utilization.png          Peak CPU/RAM use','      utilization.png          Peak CPU/RAM use\n      seeded_comparison.png    Acceptance, response and hypothetical energy across seeds')
s=s.replace('    experiments.json           Setup, expectation, outcome and evidence pointers','    experiments.json           Original setup, expectation, outcome and evidence pointers\n    extensions.json            Seeded/queue setup, assumptions and actual outcomes\n    *_decisions.json           Node evaluations saved for queue and seed-7 traces')
s=s.replace('Seven-page formal report','Eight-page formal report').replace('Six-slide presentation','Seven-slide presentation').replace('seven-page report','eight-page report').replace('six-slide presentation','seven-slide presentation')
s=s.replace('The first command checks the program. The second recreates the experiments.','The first command runs 22 tests. The second recreates the original and extended experiments.')
s=s.replace('across two tests.','across four tests. The extension suite adds nine checks for waiting, deadlines, energy, reproducibility and protected explorer data.')
s=s.replace('There is no waiting queue.','With the default queue setting off, there is no waiting queue. With it on, temporarily blocked but otherwise feasible work can wait; chapter 13 explains the rules.')
s=s.replace('processing_ms + network_delay_ms','wait_ms + processing_ms + network_delay_ms')
s=s.replace('Tasks have `running`, `completed`, `rejected` or `cancelled` status.','Tasks have `queued`, `running`, `completed`, `rejected`, `expired` or `cancelled` status.')
s=s.replace('Predicted response is `40 + 5 = 45 ms`.','Predicted response is `40 + 5 = 45 ms` with no wait.')
s=s.replace('The model intentionally omits real VMs, network traffic, queues, migrations, failures, contention slowdown and production authentication.','The model intentionally omits real VMs, network traffic, migrations, failures, contention slowdown and production authentication. Waiting queues and deadlines are now optional simulated features.')
s += '''

## 13. The bigger playground

### Watch the story happen

Press **Schedule seeded workload**, then **Play timeline**. The program delivers future job cards at their saved arrival times and advances 20 virtual ms each second. This is a visual playback speed, not a real hardware clock. **Pause timeline**, **Advance 50 ms** and **Run until complete** give manual control too. Reset clears scheduled work. Use **Timeline** to see only your tenant's jobs: grey hatch means waiting, blue means processing. The event table records arrivals, allocation, completion, rejection, expiry and cancellation. Export it with **Export my timeline**.

### The waiting bench

Imagine all helpers are busy. Instead of immediately sending every new job home, switch on **Queue temporarily blocked tasks**, then reset. A job waits only if some node could handle its CPU/RAM and response budget when empty. An impossibly large or intrinsically too-slow job is rejected straight away.

The deadline is arrival time plus its sensitivity budget. Waiting counts: `response = wait + processing + network`. At resource-release events, the queue tries earliest deadlines first, breaking ties by arrival then ID. All completions at a timestamp release capacity before queued jobs are evaluated. Other feasible jobs can pass a blocked job, so the queue does not intentionally idle a suitable node. This is a deterministic heuristic, not a promise of fair or optimal scheduling. A queued job gets no VM and reserves nothing until admission. It expires at its deadline if it has not started. You can also cancel your own queued job from the Timeline tab.

Press **Load queue demonstration** for a fresh queue-enabled world. Twelve low-sensitivity jobs fill the nodes. `wait-success` waits, starts on Cloud at 25 ms, and completes. `urgent-expiry` cannot meet its 60 ms response promise when suitable resources free up, so it expires. This button explicitly resets the world and enables its queue; the active queue status above the resource bars is authoritative. Sidebar settings apply again when you reset.

<details><summary>Does the queue mean a task can start at its deadline?</summary>

No. The response budget includes its waiting, processing and network delay. Merely finding a free CPU just before the deadline is insufficient. Queued tasks still pass the same end-to-end QoS test before starting.

</details>

### Ask the chooser why

Open **Decision explorer** and select one of your tasks. Every evaluation attempt preserves a separate node table: available CPU/RAM, capacity and QoS checks, waiting, projected utilization, score, hypothetical energy and the selected node. Earlier snapshots do not change when the node later gets busy. `decisions(tenant, task_id)` checks ownership, just like task lookup. The explorer and timeline never expose another tenant's task records.

### Different stories, reproducible endings

A **seed** is like the page number of a shuffled storybook: seed 7 gives the same ordered cards every time. [simulator/workloads.py](simulator/workloads.py) uses its own `random.Random(seed)` so unrelated random code cannot disturb it. Choose seed and task count in the sidebar, then schedule. Use another seed or reset before reusing its IDs.

The experiment runner compares **seeds 0–9**, each with **40 identical tasks for each of three policies**, always using fresh engines with queues on. [seeded_runs.csv](results/seeded_runs.csv) preserves all thirty runs. [seeded_summary.csv](results/seeded_summary.csv) reports per-run means and sample standard deviations across seeds. The plotted whiskers are sample SD, not confidence intervals. Also compare the same 14-task demonstration with queue on and off in [queue_comparison.csv](results/queue_comparison.csv).

### A pretend electricity meter

Each node has an illustrative incremental power coefficient: Edge **2**, Fog **6**, Cloud **18 watts per reserved CPU unit**. These are invented teaching parameters, not measured hardware data. Estimated compute energy is:

```text
energy_j = reserved_CPU × watts_per_CPU × elapsed_processing_ms / 1000
```

Waiting uses zero incremental compute energy in this deliberately limited model. Stopping a VM charges only the processing time already consumed. Idle power, network energy, RAM, cooling and boot costs are omitted. A task also stores its full predicted processing energy at allocation, separately from consumed energy.

The third policy, `energy_aware`, filters the same CPU/RAM/QoS constraints, then minimizes:

```text
energy_scale = largest full-task compute-energy estimate across the nodes
score = 0.5 × (response / budget) + 0.5 × (task_energy / energy_scale)
```

This balances the hypothetical energy estimate against response; it does not minimize total system electricity or guarantee the lowest measured joules. Report energy beside completed counts: doing less work can use fewer joules.

### What actually happened?

Across the ten paired seeds, average completed tasks out of 40 were **32.8 latency-first**, **33.5 capacity-aware**, and **32.9 energy-aware**. Average per-run response was **74.30**, **89.40**, and **72.48 ms**, respectively. Average modeled compute energy was **16.232**, **21.424**, and **16.456 J**. Energy-aware did not beat latency-first on total modeled energy, and their completed counts also differ. That is a result to explain, not hide.

In the 14-task queue comparison, queue-off completed **12** and rejected **2**. Queue-on completed **13**, rejected **0**, and expired **1**. More completed work increased modeled energy from **18.80 to 19.25 J**. See [extension evidence](evidence/extensions.json) for setup, expectation, actual outcomes and assumptions.

![Paired seeded comparison](results/charts/seeded_comparison.png)

## 14. Could we plug in real computers?

**Not directly.** Today a VM is a Python reservation record. Giving the application a real server address does not make that record launch real work. Think of the simulator as a toy workshop organiser: it knows how to choose a workshop, but it has no delivery truck or real tools attached.

A future **execution adapter** would be the delivery truck. The following interface is a proposed design, not working code in this submission:

| Adapter responsibility | What a real implementation must do |
|---|---|
| Discover resources | Obtain current node capacity, availability and health |
| Launch work | Map a supported task to a real process, container, VM or managed job |
| Track identity | Authenticate users and apply real resource permissions and quotas |
| Observe execution | Read actual job status, elapsed time, CPU/RAM and failures |
| Stop work | Stop the real job and confirm that its resources are released |
| Reconcile state | Recover after crashes and prevent simulated reservations drifting from reality |
| Handle credentials | Use an appropriate secret store instead of putting secrets in project files |

The placement rules, task data model and parts of the interface could be reused. The virtual-time engine, predicted work formula, VM records and demo identity selector would need adaptation or replacement. Real infrastructure would also introduce queues, provisioning delays, billing and failure modes outside the current model. No adapter, real cloud connection or hypervisor integration is implemented or claimed here.

[Back to the adventure menu](#choose-your-adventure)
'''
p.write_text(s,encoding='utf-8')
