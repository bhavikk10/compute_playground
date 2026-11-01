import unittest
from streamlit.testing.v1 import AppTest
class UITests(unittest.TestCase):
 def test_sample_and_security(self):
  a=AppTest.from_file('app.py', default_timeout=15).run(); next(b for b in a.button if b.label=='Load 18 sample tasks').click().run(); self.assertFalse(a.exception); self.assertEqual(a.session_state.engine.clock,100)
  next(s for s in a.selectbox if s.label=='Demo identity').select('tenant_b').run(); next(b for b in a.button if b.label=='Attempt access as current tenant').click().run(); self.assertFalse(a.exception); self.assertIn('Access denied',a.error[0].value)
 def test_custom_and_collision(self):
  a=AppTest.from_file('app.py', default_timeout=15).run(); a.text_input[0].set_value('T01'); next(b for b in a.button if b.label=='Place task').click().run(); self.assertFalse(a.exception)
  self.assertEqual(len(a.session_state.engine.records('tenant_a')),1)
  next(b for b in a.button if b.label=='Load 18 sample tasks').click().run(); self.assertFalse(a.exception); self.assertTrue(a.warning)
 def test_queue_demo_explorer_and_completion(self):
  a=AppTest.from_file('app.py',default_timeout=15).run()
  next(b for b in a.button if b.label=='Load queue demonstration').click().run()
  self.assertFalse(a.exception);self.assertTrue(a.session_state.engine.queue_enabled)
  self.assertEqual(a.session_state.engine.get_task('tenant_a','wait-success')['status'],'queued')
  next(b for b in a.button if b.label=='Run until complete').click().run()
  self.assertFalse(a.exception)
  self.assertEqual(a.session_state.engine.get_task('tenant_a','wait-success')['status'],'completed')
  self.assertEqual(a.session_state.engine.get_task('tenant_a','urgent-expiry')['status'],'expired')
 def test_scheduled_seeded_workload(self):
  a=AppTest.from_file('app.py',default_timeout=15).run()
  next(b for b in a.button if b.label=='Schedule seeded workload').click().run()
  self.assertFalse(a.exception);self.assertTrue(a.session_state.pending)
  next(b for b in a.button if b.label=='Run until complete').click().run()
  self.assertFalse(a.exception);self.assertEqual(a.session_state.pending,[])
  self.assertEqual(sum(len(a.session_state.engine.records(t)) for t in ('tenant_a','tenant_b')),40)
 def test_mixed_sample_and_scheduled_arrivals(self):
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
 def test_friendly_submission_receipt(self):
  a=AppTest.from_file('app.py',default_timeout=15).run()
  self.assertEqual(a.tabs[0].label,'Submit task')
  next(t for t in a.text_input if t.label=='Task ID').set_value('my-own-task')
  next(b for b in a.button if b.label=='Place task').click().run()
  self.assertFalse(a.exception)
  self.assertTrue(any('my-own-task' in x.value and 'Edge' in x.value for x in a.success))
  self.assertTrue(any('45.00 ms' in x.value for x in a.info))
if __name__=='__main__': unittest.main()
