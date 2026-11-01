from pathlib import Path
r=Path.cwd()
for name in ['app.py','build_report.py','.build/slides.mjs']:
 p=r/name;s=p.read_text();s=s.replace('ARM305 Resource Lab','Compute Playground').replace('ARM 305 | Edge, Fog and Cloud Resource Simulator','Compute Playground | CDEF Computing').replace('ARM 305 / RESOURCE LAB','CDEF COMPUTING / COMPUTE PLAYGROUND').replace('ARM 305','CDEF Computing').replace("'Edge, Fog and Cloud\\nResource Simulator'","'Compute Playground\\nEdge, Fog and Cloud'")
 if name=='app.py': s=s.replace("st.title('Compute Playground')","st.title('Compute Playground')\nst.caption('CDEF Computing · Learn by placing tasks on Edge, Fog and Cloud')")
 p.write_text(s,encoding='utf-8')
