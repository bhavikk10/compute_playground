import unittest
from simulator.engine import Engine,Task
from simulator.workloads import seeded_workload

NODES=[dict(name='Edge',cpu=1,ram=1,latency=5,speed=1,watts_per_cpu=2)]
class ExtensionTests(unittest.TestCase):
    def test_queue_and_waiting_response(self):
        e=Engine(NODES,queue_enabled=True)
        e.submit(Task('first','tenant_a',1,1,'high',20))
        self.assertEqual(e.submit(Task('next','tenant_a',1,1,'high',20))['status'],'queued')
        self.assertEqual(len(e.vms('tenant_a')),1)
        e.advance(20); r=e.get_task('tenant_a','next')
        self.assertEqual((r['status'],r['start_ms'],r['wait_ms'],r['response_ms']),('running',20,20,45))
        e.run_until_complete(); self.assertEqual(e.get_task('tenant_a','next')['status'],'completed')
    def test_deadline_and_impossible(self):
        e=Engine(NODES,queue_enabled=True)
        e.submit(Task('long','tenant_a',1,1,'low',200))
        e.submit(Task('urgent','tenant_a',1,1,'high',20))
        self.assertEqual(e.submit(Task('huge','tenant_a',2,1,'low',1))['status'],'rejected')
        e.advance(60); self.assertEqual(e.get_task('tenant_a','urgent')['status'],'expired')
        self.assertEqual(len(e.vms('tenant_a')),1)
    def test_release_at_deadline_cannot_start_late(self):
        e=Engine(NODES,queue_enabled=True); e.submit(Task('busy','tenant_a',1,1,'low',60))
        e.submit(Task('urgent','tenant_a',1,1,'high',1)); e.advance(60)
        self.assertEqual(e.get_task('tenant_a','urgent')['status'],'expired')
    def test_stop_dispatch_and_energy(self):
        e=Engine(NODES,queue_enabled=True);e.submit(Task('a','tenant_a',1,1,'low',100))
        e.submit(Task('b','tenant_a',1,1,'low',100)); e.advance(25);e.stop('tenant_a','vm-a')
        self.assertEqual(e.get_task('tenant_a','b')['start_ms'],25)
        self.assertAlmostEqual(e.get_task('tenant_a','a')['energy_j'],.05)
        e.stop('tenant_a','vm-a');e.run_until_complete()
        self.assertAlmostEqual(e.get_task('tenant_a','a')['energy_j'],.05)
        self.assertAlmostEqual(e.get_task('tenant_a','b')['energy_j'],.2)
    def test_protected_explorer(self):
        e=Engine();e.submit(Task('private','tenant_a',1,1,'low',10))
        with self.assertRaises(PermissionError):e.decisions('tenant_b','private')
        self.assertEqual(e.timeline('tenant_b'),[])
        self.assertEqual(len(e.decisions('tenant_a','private')[0]['nodes']),3)
        events=e.timeline('tenant_a');events[0]['event']='tamper'
        self.assertNotEqual(e.timeline('tenant_a')[0]['event'],'tamper')
    def test_seeded_workloads(self):
        self.assertEqual(seeded_workload(7,30),seeded_workload(7,30))
        self.assertNotEqual(seeded_workload(7,30),seeded_workload(8,30))
        self.assertEqual(len(seeded_workload(7,30)),30)
        with self.assertRaises(ValueError):seeded_workload(7,0)
    def test_energy_policy(self):
        e=Engine(policy='energy_aware');r=e.submit(Task('x','tenant_a',1,1,'low',10))
        self.assertEqual(r['node'],'Edge');e.run_until_complete()
        self.assertAlmostEqual(e.get_task('tenant_a','x')['energy_j'],.02)
    def test_equal_time_completions_before_queue(self):
        n=[dict(name='Edge',cpu=2,ram=2,latency=0,speed=1,watts_per_cpu=2)]
        e=Engine(n,queue_enabled=True)
        e.submit(Task('a','tenant_a',1,1,'low',20));e.submit(Task('b','tenant_a',1,1,'low',20))
        e.submit(Task('c','tenant_a',2,2,'high',20));e.advance(20)
        self.assertEqual(e.get_task('tenant_a','c')['start_ms'],20)
        self.assertEqual(e.get_task('tenant_a','c')['response_ms'],30)
    def test_queued_cancellation(self):
        e=Engine(NODES,queue_enabled=True);e.submit(Task('a','tenant_a',1,1,'low',100));e.submit(Task('b','tenant_a',1,1,'low',100))
        with self.assertRaises(PermissionError):e.cancel_queued('tenant_b','b')
        e.cancel_queued('tenant_a','b');e.run_until_complete()
        self.assertEqual(e.get_task('tenant_a','b')['status'],'cancelled')
        self.assertEqual(len(e.vms('tenant_a')),1)
if __name__=='__main__':unittest.main()
