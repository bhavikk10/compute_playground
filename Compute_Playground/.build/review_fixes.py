from pathlib import Path
p=Path('app.py');s=p.read_text();s=s.replace("ids={r['id'] for t in ('tenant_a','tenant_b') for r in e.records(t)}\n    if ids.intersection", "ids={r['id'] for t in ('tenant_a','tenant_b') for r in e.records(t)}|{t.id for t in st.session_state.pending}\n    if ids.intersection")
s=s.replace("        for t in workload(): e.submit(Task(t.id,t.tenant,t.cpu,t.ram,t.sensitivity,t.work,offset+t.arrival))\n        st.session_state.loaded=True; st.rerun()", "        st.session_state.pending.extend(Task(t.id,t.tenant,t.cpu,t.ram,t.sensitivity,t.work,offset+t.arrival) for t in workload())\n        st.session_state.pending.sort(key=lambda t:t.arrival)\n        tick(offset+100)\n        st.session_state.loaded=True; st.rerun()")
s=s.replace("            result=e.submit(Task(id,tenant,cpu,ram,sensitivity,work,e.clock))", "            if id in {t.id for t in st.session_state.pending}:raise ValueError('Task ID is reserved by a scheduled task')\n            result=e.submit(Task(id,tenant,cpu,ram,sensitivity,work,e.clock))")
p.write_text(s)
p=Path('tests/test_ui.py');s=p.read_text().replace("if __name__=='__main__': unittest.main()",''' def test_mixed_sample_and_scheduled_arrivals(self):
  a=AppTest.from_file('app.py',default_timeout=15).run()
  next(b for b in a.button if b.label=='Schedule seeded workload').click().run()
  next(b for b in a.button if b.label=='Load 18 sample tasks').click().run()
  next(b for b in a.button if b.label=='Run until complete').click().run()
  self.assertFalse(a.exception)
  self.assertEqual(sum(len(a.session_state.engine.records(t)) for t in ('tenant_a','tenant_b')),58)
 def test_pending_id_is_reserved(self):
  a=AppTest.from_file('app.py',default_timeout=15).run()
  next(b for b in a.button if b.label=='Schedule seeded workload').click().run()
  reserved=a.session_state.pending[0].id
  next(t for t in a.text_input if t.label=='Task ID').set_value(reserved)
  next(b for b in a.button if b.label=='Place task').click().run()
  self.assertFalse(a.exception);self.assertIn('reserved',a.error[0].value)
  next(b for b in a.button if b.label=='Run until complete').click().run();self.assertFalse(a.exception)
if __name__=='__main__': unittest.main()''');p.write_text(s)
p=Path('README.md');s=p.read_text(encoding='utf-8').replace('Four interface behaviour tests','Six interface behaviour tests').replace('across four tests.','across six tests.').replace('runs 22 tests','runs 24 tests');p.write_text(s,encoding='utf-8')
