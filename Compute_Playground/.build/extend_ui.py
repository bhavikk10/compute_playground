from pathlib import Path
p=Path('app.py');s=p.read_text(encoding='utf-8').replace('Â·',' / ')
s=s.replace('from simulator.engine import Engine,Task,DEFAULT_NODES','from simulator.engine import Engine,Task,DEFAULT_NODES,POLICIES\nfrom simulator.workloads import seeded_workload\nfrom experiments.extended_experiments import queue_demo')
s=s.replace("policy=st.selectbox('Policy',['latency_first','capacity_aware'])","policy=st.selectbox('Policy',list(POLICIES))\n    queue_enabled=st.checkbox('Queue temporarily blocked tasks',value=False)\n    seed=st.number_input('Workload seed',min_value=0,max_value=99999,value=7)\n    count=st.number_input('Generated task count',min_value=10,max_value=100,value=40)")
s=s.replace("st.session_state.engine=Engine(nodes,policy); st.session_state.loaded=False","st.session_state.engine=Engine(nodes,policy,queue_enabled); st.session_state.loaded=False\n        st.session_state.pending=[]; st.session_state.playing=False")
s=s.replace("e=st.session_state.engine", """e=st.session_state.engine
st.session_state.setdefault('pending',[])
st.session_state.setdefault('playing',False)
def tick(target):
    while st.session_state.pending and st.session_state.pending[0].arrival<=target:
        task=st.session_state.pending.pop(0)
        e.submit(task)
    e.advance(target)

@st.fragment(run_every='1s')
def playback():
    if st.session_state.playing:
        if not st.session_state.pending and not any(r['status'] in ('running','queued') for t in ('tenant_a','tenant_b') for r in e.records(t)):
            st.session_state.playing=False
        else:
            tick(e.clock+20)
            st.rerun()
playback()
""")
s=s.replace("if b.button('Advance 50 ms'): e.advance(e.clock+50); st.rerun()","if b.button('Advance 50 ms'): tick(e.clock+50); st.rerun()")
s=s.replace("if c.button('Run until complete'): e.run_until_complete(); st.rerun()", """if c.button('Run until complete'):
    if st.session_state.pending: tick(st.session_state.pending[-1].arrival)
    e.run_until_complete(); st.session_state.playing=False; st.rerun()
p1,p2,p3=st.columns(3)
if p1.button('Pause timeline' if st.session_state.playing else 'Play timeline'):
    st.session_state.playing=not st.session_state.playing;st.rerun()
if p2.button('Schedule seeded workload'):
    generated=seeded_workload(int(seed),int(count))
    ids={r['id'] for t in ('tenant_a','tenant_b') for r in e.records(t)}|{t.id for t in st.session_state.pending}
    if ids.intersection(t.id for t in generated):st.warning('These seed IDs already exist. Reset or use another seed.')
    else:
        st.session_state.pending.extend(Task(t.id,t.tenant,t.cpu,t.ram,t.sensitivity,t.work,e.clock+t.arrival) for t in generated)
        st.session_state.pending.sort(key=lambda t:t.arrival)
        tick(e.clock);st.rerun()
if p3.button('Load queue demonstration'):
    st.session_state.engine=Engine(policy=policy,queue_enabled=True)
    e=st.session_state.engine;st.session_state.pending=[];st.session_state.playing=False;st.session_state.loaded=False
    for task in queue_demo():e.submit(task)
    st.rerun()
st.caption(f"Active queue: {'on' if e.queue_enabled else 'off'} / Scheduled future tasks: {len(st.session_state.pending)}. Play advances 20 virtual ms each second; it does not execute real workloads. Queue demonstration starts a fresh queue-enabled world.")""")
s=s.replace("tabs=st.tabs(['Tasks and VMs','Submit task','Experiments','Security demonstration'])","tabs=st.tabs(['Tasks and VMs','Submit task','Experiments','Security demonstration','Timeline','Decision explorer'])")
s=s.replace("        for name in ['placements','qos','utilization']: st.image(str(path.parent/'charts'/f'{name}.png'))", """        st.subheader('Paired seeded experiments and queue comparison')
        for filename in ['seeded_summary.csv','queue_comparison.csv']:
            extra=path.parent/filename
            if extra.exists():st.dataframe(pd.read_csv(extra),hide_index=True)
        st.caption('Energy is hypothetical incremental compute energy. Compare joules alongside completed counts. Whiskers show sample SD across 10 seeds, not confidence intervals.')
        for name in ['seeded_comparison','placements','qos','utilization']:
            chart=path.parent/'charts'/f'{name}.png'
            if chart.exists():st.image(str(chart))""")
s+='''
with tabs[4]:
    import matplotlib.pyplot as plt
    st.subheader('Your task timeline')
    st.caption('Only the current tenant is visible. Hatched grey = waiting; blue = processing; a cross marks an arrival without allocation. Network delay contributes to response but is not a compute reservation.')
    own=e.records(tenant)[-40:]
    if own:
        fig,ax=plt.subplots(figsize=(11,max(3,len(own)*.32)))
        for i,r in enumerate(own):
            start=r['start_ms']
            waiting=(start if start is not None else min(e.clock,r['deadline_ms']))-r['arrival']
            if waiting>0:ax.barh(i,waiting,left=r['arrival'],color='#dddddd',hatch='//',edgecolor='#999999',height=.6)
            if start is not None:
                end=r['end_ms'] if r['end_ms'] is not None else e.clock
                ax.barh(i,max(.05,end-start),left=start,color='#286680',height=.6)
            else:ax.plot(r['arrival'],i,'x',color='#875437')
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
    own=e.records(tenant)
    if own:
        task_id=st.selectbox('Your task to explain',[r['id'] for r in own])
        trials=e.decisions(tenant,task_id)
        index=st.selectbox('Evaluation attempt',range(len(trials)),format_func=lambda i:f"Attempt {i+1} at {trials[i]['time_ms']:g} ms")
        trial=trials[index];st.write(f"Policy: {trial['policy']}");st.dataframe(pd.DataFrame(trial['nodes']),hide_index=True)
        st.write(e.get_task(tenant,task_id)['reason'])
        st.caption('Each attempt is a saved snapshot. Waiting counts against the response budget. Ineligible nodes cannot win even with a low score. Energy values and power coefficients are hypothetical.')
    else:st.info('Your task decisions will appear here after submission.')
'''
p.write_text(s,encoding='utf-8')
