from pathlib import Path
import re,zipfile
r=Path.cwd()
for href in re.findall(r'\]\(([^)]+)\)',(r/'README.md').read_text(encoding='utf-8')):
 if not href.startswith(('#','http')): assert (r/href).exists(),href
allowed={'app.py','README.md','README.html','requirements.txt','requirements-docs.txt','build_report.py'}
folders={'simulator','tests','experiments','config','workloads','results','evidence','docs'}
files=[p for p in r.rglob('*') if p.is_file() and '__pycache__' not in p.parts and (p.parent==r and p.name in allowed or p.relative_to(r).parts[0] in folders) and 'superpowers' not in p.parts and not p.name.startswith('report-') and p.name not in ('presentation-updated.pptx','presentation-renamed.pptx')]
for p in files:
 if p.suffix in ('.py','.md','.html','.txt'):
  assert not re.search(r'ARM\s*305',p.read_text(encoding='utf-8-sig',errors='ignore'),re.I),p
zpath=r.parent/'Compute_Playground_Submission.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files:z.write(p,Path('Compute_Playground')/p.relative_to(r))
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 assert 'Compute_Playground/README.html' in z.namelist()
 print(f'Checked README file links and subject references. ZIP verified: {len(z.namelist())} files, {zpath.stat().st_size} bytes')
