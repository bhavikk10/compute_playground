import unittest
from streamlit.testing.v1 import AppTest
class UITests(unittest.TestCase):
 def test_sample_and_security(self):
  a=AppTest.from_file('app.py').run(); next(b for b in a.button if b.label=='Load 18 sample tasks').click().run(); self.assertFalse(a.exception); self.assertEqual(a.session_state.engine.clock,100)
  next(s for s in a.selectbox if s.label=='Demo identity').select('tenant_b').run(); next(b for b in a.button if b.label=='Attempt access as current tenant').click().run(); self.assertFalse(a.exception); self.assertIn('Access denied',a.error[0].value)
 def test_custom_and_collision(self):
  a=AppTest.from_file('app.py').run(); a.text_input[0].set_value('T01'); next(b for b in a.button if b.label=='Place task').click().run(); self.assertFalse(a.exception)
  self.assertEqual(len(a.session_state.engine.records('tenant_a')),1)
  next(b for b in a.button if b.label=='Load 18 sample tasks').click().run(); self.assertFalse(a.exception); self.assertTrue(a.warning)
if __name__=='__main__': unittest.main()
