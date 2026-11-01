# Implementation plan
Approved scope: deterministic Streamlit simulator and complete local submission package.
1. Test and implement Engine.submit, advance, stop, get_task, records and snapshot.
2. Use capacity and latency admission checks, stable ties, two scored policies.
3. Run baseline, overload, capacity, latency, security and lifecycle experiments from fresh state.
4. Build Streamlit UI and CSV exports without bypassing ownership checks.
5. Generate 7-page report, 6-slide presentation, architecture and recorded evidence.
6. Verify accounting, determinism, validation, policy comparisons, artifact counts and clean ZIP.
Review focus: invalid numeric inputs, duplicate IDs, backward time, unauthorized mutation, double release.
