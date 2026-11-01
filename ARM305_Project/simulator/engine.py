from dataclasses import dataclass, asdict
from copy import deepcopy
import math
BUDGETS={'high':60,'medium':180,'low':600}
TENANTS=('tenant_a','tenant_b')
DEFAULT_NODES=[dict(name='Edge',cpu=4,ram=4,latency=5,speed=1),dict(name='Fog',cpu=12,ram=16,latency=25,speed=2),dict(name='Cloud',cpu=32,ram=64,latency=100,speed=4)]
@dataclass(frozen=True)
class Task:
    id:str
    tenant:str
    cpu:float
    ram:float
    sensitivity:str
    work:float
    arrival:float=0

def positive(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) and x>0
class Engine:
    def __init__(self,nodes=None,policy='latency_first'):
        if policy not in ('latency_first','capacity_aware'): raise ValueError('Unknown policy')
        self.nodes=deepcopy(DEFAULT_NODES if nodes is None else nodes)
        if not self.nodes or len({n['name'] for n in self.nodes})!=len(self.nodes): raise ValueError('Unique nodes required')
        for n in self.nodes:
            if not all(positive(n[k]) for k in ('cpu','ram','speed')) or not math.isfinite(n['latency']) or n['latency']<0: raise ValueError('Invalid node')
            n.update(cpu_used=0,ram_used=0)
        self.policy=policy; self.clock=0.; self._tasks={}; self._vms={}; self.history=[]; self.audit=[]; self._record()
    def _record(self): self.history.extend(dict(time_ms=self.clock,**deepcopy(n)) for n in self.nodes)
    def snapshot(self): return deepcopy(self.nodes)
    def _tenant(self,t):
        if t not in TENANTS: raise PermissionError('Unknown demo tenant')
    def _owned(self,t,r):
        self._tenant(t)
        if r['tenant']!=t:
            self.audit.append(dict(time_ms=self.clock,actor=t,outcome='DENIED',action='protected record access'))
            raise PermissionError('Access denied: record belongs to another tenant')
    def records(self,t):
        self._tenant(t); return deepcopy([r for r in self._tasks.values() if r['tenant']==t])
    def vms(self,t):
        self._tenant(t); return deepcopy([r for r in self._vms.values() if r['tenant']==t])
    def get_task(self,t,id):
        r=self._tasks[id]; self._owned(t,r); return deepcopy(r)
    def submit(self,t):
        self._tenant(t.tenant)
        if not t.id or t.id in self._tasks: raise ValueError('Task ID must be nonempty and unique')
        if not all(positive(v) for v in (t.cpu,t.ram,t.work)) or t.sensitivity not in BUDGETS: raise ValueError('Invalid task')
        if not math.isfinite(t.arrival) or t.arrival<self.clock: raise ValueError('Arrival precedes clock')
        self.advance(t.arrival); candidates=[]; checks=[]
        for n in self.nodes:
            p=t.work/(t.cpu*n['speed']); r=n['latency']+p
            cap=n['cpu_used']+t.cpu<=n['cpu'] and n['ram_used']+t.ram<=n['ram']; qos=r<=BUDGETS[t.sensitivity]
            checks.append(f"{n['name']}: capacity={'pass' if cap else 'fail'}, QoS={'pass' if qos else 'fail'}")
            if cap and qos:
                u=max((n['cpu_used']+t.cpu)/n['cpu'],(n['ram_used']+t.ram)/n['ram'])
                w={'high':.8,'medium':.5,'low':.2}[t.sensitivity]
                score=n['latency'] if self.policy=='latency_first' else w*r/BUDGETS[t.sensitivity]+(1-w)*u
                candidates.append((score,n['name'],n,p,r))
        row=dict(asdict(t),policy=self.policy,budget_ms=BUDGETS[t.sensitivity],node='',status='rejected',processing_ms=None,response_ms=None,finish_ms=None,reason='; '.join(checks))
        if candidates:
            score,_,n,p,r=min(candidates,key=lambda c:(c[0],c[1])); n['cpu_used']+=t.cpu; n['ram_used']+=t.ram
            row.update(node=n['name'],status='running',processing_ms=p,response_ms=r,finish_ms=self.clock+p,reason=f"{n['name']} selected; {self.policy} score={score:.4f}. "+row['reason'])
            self._vms['vm-'+t.id]=dict(id='vm-'+t.id,task_id=t.id,tenant=t.tenant,host=n['name'],cpu=t.cpu,ram=t.ram,created_ms=self.clock,stopped_ms=None,status='running')
        self._tasks[t.id]=row; self._record(); return deepcopy(row)
    def _release(self,vm,status):
        if vm['status']!='running': return
        n=next(n for n in self.nodes if n['name']==vm['host']); n['cpu_used']-=vm['cpu']; n['ram_used']-=vm['ram']
        vm.update(status=status,stopped_ms=self.clock)
        for key in ('cpu','ram'):
            n[key+'_used']=math.fsum(v[key] for v in self._vms.values() if v['host']==n['name'] and v['status']=='running')
        self._tasks[vm['task_id']]['status']='completed' if status=='completed' else 'cancelled'; self._record()
    def advance(self,to_ms):
        if not isinstance(to_ms,(int,float)) or not math.isfinite(to_ms) or to_ms<self.clock: raise ValueError('Invalid clock')
        due=sorted((r for r in self._tasks.values() if r['status']=='running' and r['finish_ms']<=to_ms),key=lambda r:(r['finish_ms'],r['id']))
        for r in due:
            self.clock=r['finish_ms']; self._release(self._vms['vm-'+r['id']],'completed')
        self.clock=to_ms
    def stop(self,t,id):
        vm=self._vms[id]; self._owned(t,vm); self._release(vm,'stopped'); return deepcopy(vm)
    def run_until_complete(self): self.advance(max([self.clock]+[r['finish_ms'] for r in self._tasks.values() if r['status']=='running']))
