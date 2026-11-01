# ARM305 Resource Lab

A deterministic local Python simulator for ARM 305. All servers, VMs and performance values are simulated. No cloud account required.

## Quick start (Python 3.10+)
From this directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```
If PowerShell blocks activation, use `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py` directly. On macOS/Linux activate with `source .venv/bin/activate`.

## Reproduce evidence without opening the UI
```text
python -m unittest discover -s tests -v
python -m experiments.run_experiments
```
Experiments overwrite generated synthetic evidence under results/, evidence/, config/ and workloads/. Run from this project directory. CSVs can be opened in a spreadsheet app. requirements-docs.txt is optional and needed only to regenerate report.pdf with `python build_report.py`.

## Demonstration
1. Start as tenant_a. Load 18 sample tasks. The loader advances through arrival times up to 100 ms; earlier tasks may already be complete.
2. Inspect your task table, node resource bars, and VM records. Advance 50 ms or run until complete.
3. Reset. Submit a custom high-sensitivity task with 2 CPU, 1 GB, 80 work. Edge processing is 40 ms and predicted response is 45 ms.
4. Stop its VM and show resource release. Reset before loading the sample again. IDs must be unique.
5. Load samples, switch to tenant_b, open Security demonstration, request T01. Access is denied. Try the Stop VM operation too.
6. Open Experiments to show policy comparison and overload. Regenerate to reproduce all saved outputs.
7. Change Edge capacity or network delay in the sidebar and reset before repeating a workload.

## Model and placement
CPU is a reserved abstract unit; RAM is GB. Work is CPU-ms at speed 1. Processing ms = work/(CPU*node speed). Predicted response ms = processing + total network delay. Resources release at processing finish; response time includes the additional network component. `completed` means compute completion. There is no queue, migration, contention slowdown, stochastic failure or real VM. Existing tasks retain reserved CPU.

Latency budgets: high 60 ms, medium 180 ms, low 600 ms. Both policies admit only capacity- and budget-feasible nodes. latency_first minimizes network delay. capacity_aware minimizes w*(response/budget)+(1-w)*max(projected CPU fraction,projected RAM fraction), with w=.8/.5/.2 for high/medium/low. Node name breaks ties. Rejection logs explain capacity and QoS checks for every node. At equal event times, completions release resources before arrivals. Workload order breaks simultaneous arrival ties. advance() takes an absolute time.

## Security boundary
The identity selector impersonates a demo tenant intentionally. This is an ownership-check demonstration, not authentication or an internet-ready service. Engine methods protect task lookup, tenant lists, VM lists and stopping. Returned rows are copies. Shared node utilization is public. Published experiment CSVs contain explicitly synthetic data for both tenants and are classroom evidence, not private multiuser storage. No passwords or sensitive data are used.

## Results
See results/summary.csv and results/charts/. Peak utilization uses event snapshots, not the idle final state. Response statistics cover completed tasks; rejection counts are reported alongside QoS compliance. Rejected and cancelled tasks have no successful response observation. p95 uses pandas linear quantile interpolation. Strict admission makes all accepted predictions meet the budget in this model.

## Submission contents
Source: simulator/, app.py. Tests: tests/. Inputs: config/, workloads/. Evidence: evidence/experiments.json, security.json, lifecycle.json, screenshots/, test_output.txt. Results: CSV tables and charts. Documentation: docs/report.pdf (7 pages), docs/presentation.pptx (6 slides), docs/architecture.png, docs/demo_script.md, docs/viva.md.

## Team details
Add your actual team names, roll numbers and truthful individual contributions before submission. See docs/team_details.md. This package makes no claim about contributions that have not been supplied.
