"""Paired, reproducible extension experiments; no real energy or hardware measurements."""
from pathlib import Path
from dataclasses import asdict
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from simulator.engine import Engine,Task,POLICIES,TENANTS
from simulator.workloads import seeded_workload
ROOT=Path(__file__).resolve().parents[1]

def queue_demo():
    # Fill 4+12+32 CPU with low-sensitivity jobs before the next arrivals.
    return [Task(f'fill-{i:02}','tenant_a',4,4,'low',400) for i in range(12)]+[
        Task('wait-success','tenant_a',4,4,'low',100),
        Task('urgent-expiry','tenant_a',4,4,'high',200)]

def run(tasks,policy='latency_first',queue_enabled=True):
    e=Engine(policy=policy,queue_enabled=queue_enabled)
    for t in tasks:e.submit(t)
    e.run_until_complete()
    return e

def rows(e):return sorted(sum((e.records(t) for t in TENANTS),[]),key=lambda r:r['id'])
def metrics(e):
    data=rows(e); done=[r for r in data if r['status']=='completed']; response=pd.Series([r['response_ms'] for r in done],dtype=float)
    return dict(total=len(data),completed=len(done),rejected=sum(r['status']=='rejected' for r in data),expired=sum(r['status']=='expired' for r in data),cancelled=sum(r['status']=='cancelled' for r in data),mean_ms=float(response.mean()) if done else 0,p95_ms=float(response.quantile(.95)) if done else 0,mean_wait_ms=sum(r['wait_ms'] for r in done)/len(done) if done else 0,energy_j=sum(r['energy_j'] for r in data),qos_percent=100*sum(r['response_ms']<=r['budget_ms']+1e-9 for r in done)/len(done) if done else 0)

def export_trace(name,e):
    pd.DataFrame(rows(e)).to_csv(ROOT/f'results/{name}_tasks.csv',index=False)
    pd.DataFrame(sum((e.timeline(t) for t in TENANTS),[])).sort_values(['time_ms','task_id'],kind='stable').to_csv(ROOT/f'results/{name}_timeline.csv',index=False)
    pd.DataFrame(e.history).to_csv(ROOT/f'results/{name}_utilization.csv',index=False)
    (ROOT/f'evidence/{name}_decisions.json').write_text(json.dumps({r['id']:e.decisions(r['tenant'],r['id']) for r in rows(e)},indent=2))

def main():
    records=[]
    for seed in range(10):
        tasks=seeded_workload(seed,40)
        for policy in POLICIES:
            e=run(tasks,policy)
            records.append(dict(seed=seed,policy=policy,queue_enabled=True,**metrics(e)))
            if seed==7:export_trace('seed7_'+policy,e)
    df=pd.DataFrame(records);df.to_csv(ROOT/'results/seeded_runs.csv',index=False)
    aggregate=df.groupby('policy').agg(runs=('seed','size'),completed_mean=('completed','mean'),completed_std=('completed','std'),mean_response_ms=('mean_ms','mean'),response_std_ms=('mean_ms','std'),mean_wait_ms=('mean_wait_ms','mean'),mean_energy_j=('energy_j','mean'),energy_std_j=('energy_j','std'),mean_expired=('expired','mean'),mean_rejected=('rejected','mean'))
    aggregate.to_csv(ROOT/'results/seeded_summary.csv')
    paired=[]
    for queue in (False,True):
        e=run(queue_demo(),queue_enabled=queue);name='queue_on' if queue else 'queue_off';export_trace(name,e);paired.append(dict(scenario=name,**metrics(e)))
    pd.DataFrame(paired).to_csv(ROOT/'results/queue_comparison.csv',index=False)
    (ROOT/'workloads/seed7.json').write_text(json.dumps([asdict(t) for t in seeded_workload(7,40)],indent=2))
    (ROOT/'workloads/queue_demo.json').write_text(json.dumps([asdict(t) for t in queue_demo()],indent=2))
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(13,4.5))
    for ax,col,err,title,unit in [(axes[0],'completed_mean','completed_std','Completed out of 40','Tasks'),(axes[1],'mean_response_ms','response_std_ms','Mean response per run','ms'),(axes[2],'mean_energy_j','energy_std_j','Estimated incremental compute energy','J (hypothetical)')]:
        ax.bar(aggregate.index,aggregate[col],yerr=aggregate[err],capsize=4,color='#286680');ax.set_title(title,fontsize=11);ax.set_ylabel(unit);ax.tick_params(axis='x',rotation=20)
    fig.suptitle('10 paired seeds: same 40 tasks per policy; bars show mean, whiskers show sample SD',fontsize=11);fig.tight_layout();fig.savefig(ROOT/'results/charts/seeded_comparison.png',dpi=160);plt.close(fig)
    evidence=dict(setup='Seeds 0-9; 40 tasks each; fresh engine per seed/policy; queue on for all policies. Weights and watts are model assumptions.',expected='Reproducible paired comparisons; queue can improve acceptance but waiting counts against response budgets.',actual=dict(seeded=aggregate.reset_index().to_dict('records'),queue_comparison=paired),evidence=['results/seeded_runs.csv','results/seeded_summary.csv','results/queue_comparison.csv','results/queue_on_timeline.csv','evidence/queue_on_decisions.json'],energy_model='CPU units * illustrative watts per CPU * elapsed processing ms / 1000. No idle, network, memory, cooling or real measurements. Compare energy beside completed count.')
    (ROOT/'evidence/extensions.json').write_text(json.dumps(evidence,indent=2));print(aggregate.round(3).to_string());print(pd.DataFrame(paired).round(3).to_string(index=False))
if __name__=='__main__':main()
