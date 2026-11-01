import unittest
from simulator.engine import Engine, Task

class SimulatorTests(unittest.TestCase):
    def test_fractional_release(self):
        e=Engine()
        for i in range(3): e.submit(Task(str(i),'tenant_a',.1,.1,'low',1))
        e.run_until_complete()
        self.assertTrue(all(n['cpu_used']==n['ram_used']==0 for n in e.snapshot()))
    def test_completion(self):
        e=Engine(); r=e.submit(Task('x','tenant_a',2,1,'high',80))
        self.assertEqual(r['node'],'Edge'); self.assertEqual(r['response_ms'],45)
        self.assertEqual(e.snapshot()[0]['cpu_used'],2)
        e.advance(40); self.assertEqual(e.get_task('tenant_a','x')['status'],'completed')
        self.assertEqual(e.snapshot()[0]['cpu_used'],0)
    def test_security(self):
        e=Engine(); e.submit(Task('x','tenant_a',2,1,'high',80))
        for action in [lambda:e.get_task('tenant_b','x'),lambda:e.stop('tenant_b','vm-x')]:
            with self.assertRaises(PermissionError): action()
        self.assertEqual(e.snapshot()[0]['cpu_used'],2)
    def test_stop_twice(self):
        e=Engine(); e.submit(Task('x','tenant_a',2,1,'high',80))
        e.stop('tenant_a','vm-x'); e.stop('tenant_a','vm-x'); e.advance(100)
        self.assertEqual(e.snapshot()[0]['cpu_used'],0)
        self.assertEqual(e.get_task('tenant_a','x')['status'],'cancelled')
    def test_rejection_and_fallback(self):
        e=Engine()
        for i in range(10): e.submit(Task(str(i),'tenant_a',4,4,'low',400))
        rows=e.records('tenant_a')
        self.assertIn('Fog',[r['node'] for r in rows]); self.assertIn('Cloud',[r['node'] for r in rows])
        self.assertEqual(e.submit(Task('huge','tenant_a',100,1,'low',1))['status'],'rejected')
    def test_validation(self):
        e=Engine()
        for cpu in [0,-1,float('nan'),float('inf')]:
            with self.assertRaises(ValueError): e.submit(Task('x','tenant_a',cpu,1,'low',1))
        e.submit(Task('x','tenant_a',1,1,'low',1))
        with self.assertRaises(ValueError): e.submit(Task('x','tenant_a',1,1,'low',1))
        with self.assertRaises(ValueError): e.advance(-1)
    def test_deterministic(self):
        def run():
            e=Engine(policy='capacity_aware')
            for i in range(18): e.submit(Task(str(i),'tenant_a',2,2,'low',100))
            e.advance(1000); return e.records('tenant_a'),e.history
        self.assertEqual(run(),run())
    def test_policy_difference(self):
        a=Engine(); b=Engine(policy='capacity_aware')
        task=Task('x','tenant_a',4,4,'low',400)
        self.assertNotEqual(a.submit(task)['node'], b.submit(task)['node'])
    def test_capacity_invariant(self):
        e=Engine()
        for i in range(50):
            e.submit(Task(str(i),'tenant_a',2,2,'medium',80,e.clock))
            for n in e.snapshot():
                self.assertTrue(0<=n['cpu_used']<=n['cpu']); self.assertTrue(0<=n['ram_used']<=n['ram'])
            e.advance(e.clock+2)
        e.advance(1000)
        self.assertTrue(all(n['cpu_used']==n['ram_used']==0 for n in e.snapshot()))
if __name__=='__main__': unittest.main()

