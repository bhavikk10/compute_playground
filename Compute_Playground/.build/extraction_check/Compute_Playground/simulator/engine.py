"""Deterministic event-driven simulation. Time: ms. Energy: illustrative incremental joules."""
from dataclasses import dataclass, asdict
from copy import deepcopy
import math

BUDGETS = {'high': 60, 'medium': 180, 'low': 600}
TENANTS = ('tenant_a', 'tenant_b')
POLICIES = ('latency_first', 'capacity_aware', 'energy_aware')
DEFAULT_NODES = [
    dict(name='Edge', cpu=4, ram=4, latency=5, speed=1, watts_per_cpu=2),
    dict(name='Fog', cpu=12, ram=16, latency=25, speed=2, watts_per_cpu=6),
    dict(name='Cloud', cpu=32, ram=64, latency=100, speed=4, watts_per_cpu=18),
]

@dataclass(frozen=True)
class Task:
    id: str
    tenant: str
    cpu: float
    ram: float
    sensitivity: str
    work: float
    arrival: float = 0


def positive(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0


class Engine:
    def __init__(self, nodes=None, policy='latency_first', queue_enabled=False):
        if policy not in POLICIES:
            raise ValueError('Unknown policy')
        self.nodes = deepcopy(DEFAULT_NODES if nodes is None else nodes)
        if not self.nodes or len({n['name'] for n in self.nodes}) != len(self.nodes):
            raise ValueError('Unique nodes required')
        for n in self.nodes:
            n.setdefault('watts_per_cpu', 2)
            if not all(positive(n[k]) for k in ('cpu', 'ram', 'speed', 'watts_per_cpu')) or not isinstance(n['latency'], (int, float)) or not math.isfinite(n['latency']) or n['latency'] < 0:
                raise ValueError('Invalid node')
            n.update(cpu_used=0, ram_used=0)
        self.policy = policy
        self.queue_enabled = bool(queue_enabled)
        self.clock = 0.
        self._tasks, self._vms, self._decisions = {}, {}, {}
        self._events, self.history, self.audit = [], [], []
        self._record()

    def _refresh_energy(self):
        for r in self._tasks.values():
            if r['start_ms'] is not None:
                end = r['end_ms'] if r['end_ms'] is not None else self.clock
                r['energy_j'] = r['cpu'] * r['watts_per_cpu'] * max(0, end - r['start_ms']) / 1000

    def _record(self):
        self._refresh_energy()
        self.history.extend(dict(time_ms=self.clock, **deepcopy(n)) for n in self.nodes)

    def _event(self, row, event, detail=''):
        self._events.append(dict(time_ms=self.clock, task_id=row['id'], tenant=row['tenant'], event=event, node=row['node'], detail=detail))

    def snapshot(self):
        return deepcopy(self.nodes)

    def _tenant(self, tenant):
        if tenant not in TENANTS:
            raise PermissionError('Unknown demo tenant')

    def _owned(self, tenant, row):
        self._tenant(tenant)
        if row['tenant'] != tenant:
            self.audit.append(dict(time_ms=self.clock, actor=tenant, outcome='DENIED', action='protected record access'))
            raise PermissionError('Access denied: record belongs to another tenant')

    def records(self, tenant):
        self._tenant(tenant)
        return deepcopy([r for r in self._tasks.values() if r['tenant'] == tenant])

    def vms(self, tenant):
        self._tenant(tenant)
        return deepcopy([r for r in self._vms.values() if r['tenant'] == tenant])

    def timeline(self, tenant):
        self._tenant(tenant)
        return deepcopy([r for r in self._events if r['tenant'] == tenant])

    def get_task(self, tenant, task_id):
        row = self._tasks[task_id]
        self._owned(tenant, row)
        return deepcopy(row)

    def decisions(self, tenant, task_id):
        self._owned(tenant, self._tasks[task_id])
        return deepcopy(self._decisions[task_id])

    def _evaluate(self, row, ignore_usage=False):
        evaluations = []
        wait = self.clock - row['arrival']
        energy_scale = max(row['work'] * n['watts_per_cpu'] / n['speed'] / 1000 for n in self.nodes)
        for n in self.nodes:
            cpu_free = n['cpu'] - (0 if ignore_usage else n['cpu_used'])
            ram_free = n['ram'] - (0 if ignore_usage else n['ram_used'])
            processing = row['work'] / (row['cpu'] * n['speed'])
            response = wait + processing + n['latency']
            capacity = row['cpu'] <= cpu_free + 1e-12 and row['ram'] <= ram_free + 1e-12
            qos = response <= row['budget_ms'] + 1e-12
            utilization = max((n['cpu'] - cpu_free + row['cpu']) / n['cpu'], (n['ram'] - ram_free + row['ram']) / n['ram'])
            energy = row['cpu'] * n['watts_per_cpu'] * processing / 1000
            w = {'high': .8, 'medium': .5, 'low': .2}[row['sensitivity']]
            if self.policy == 'latency_first':
                score = n['latency']
            elif self.policy == 'capacity_aware':
                score = w * response / row['budget_ms'] + (1-w) * utilization
            else:
                score = .5 * response / row['budget_ms'] + .5 * energy / energy_scale
            evaluations.append(dict(node=n['name'], cpu_available=cpu_free, ram_available=ram_free,
                capacity_pass=capacity, qos_pass=qos, eligible=capacity and qos, processing_ms=processing,
                wait_ms=wait, response_ms=response, projected_utilization=utilization,
                estimated_energy_j=energy, score=score, selected=False))
        return evaluations

    def _attempt(self, row):
        nodes = self._evaluate(row)
        eligible = [n for n in nodes if n['eligible']]
        chosen = min(eligible, key=lambda n: (n['score'], n['node'])) if eligible else None
        if chosen:
            chosen['selected'] = True
        self._decisions[row['id']].append(dict(time_ms=self.clock, policy=self.policy, nodes=deepcopy(nodes)))
        checks = '; '.join(f"{n['node']}: capacity={'pass' if n['capacity_pass'] else 'fail'}, QoS={'pass' if n['qos_pass'] else 'fail'}" for n in nodes)
        row['reason'] = checks
        if chosen:
            n = next(n for n in self.nodes if n['name'] == chosen['node'])
            row.update(node=n['name'], status='running', start_ms=self.clock, wait_ms=chosen['wait_ms'],
                processing_ms=chosen['processing_ms'], response_ms=chosen['response_ms'],
                finish_ms=self.clock + chosen['processing_ms'], estimated_energy_j=chosen['estimated_energy_j'],
                watts_per_cpu=n['watts_per_cpu'], reason=f"{n['name']} selected; {self.policy} score={chosen['score']:.4f}. " + checks)
            self._vms['vm-' + row['id']] = dict(id='vm-' + row['id'], task_id=row['id'], tenant=row['tenant'],
                host=n['name'], cpu=row['cpu'], ram=row['ram'], created_ms=self.clock, stopped_ms=None, status='running')
            self._recount(n)
            self._event(row, 'allocated', row['reason'])
            self._record()
        return bool(chosen)

    def submit(self, task):
        self._tenant(task.tenant)
        if not isinstance(task.id, str) or not task.id.strip() or task.id in self._tasks:
            raise ValueError('Task ID must be nonempty and unique')
        if not all(positive(v) for v in (task.cpu, task.ram, task.work)) or task.sensitivity not in BUDGETS:
            raise ValueError('Invalid task')
        if not isinstance(task.arrival, (int, float)) or not math.isfinite(task.arrival) or task.arrival < self.clock:
            raise ValueError('Arrival precedes clock')
        self.advance(task.arrival)
        row = dict(asdict(task), policy=self.policy, budget_ms=BUDGETS[task.sensitivity],
            deadline_ms=task.arrival + BUDGETS[task.sensitivity], node='', status='rejected',
            processing_ms=None, response_ms=None, finish_ms=None, start_ms=None, end_ms=None,
            wait_ms=0., energy_j=0., estimated_energy_j=0., watts_per_cpu=0., reason='')
        self._tasks[task.id] = row
        self._decisions[task.id] = []
        self._event(row, 'arrived')
        if not self._attempt(row):
            if self.queue_enabled and any(n['eligible'] for n in self._evaluate(row, ignore_usage=True)):
                row['status'] = 'queued'
                self._event(row, 'queued', 'Waiting for resources; absolute response deadline applies.')
            else:
                self._event(row, 'rejected', row['reason'])
        self._record()
        return deepcopy(row)

    def _recount(self, node):
        for key in ('cpu', 'ram'):
            node[key + '_used'] = math.fsum(v[key] for v in self._vms.values() if v['host'] == node['name'] and v['status'] == 'running')

    def _release(self, vm, status):
        if vm['status'] != 'running':
            return
        vm.update(status=status, stopped_ms=self.clock)
        node = next(n for n in self.nodes if n['name'] == vm['host'])
        self._recount(node)
        row = self._tasks[vm['task_id']]
        row.update(status='completed' if status == 'completed' else 'cancelled', end_ms=self.clock)
        self._event(row, row['status'])
        self._record()

    def _dispatch(self):
        queued = sorted((r for r in self._tasks.values() if r['status'] == 'queued'),
                        key=lambda r: (r['deadline_ms'], r['arrival'], r['id']))
        for row in queued:
            if self.clock >= row['deadline_ms']:
                row.update(status='expired', wait_ms=self.clock-row['arrival'], reason='Response deadline expired while waiting')
                self._event(row, 'expired', row['reason'])
            else:
                self._attempt(row)

    def advance(self, to_ms):
        if not isinstance(to_ms, (int, float)) or not math.isfinite(to_ms) or to_ms < self.clock:
            raise ValueError('Invalid clock')
        while True:
            moments = [r['finish_ms'] for r in self._tasks.values() if r['status'] == 'running']
            moments += [r['deadline_ms'] for r in self._tasks.values() if r['status'] == 'queued']
            if not moments or min(moments) > to_ms:
                break
            self.clock = min(moments)
            for row in sorted(self._tasks.values(), key=lambda r: r['id']):
                if row['status'] == 'running' and row['finish_ms'] <= self.clock:
                    self._release(self._vms['vm-' + row['id']], 'completed')
            self._dispatch()
            self._record()
        self.clock = to_ms
        self._refresh_energy()

    def stop(self, tenant, vm_id):
        vm = self._vms[vm_id]
        self._owned(tenant, vm)
        self._release(vm, 'stopped')
        self._dispatch()
        return deepcopy(vm)

    def cancel_queued(self, tenant, task_id):
        row = self._tasks[task_id]
        self._owned(tenant, row)
        if row['status'] == 'queued':
            row.update(status='cancelled', wait_ms=self.clock-row['arrival'], reason='Cancelled while queued')
            self._event(row, 'cancelled', row['reason'])
        return deepcopy(row)

    def run_until_complete(self):
        while any(r['status'] in ('running', 'queued') for r in self._tasks.values()):
            moments = [r['finish_ms'] for r in self._tasks.values() if r['status'] == 'running']
            moments += [r['deadline_ms'] for r in self._tasks.values() if r['status'] == 'queued']
            self.advance(min(moments))
