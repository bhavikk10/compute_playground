from pathlib import Path
p=Path('build_report.py');s=p.read_text().replace("The baseline has 18 tasks over two tenants", "Original baseline and overload runs keep queues off. The baseline has 18 tasks over two tenants");p.write_text(s)
