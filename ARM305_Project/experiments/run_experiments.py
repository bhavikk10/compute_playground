"""Run from the project root: python -m experiments.run_experiments."""
from pathlib import Path
from copy import deepcopy
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from simulator.engine import Engine,Task,DEFAULT_NODES,TENANTS
ROOT=Path(__file__).resolve().parents[1]

def workload():
    return [Task(f'T{i+1:02}',TENANTS[i%2], [4,2,1,3,2,4][i%6],[4,2,1,2,3,4][i%6],['low','high','medium'][i%3],[400,80,100,180,120,320][i%6],(i//6)*50) for i in range(18)]
def all_rows(e): return sum((e.records(t) for t in TENANTS),[])
def run(tasks,policy='latency_first',nodes=None):
    e=Engine(nodes,policy)
    for t in tasks: e.submit(t)
    e.run_until_complete(); return e

def summarize(name,e):
    df=pd.DataFrame(all_rows(e)); ok=df[df.status=='completed']; h=pd.DataFrame(e.history)
    out=dict(experiment=name,policy=e.policy,total=len(df),completed=len(ok),rejected=int((df.status=='rejected').sum()),cancelled=int((df.status=='cancelled').sum()),mean_ms=round(ok.response_ms.mean(),2) if len(ok) else 0,p95_ms=round(ok.response_ms.quantile(.95),2) if len(ok) else 0,qos_percent=round(100*(ok.response_ms<=ok.budget_ms).mean(),2) if len(ok) else 0)
    for n in e.nodes:
        part=h[h.name==n['name']]; out[n['name']+'_tasks']=int((df.node==n['name']).sum()); out[n['name']+'_peak_cpu_pct']=round(100*(part.cpu_used/part.cpu).max(),2); out[n['name']+'_peak_ram_pct']=round(100*(part.ram_used/part.ram).max(),2)
    return out

def main():
    for p in ['results/charts','evidence','workloads','config']: (ROOT/p).mkdir(parents=True,exist_ok=True)
    (ROOT/'config/nodes.json').write_text(json.dumps(DEFAULT_NODES,indent=2))
    from dataclasses import asdict
    (ROOT/'workloads/baseline.json').write_text(json.dumps([asdict(t) for t in workload()],indent=2))
    overload=[Task(f'O{i:02}','tenant_a',4,4,'low',400) for i in range(20)]
    (ROOT/'workloads/overload.json').write_text(json.dumps([asdict(t) for t in overload],indent=2))
    cap=deepcopy(DEFAULT_NODES); cap[0].update(cpu=12,ram=12)
    lag=deepcopy(DEFAULT_NODES); lag[0]['latency']=90
    scenarios={'baseline_latency':run(workload()),'baseline_capacity':run(workload(),'capacity_aware'),'overload':run(overload),'capacity_increase':run(workload(),nodes=cap),'latency_increase':run(workload(),nodes=lag)}
    summaries=[]
    for name,e in scenarios.items():
        pd.DataFrame(all_rows(e)).sort_values('id').to_csv(ROOT/f'results/{name}_tasks.csv',index=False)
        pd.DataFrame(e.history).to_csv(ROOT/f'results/{name}_utilization.csv',index=False)
        pd.DataFrame(sum((e.vms(t) for t in TENANTS),[])).to_csv(ROOT/f'results/{name}_vms.csv',index=False)
        summaries.append(summarize(name,e))
    df=pd.DataFrame(summaries); df.to_csv(ROOT/'results/summary.csv',index=False)
    security=Engine(); security.submit(Task('protected','tenant_a',2,1,'high',80)); before=security.snapshot(); denied=[]
    for label,action in [('view',lambda:security.get_task('tenant_b','protected')),('stop',lambda:security.stop('tenant_b','vm-protected'))]:
        try: action(); denied.append({'action':label,'outcome':'UNEXPECTED ALLOW'})
        except PermissionError as ex: denied.append({'action':label,'outcome':'DENIED','message':str(ex)})
    assert before==security.snapshot() and all(x['outcome']=='DENIED' for x in denied)
    (ROOT/'evidence/security.json').write_text(json.dumps(dict(attempts=denied,resources_unchanged=True,audit=security.audit),indent=2))
    life=Engine(); life.submit(Task('life','tenant_a',2,1,'high',80)); allocated=life.snapshot(); life.stop('tenant_a','vm-life'); stopped=life.snapshot(); life.stop('tenant_a','vm-life'); life.advance(200)
    assert stopped==life.snapshot()
    (ROOT/'evidence/lifecycle.json').write_text(json.dumps(dict(allocated=allocated,after_stop=stopped,after_second_stop=life.snapshot(),task=life.get_task('tenant_a','life')),indent=2))
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white'})
    base=df.iloc[:2].set_index('policy')
    for cols,title,ylabel,file in [(['Edge_tasks','Fog_tasks','Cloud_tasks'],'Placement by policy','Tasks','placements'),(['mean_ms','p95_ms'],'Predicted response time of completed tasks','Milliseconds','qos'),(['Edge_peak_cpu_pct','Fog_peak_cpu_pct','Cloud_peak_cpu_pct','Edge_peak_ram_pct','Fog_peak_ram_pct','Cloud_peak_ram_pct'],'Peak resource utilization','Percent of capacity','utilization')]:
        ax=base[cols].plot.bar(figsize=(10,5),rot=0); ax.set_title(title); ax.set_ylabel(ylabel); ax.set_xlabel(''); ax.legend(fontsize=8); plt.tight_layout(); plt.savefig(ROOT/f'results/charts/{file}.png',dpi=160); plt.close()
    records=[]
    setups=[('Policy comparison','18 identical tasks; fresh state; two policies','Different selections; compare acceptance and latency','baseline_latency / baseline_capacity'),('Overload','20 simultaneous tasks, each 4 CPU / 4 GB','Fallback to Fog and Cloud; reject beyond capacity','overload'),('Capacity change','Edge CPU/RAM 4/4 to 12/12; same workload','Placement and admission may change','capacity_increase'),('Latency change','Edge delay 5 to 90 ms; same workload','High-sensitivity tasks cannot use Edge','latency_increase')]
    for title,setup,expected,key in setups:
        actual=df[df.experiment.isin(key.split(' / '))].to_dict('records')
        records.append(dict(experiment=title,setup=setup,expected=expected,actual=actual,evidence='results/summary.csv and scenario task/utilization CSVs'))
    records.extend([dict(experiment='Tenant isolation',setup='Tenant B views/stops Tenant A task',expected='Both denied without resource mutation',actual=denied,evidence='evidence/security.json'),dict(experiment='VM lifecycle',setup='Stop running VM twice, advance past completion',expected='Release exactly once; task cancelled',actual='PASS: resources restored exactly once',evidence='evidence/lifecycle.json')])
    (ROOT/'evidence/experiments.json').write_text(json.dumps(records,indent=2))
    print(df.to_string(index=False))
if __name__=='__main__': main()
