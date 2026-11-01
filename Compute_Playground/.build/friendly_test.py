from pathlib import Path
p=Path('tests/test_ui.py');s=p.read_text().replace("if __name__=='__main__': unittest.main()",''' def test_friendly_submission_receipt(self):
  a=AppTest.from_file('app.py',default_timeout=15).run()
  self.assertEqual(a.tabs[0].label,'Submit task')
  next(t for t in a.text_input if t.label=='Task ID').set_value('my-own-task')
  next(b for b in a.button if b.label=='Place task').click().run()
  self.assertFalse(a.exception)
  self.assertTrue(any('my-own-task' in x.value and 'Edge' in x.value for x in a.success))
  self.assertTrue(any('45.00 ms' in x.value for x in a.info))
if __name__=='__main__': unittest.main()''');p.write_text(s)
