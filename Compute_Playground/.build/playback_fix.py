from pathlib import Path
p=Path('app.py');s=p.read_text().replace('import json','import json\nimport time',1)
s=s.replace("st.session_state.setdefault('playing',False)","st.session_state.setdefault('playing',False)\nst.session_state.setdefault('last_frame_wall',time.monotonic())")
s=s.replace("    if st.session_state.playing:\n        if not", "    if st.session_state.playing and time.monotonic()-st.session_state.last_frame_wall>=.85:\n        st.session_state.last_frame_wall=time.monotonic()\n        if not")
s=s.replace("    st.session_state.playing=not st.session_state.playing;st.rerun()","    st.session_state.playing=not st.session_state.playing;st.session_state.last_frame_wall=time.monotonic();st.rerun()")
p.write_text(s)
p=Path('README.md');s=p.read_text(encoding='utf-8').replace('six-slide summary','seven-slide summary').replace('First, both policies ask','First, all three policies ask');p.write_text(s,encoding='utf-8')
