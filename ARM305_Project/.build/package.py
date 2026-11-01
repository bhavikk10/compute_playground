from pathlib import Path
import zipfile, json
root=Path.cwd(); dest=root.parent/'ARM305_Submission.zip'
allow={'app.py','README.md','requirements.txt','requirements-docs.txt','build_report.py'}
folders={'simulator','tests','experiments','config','workloads','results','evidence','docs'}
files=[p for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and (p.name in allow and p.parent==root or p.relative_to(root).parts[0] in folders) and not p.name.startswith('report-') and 'superpowers' not in p.parts]
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for p in files: z.write(p,Path('ARM305_Project')/p.relative_to(root))
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 required=['README.md','requirements.txt','app.py','docs/report.pdf','docs/presentation.pptx','docs/architecture.png','results/summary.csv','evidence/security.json','evidence/test_output.txt','evidence/screenshots/security.png']
 for p in required: assert 'ARM305_Project/'+p in z.namelist(),p
 print(f'ZIP verified: {len(z.namelist())} files, {dest.stat().st_size} bytes')
