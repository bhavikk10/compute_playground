from pathlib import Path
p=Path('README.md');s=p.read_text(encoding='utf-8').replace('Six interface behaviour tests','Seven interface behaviour tests').replace('across six tests.','across seven tests.').replace('runs 24 tests','runs 25 tests')
s=s.replace('## 4. Your first job\n','''## 4. Your first job

**Yes, you can add your own tasks.** The first app tab is **Submit task**. Enter any unique task name and your own CPU, RAM, sensitivity and work values. Each submission belongs to the selected tenant. You can add multiple tasks; the engine decides whether to allocate, queue or reject each one based on the current state.

The app now includes a **Start here** walkthrough, question-mark help beside the inputs, friendly rule names and a submission receipt showing the selected server and response calculation. The task table shows the most useful columns first, with full technical fields in an expander. Generated-workload settings and Edge server settings are expandable sidebar sections. Pending rule/server changes show a warning until reset.

''')
s=s.replace('across seven tests. The extension suite','across seven tests, including the custom-submission receipt. The extension suite')
p.write_text(s,encoding='utf-8')
p=Path('build_report.py');s=p.read_text().replace('Twenty-four automated tests','Twenty-five automated tests');p.write_text(s)
p=Path('.build/browser.mjs');s=p.read_text().replace("name:'tenant_b',exact:true","name:'Tenant B',exact:true");p.write_text(s)
