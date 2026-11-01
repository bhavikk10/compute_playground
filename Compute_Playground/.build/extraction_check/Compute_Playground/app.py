import json
import time
from pathlib import Path
import pandas as pd
import streamlit as st
from simulator.engine import Engine,Task,DEFAULT_NODES,POLICIES
from simulator.workloads import seeded_workload
from experiments.extended_experiments import queue_demo
from experiments.run_experiments import workload
st.set_page_config(page_title='Compute Playground',layout='wide')
st.title('Compute Playground')
st.caption('CDEF Computing · Learn by placing tasks on Edge, Fog and Cloud')
st.caption('Deterministic Edge / Fog / Cloud simulation. CPU units, RAM in GB, time in ms. Shared node utilization is public; task and VM records are tenant protected.')
POLICY_LABELS={'latency_first':'Lowest delay','capacity_aware':'Spare capacity','energy_aware':'Energy balance'}
POLICY_EXPLANATIONS={'latency_first':'Choose the eligible server with the shortest network trip. A nearby server may still process work more slowly.', 'capacity_aware':'Balance response time against how full each server would become.', 'energy_aware':'Balance response time against a hypothetical compute-energy estimate. This is not measured electricity.'}
with st.sidebar:
    st.subheader('Your workspace')
    tenant=st.selectbox('Demo identity',['tenant_a','tenant_b'],format_func=lambda t:'Tenant A' if t=='tenant_a' else 'Tenant B',help='Tasks belong to the selected tenant. Change identity to demonstrate that another tenant cannot open your records.')
    st.caption('Two pretend users, separate task records. This selector is a classroom demo, not a real login.')
    st.subheader('Choose the rules')
    policy=st.selectbox('Policy',list(POLICIES),format_func=lambda p:POLICY_LABELS[p],help='Every rule checks free CPU, free RAM and the task response deadline first.')
    st.caption(POLICY_EXPLANATIONS[policy])
    queue_enabled=st.checkbox('Queue temporarily blocked tasks',value=False,help='On: a suitable task may wait for resources until its deadline. Off: reject it immediately when no server fits.')
    with st.expander('Generated-workload settings'):
        st.caption('A seed recreates the same list of jobs. These settings apply when you press Schedule seeded workload.')
        seed=st.number_input('Workload seed',min_value=0,max_value=99999,value=7)
        count=st.number_input('Generated task count',min_value=10,max_value=100,value=40)
    with st.expander('Change the Edge server (advanced)'):
        st.caption('Try changing one value, reset, then repeat the same workload. Fog and Cloud keep their default settings.')
        edge_cpu=st.number_input('Edge CPU capacity',1,64,4,help='How many processing units Edge can reserve at once.')
        edge_ram=st.number_input('Edge RAM (GB)',1,128,4,help='How much memory Edge can reserve at once.')
        edge_latency=st.number_input('Edge network delay (ms)',0,500,5,help='Travel delay added to predicted response time, in milliseconds.')
    if st.button('Reset with these settings',help='Clears live tasks, VMs and scheduled arrivals. Saved experiment files stay on disk.') or 'engine' not in st.session_state:
        nodes=[dict(n) for n in DEFAULT_NODES]; nodes[0].update(cpu=edge_cpu,ram=edge_ram,latency=edge_latency)
        st.session_state.engine=Engine(nodes,policy,queue_enabled); st.session_state.loaded=False
        st.session_state.pending=[]; st.session_state.playing=False
        st.session_state.pop('submission_receipt',None)
    st.caption('Changing a rule or server setting takes effect after reset. Reset clears the current playground.')

e=st.session_state.engine
st.session_state.setdefault('pending',[])
st.session_state.setdefault('playing',False)
st.session_state.setdefault('last_frame_wall',time.monotonic())
def tick(target):
    while st.session_state.pending and st.session_state.pending[0].arrival<=target:
        task=st.session_state.pending.pop(0)
        e.submit(task)
    e.advance(target)

@st.fragment(run_every='1s')
def playback():
    if st.session_state.playing and time.monotonic()-st.session_state.last_frame_wall>=.85:
        st.session_state.last_frame_wall=time.monotonic()
        if not st.session_state.pending and not any(r['status'] in ('running','queued') for t in ('tenant_a','tenant_b') for r in e.records(t)):
            st.session_state.playing=False
        else:
            tick(e.clock+20)
            st.rerun()
playback()

if 'last_decision' in st.session_state:
    st.info(st.session_state.pop('last_decision'))
st.write(f'Clock: **{e.clock:.2f} ms**  /  Active rule: **{POLICY_LABELS[e.policy]}**  /  Workspace: **{tenant}**')
if e.policy!=policy or e.queue_enabled!=queue_enabled or any(e.nodes[0][k]!=v for k,v in [('cpu',edge_cpu),('ram',edge_ram),('latency',edge_latency)]):
    st.warning('The sidebar settings differ from the active playground. Press Reset with these settings to apply them and clear live tasks.')
with st.expander('Start here: your first task in three steps',expanded=not e.records(tenant)):
    st.markdown('**1. Make a job.** In Submit task below, keep 2 CPU units, 1 GB RAM, High sensitivity and 80 work units. Give it any unique name and press Place task.\n\n**2. Read the answer.** You will see the selected server, predicted response and resources reserved. With fresh default settings, Edge predicts 45 ms.\n\n**3. Finish the job.** Press Advance 50 ms, then open Tasks and VMs. The task completes and its CPU/RAM become free again.')
    st.caption('CPU = helpers; RAM = table space; work = job size. Everything here is simulated. You can submit as many uniquely named tasks as you like; capacity and deadlines decide whether they fit.')
st.markdown('**Move simulated time** — processing finishes only when you advance or play the clock.')
a,b,c=st.columns(3)
if a.button('Load 18 sample tasks',disabled=st.session_state.loaded,help='Adds a prepared two-tenant workload and advances through its arrivals to 100 ms. Earlier tasks may already be finished.'):
    ids={r['id'] for t in ('tenant_a','tenant_b') for r in e.records(t)}|{t.id for t in st.session_state.pending}
    if ids.intersection(t.id for t in workload()):
        st.warning('Sample task IDs already exist. Reset before loading samples.')
    else:
        offset=e.clock
        st.session_state.pending.extend(Task(t.id,t.tenant,t.cpu,t.ram,t.sensitivity,t.work,offset+t.arrival) for t in workload())
        st.session_state.pending.sort(key=lambda t:t.arrival)
        tick(offset+100)
        st.session_state.loaded=True; st.rerun()
if b.button('Advance 50 ms',help='Move 50 simulated milliseconds forward. Complete due jobs and retry waiting tasks.'): tick(e.clock+50); st.rerun()
if c.button('Run until complete',help='Deliver every scheduled job, finish running work and resolve all waiting deadlines.'):
    if st.session_state.pending: tick(st.session_state.pending[-1].arrival)
    e.run_until_complete(); st.session_state.playing=False; st.rerun()
st.caption('Ready-made examples are optional: submit your own tasks in the first tab, or use these buttons to explore larger workloads.')
p1,p2,p3=st.columns(3)
if p1.button('Pause timeline' if st.session_state.playing else 'Play timeline'):
    st.session_state.playing=not st.session_state.playing;st.session_state.last_frame_wall=time.monotonic();st.rerun()
if p2.button('Schedule seeded workload'):
    generated=seeded_workload(int(seed),int(count))
    ids={r['id'] for t in ('tenant_a','tenant_b') for r in e.records(t)}|{t.id for t in st.session_state.pending}
    if ids.intersection(t.id for t in generated):st.warning('These seed IDs already exist. Reset or use another seed.')
    else:
        st.session_state.pending.extend(Task(t.id,t.tenant,t.cpu,t.ram,t.sensitivity,t.work,e.clock+t.arrival) for t in generated)
        st.session_state.pending.sort(key=lambda t:t.arrival)
        tick(e.clock);st.rerun()
if p3.button('Load queue demonstration',help='Replaces the current playground with a fresh queue-enabled example: one blocked job succeeds, one urgent job expires.'):
    st.session_state.pop('submission_receipt',None)
    st.session_state.engine=Engine(policy=policy,queue_enabled=True)
    e=st.session_state.engine;st.session_state.pending=[];st.session_state.playing=False;st.session_state.loaded=False
    for task in queue_demo():e.submit(task)
    st.rerun()
st.caption(f"Active queue: {'on' if e.queue_enabled else 'off'} / Scheduled future tasks: {len(st.session_state.pending)}. Play advances 20 virtual ms each second; it does not execute real workloads. Queue demonstration starts a fresh queue-enabled world.")
for col,n in zip(st.columns(3),e.snapshot()):
    with col:
        st.subheader(n['name'])
        st.caption({'Edge':'Nearby workshop: small capacity, short trip.','Fog':'Town workshop: more capacity and faster processing.','Cloud':'Distant workshop: most capacity, longest trip.'}.get(n['name'],''))
        st.write(f"CPU {n['cpu_used']:g} / {n['cpu']:g} units"); st.progress(min(1.,max(0.,n['cpu_used']/n['cpu'])))
        st.write(f"RAM {n['ram_used']:g} / {n['ram']:g} GB"); st.progress(min(1.,max(0.,n['ram_used']/n['ram'])))
        st.caption(f"Network {n['latency']} ms  /  speed {n['speed']} work units / CPU / ms")
tabs=st.tabs(['Submit task','Tasks and VMs','Experiments','Security demonstration','Timeline','Decision explorer'])
with tabs[1]:
    st.subheader('Your jobs and their resource bookings')
    st.caption('Only your tenant’s jobs are listed. Server bars above show shared usage across both tenants.')
    rows=e.records(tenant); df=pd.DataFrame(rows)
    st.write(f"Your tasks: {len(rows)}  /  completed: {sum(r['status']=='completed' for r in rows)}  /  rejected: {sum(r['status']=='rejected' for r in rows)}")
    if rows:
        visible=['id','status','node','cpu','ram','wait_ms','response_ms','energy_j']
        st.dataframe(df[visible],width='stretch',hide_index=True,column_config={'id':'Task name','status':'What happened','node':'Server','cpu':'CPU reserved','ram':'RAM (GB)','wait_ms':'Waiting (ms)','response_ms':'Predicted response (ms)','energy_j':'Modeled compute energy (J)'})
        with st.expander('What do task statuses mean?'):
            st.write('Queued: waiting, no resources reserved. Running: resources reserved. Completed: processing finished and resources freed. Rejected: no suitable placement. Expired: waiting deadline passed. Cancelled: you stopped or cancelled it.')
        with st.expander('All task fields and decision reasons'):st.dataframe(df,hide_index=True)
    else:st.info('No jobs in your workspace yet. Open Submit task to add your own, or load the sample workload.')
    st.download_button('Export my task records',df.to_csv(index=False),'my_tasks.csv','text/csv')
    st.subheader('Your simulated VMs');st.caption('A VM is a booking ticket for CPU and RAM. Stopping a running VM cancels its task and returns those resources. No actual virtual machine starts.'); vms=e.vms(tenant); st.dataframe(pd.DataFrame(vms),hide_index=True)
    active=[v['id'] for v in vms if v['status']=='running']
    if active:
        vm=st.selectbox('Running VM',active)
        if st.button('Stop selected VM'): e.stop(tenant,vm); st.rerun()
with tabs[0]:
    st.subheader('Create your own task')
    st.write('Give your job a name and tell us what it needs. The chooser will find a suitable server or explain why it cannot fit.')
    st.caption(f'Owner: {tenant}. Your task arrives now, at {e.clock:.2f} ms. Nothing is sent to a real cloud.')
    with st.expander('What should I enter? Example: a small urgent job',expanded=False):
        st.write('Use 2 CPU, 1 GB RAM, High sensitivity and 80 work units. On an empty default Edge server: 80 ÷ (2 × 1) = 40 ms processing, plus 5 ms network = 45 ms response. High sensitivity permits at most 60 ms. Waiting, if any, adds to that response.')
    receipt=st.session_state.get('submission_receipt')
    if receipt and receipt[0]==tenant:
        result=e.get_task(tenant,receipt[1])
        if result['start_ms'] is not None:
            st.success(f"Task {result['id']} accepted on {result['node']}. Current status: {result['status']}.")
            st.info(f"Predicted response: {result['response_ms']:.2f} ms = {result['wait_ms']:.2f} waiting + {result['processing_ms']:.2f} processing + {result['response_ms']-result['wait_ms']-result['processing_ms']:.2f} network. Budget: {result['budget_ms']} ms.")
            st.caption('Next: Advance 50 ms or Run until complete, then inspect Tasks and VMs. Decision explorer explains the server scores.')
        elif result['status']=='queued':st.info(f"Task {result['id']} is waiting for capacity. It has no VM yet. Advance the clock to retry; its deadline is {result['deadline_ms']:.2f} ms.")
        else:st.warning(f"Task {result['id']}: {result['status']}. {result['reason']}")
    with st.form('submit'):

        id=st.text_input('Task ID',f'custom-{len(e.history)}',help='A unique name, such as my-drawing or camera-job-1. Sample IDs and scheduled IDs cannot be reused.')
        cpu=st.number_input('CPU units',min_value=0.1,value=2.0,help='How many processing helpers to reserve. Example: 2 uses half of default Edge CPU. More CPU speeds this task up but leaves less for other jobs.')
        ram=st.number_input('RAM (GB)',min_value=0.1,value=1.0,help='Memory/table space needed while processing. A task must fit in the server’s currently free RAM.')
        sensitivity=st.selectbox('Latency sensitivity',['high','medium','low'],format_func=lambda s:{'high':'High: urgent, up to 60 ms','medium':'Medium: up to 180 ms','low':'Low: can wait up to 600 ms'}[s],help='How quickly the whole response must arrive: waiting + processing + network trip.')
        work=st.number_input('Work units',min_value=0.1,value=80.0,help='Job size. Larger numbers take longer. 80 work / 2 CPU / Edge speed 1 = 40 ms processing.')
        st.caption('A task needs both enough free resources and a response within its budget. Pressing Place task makes a simulated reservation; it does not run a real program.')
        submitted=st.form_submit_button('Place task')
    if submitted:
        try:
            if id in {t.id for t in st.session_state.pending}:raise ValueError('Task ID is reserved by a scheduled task')
            result=e.submit(Task(id,tenant,cpu,ram,sensitivity,work,e.clock)); st.session_state.submission_receipt=(tenant,result['id']); st.rerun()
        except ValueError as ex: st.error(str(ex))

with tabs[2]:
    st.subheader('Compare the rules fairly')
    st.write('These are saved, repeatable classroom experiments. They are separate from your live playground. Regenerate runs the fixed workloads again and overwrites the saved results.')
    st.caption('Published classroom experiments contain synthetic demo data from both tenants. Live task exports remain tenant scoped.')
    if st.button('Regenerate reproducible experiments'):
        from experiments.run_experiments import main
        main(); st.success('Saved CSV tables, charts, and experiment evidence.')
    path=Path(__file__).parent/'results/summary.csv'
    if path.exists():
        st.dataframe(pd.read_csv(path),hide_index=True)
        st.subheader('Paired seeded experiments and queue comparison')
        for filename in ['seeded_summary.csv','queue_comparison.csv']:
            extra=path.parent/filename
            if extra.exists():st.dataframe(pd.read_csv(extra),hide_index=True)
        st.caption('Energy is hypothetical incremental compute energy. Compare joules alongside completed counts. Whiskers show sample SD across 10 seeds, not confidence intervals.')
        for name in ['seeded_comparison','placements','qos','utilization']:
            chart=path.parent/'charts'/f'{name}.png'
            if chart.exists():st.image(str(chart))
with tabs[3]:
    st.subheader('Try opening another tenant’s job')
    st.write('First load the 18 sample tasks. Choose Tenant B in the sidebar, leave task ID T01 below, then attempt View task or Stop VM. Both should be denied because T01 belongs to Tenant A.')
    target=st.text_input('Protected task ID to request','T01')
    action=st.selectbox('Protected operation',['View task','Stop VM'])
    if st.button('Attempt access as current tenant'):
        try:
            if action=='View task': st.json(e.get_task(tenant,target))
            else:
                e.stop(tenant,'vm-'+target); st.session_state.last_decision='VM stop processed'; st.rerun()
        except PermissionError as ex: st.error(str(ex))
        except KeyError: st.warning('Task does not exist. Load the sample workload first.')
    st.caption('T01 belongs to tenant_a. Select tenant_b to demonstrate denial. Audit logs are recorded by the engine.')

with tabs[4]:
    import matplotlib.pyplot as plt
    st.subheader('Your task timeline')
    st.caption('Only the current tenant is visible. Hatched grey = waiting; filled blue = elapsed processing; outlined blue = remaining planned processing; a cross marks an arrival without allocation. Network delay contributes to response but is not a compute reservation.')
    own=e.records(tenant)[-40:]
    if own:
        fig,ax=plt.subplots(figsize=(11,max(3,len(own)*.32)))
        for i,r in enumerate(own):
            start=r['start_ms']
            waiting=(start-r['arrival']) if start is not None else ((e.clock-r['arrival']) if r['status']=='queued' else r['wait_ms'])
            if waiting>0:ax.barh(i,waiting,left=r['arrival'],color='#dddddd',hatch='//',edgecolor='#999999',height=.6)
            if start is not None:
                end=r['end_ms'] if r['end_ms'] is not None else e.clock
                if r['status']=='running':ax.barh(i,r['finish_ms']-start,left=start,color='none',edgecolor='#286680',linestyle=':',height=.6)
                if end>start:ax.barh(i,end-start,left=start,color='#286680',height=.6)
                else:ax.plot(start,i,'|',color='#286680')
            else:ax.plot(r['arrival'],i,'x',color='#875437')
        horizon=max([1,e.clock]+[(r['end_ms'] if r['end_ms'] is not None else r['finish_ms'] if r['status']=='running' else r['arrival']) for r in own])
        ax.set_xlim(0,horizon*1.05)
        ax.set_yticks(range(len(own)),[r['id']+' / '+r['status'] for r in own]);ax.axvline(e.clock,color='#b27525',label='Current virtual time');ax.set_xlabel('Virtual ms');ax.invert_yaxis();fig.tight_layout();st.pyplot(fig);plt.close(fig)
    else:st.info('Submit a task or schedule a seeded workload to begin.')
    events=pd.DataFrame(e.timeline(tenant));st.dataframe(events,hide_index=True)
    st.download_button('Export my timeline',events.to_csv(index=False),'my_timeline.csv','text/csv')
    queued=[r['id'] for r in e.records(tenant) if r['status']=='queued']
    if queued:
        selected=st.selectbox('Your queued task',queued)
        if st.button('Cancel queued task'):e.cancel_queued(tenant,selected);st.rerun()
with tabs[5]:
    st.subheader('Why was this node selected?')
    st.write('Choose one of your tasks, then an evaluation attempt. A server can win only when both capacity and QoS checks pass. Among those servers, the lowest score wins. The selected column marks the winner.')
    own=e.records(tenant)
    if own:
        task_id=st.selectbox('Your task to explain',[r['id'] for r in own])
        trials=e.decisions(tenant,task_id)
        index=st.selectbox('Evaluation attempt',range(len(trials)),format_func=lambda i:f"Attempt {i+1} at {trials[i]['time_ms']:g} ms")
        trial=trials[index];st.write(f"Policy: {trial['policy']}");st.dataframe(pd.DataFrame(trial['nodes']),hide_index=True)
        st.write(e.get_task(tenant,task_id)['reason'])
        st.caption('Each attempt is a saved snapshot. Waiting counts against the response budget. Ineligible nodes cannot win even with a low score. Energy values and power coefficients are hypothetical.')
    else:st.info('Your task decisions will appear here after submission.')
