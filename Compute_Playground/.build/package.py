from pathlib import Path
import zipfile,re,json
from xml.etree import ElementTree as ET
r=Path.cwd()
for href in re.findall(r'\]\(([^)]+)\)',(r/'README.md').read_text(encoding='utf-8')):
 if not href.startswith(('#','http')):assert (r/href).exists(),href
folders={'simulator','tests','experiments','config','workloads','results','evidence','docs'}
allowed={'README.md','README.html','app.py','build_report.py','requirements.txt','requirements-docs.txt'}
files=[p for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts and (p.parent==r and p.name in allowed or p.relative_to(r).parts[0] in folders) and 'superpowers' not in p.parts and not p.name.startswith('report-') and p.name!='presentation-v2.pptx']
with zipfile.ZipFile(r/'docs/presentation.pptx') as z:
 slides=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)];assert len(slides)==7
 texts=' '.join(z.read(n).decode('utf-8') for n in slides);assert 'Energy assumptions' in texts
for p in files:
 if p.suffix in ('.py','.md','.html','.txt'):assert not re.search(r'ARM\s*305',p.read_text(encoding='utf-8-sig',errors='ignore'),re.I),p
out=r.parent/'Compute_Playground_Submission.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,Path('Compute_Playground')/p.relative_to(r))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for file in ['README.html','simulator/workloads.py','tests/test_extensions.py','experiments/extended_experiments.py','results/seeded_runs.csv','evidence/extensions.json','docs/report.pdf','docs/presentation.pptx']:assert 'Compute_Playground/'+file in z.namelist()
 z.extractall(r/'.build/extraction_check')
print(f'ZIP verified: {len(files)} files, {out.stat().st_size} bytes. Seven-slide deck and README file links checked.')
