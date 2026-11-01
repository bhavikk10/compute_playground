from pathlib import Path
p=Path('app.py');s=p.read_text(encoding='utf-8')
start=s.index('with st.sidebar:');end=s.index('e=st.session_state.engine',start)
s=s[:start]+'''POLICY_LABELS={'latency_first':'Lowest network delay','capacity_aware':'Keep more capacity free','energy_aware':'Balance energy and response'}
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

'''+s[end:]
s=s.replace("st.write(f'Clock: **{e.clock:.2f} ms**  /  Active policy: **{e.policy}**  /  Identity: **{tenant}**')", """st.write(f'Clock: **{e.clock:.2f} ms**  /  Active rule: **{POLICY_LABELS[e.policy]}**  /  Workspace: **{tenant}**')
if e.policy!=policy or e.queue_enabled!=queue_enabled or any(e.nodes[0][k]!=v for k,v in [('cpu',edge_cpu),('ram',edge_ram),('latency',edge_latency)]):
    st.warning('The sidebar settings differ from the active playground. Press Reset with these settings to apply them and clear live tasks.')
with st.expander('Start here: your first task in three steps',expanded=not e.records(tenant)):
    st.markdown('**1. Make a job.** In Submit task below, keep 2 CPU units, 1 GB RAM, High sensitivity and 80 work units. Give it any unique name and press Place task.\\n\\n**2. Read the answer.** You will see the selected server, predicted response and resources reserved. With fresh default settings, Edge predicts 45 ms.\\n\\n**3. Finish the job.** Press Advance 50 ms, then open Tasks and VMs. The task completes and its CPU/RAM become free again.')
    st.caption('CPU = helpers; RAM = table space; work = job size. Everything here is simulated. You can submit as many uniquely named tasks as you like; capacity and deadlines decide whether they fit.')
st.markdown('**Move simulated time** — processing finishes only when you advance or play the clock.')""")
s=s.replace("a,b,c=st.columns(3)","a,b,c=st.columns(3)",1)
s=s.replace("if a.button('Load 18 sample tasks',disabled=st.session_state.loaded):", "if a.button('Load 18 sample tasks',disabled=st.session_state.loaded,help='Adds a prepared two-tenant workload and advances through its arrivals to 100 ms. Earlier tasks may already be finished.'):")
s=s.replace("if b.button('Advance 50 ms'):","if b.button('Advance 50 ms',help='Move 50 simulated milliseconds forward. Complete due jobs and retry waiting tasks.'):")
s=s.replace("if c.button('Run until complete'):","if c.button('Run until complete',help='Deliver every scheduled job, finish running work and resolve all waiting deadlines.'):")
s=s.replace("p1,p2,p3=st.columns(3)","st.caption('Ready-made examples are optional: submit your own tasks in the first tab, or use these buttons to explore larger workloads.')\np1,p2,p3=st.columns(3)")
s=s.replace("if p3.button('Load queue demonstration'):","if p3.button('Load queue demonstration',help='Replaces the current playground with a fresh queue-enabled example: one blocked job succeeds, one urgent job expires.'):")
s=s.replace("    st.session_state.engine=Engine(policy=policy,queue_enabled=True)","    st.session_state.pop('submission_receipt',None)\n    st.session_state.engine=Engine(policy=policy,queue_enabled=True)")
s=s.replace("        st.subheader(n['name'])", "        st.subheader(n['name'])\n        st.caption({'Edge':'Nearby workshop: small capacity, short trip.','Fog':'Town workshop: more capacity and faster processing.','Cloud':'Distant workshop: most capacity, longest trip.'}.get(n['name'],''))")
s=s.replace("st.progress(n['cpu_used']/n['cpu'])", "st.progress(min(1.,max(0.,n['cpu_used']/n['cpu'])))").replace("st.progress(n['ram_used']/n['ram'])", "st.progress(min(1.,max(0.,n['ram_used']/n['ram'])))")
s=s.replace("tabs=st.tabs(['Tasks and VMs','Submit task'", "tabs=st.tabs(['Submit task','Tasks and VMs'")
s=s.replace('with tabs[0]:','with tabs[TASKS]:',1).replace('with tabs[1]:','with tabs[0]:',1).replace('with tabs[TASKS]:','with tabs[1]:',1)
s=s.replace("    rows=e.records(tenant); df=pd.DataFrame(rows)", "    st.subheader('Your jobs and their resource bookings')\n    st.caption('Only your tenant’s jobs are listed. Server bars above show shared usage across both tenants.')\n    rows=e.records(tenant); df=pd.DataFrame(rows)")
s=s.replace("    st.dataframe(df,width='stretch',hide_index=True)", """    if rows:
        visible=['id','status','node','cpu','ram','wait_ms','response_ms','energy_j']
        st.dataframe(df[visible],width='stretch',hide_index=True,column_config={'id':'Task name','status':'What happened','node':'Server','cpu':'CPU reserved','ram':'RAM (GB)','wait_ms':'Waiting (ms)','response_ms':'Predicted response (ms)','energy_j':'Modeled compute energy (J)'})
        with st.expander('What do task statuses mean?'):
            st.write('Queued: waiting, no resources reserved. Running: resources reserved. Completed: processing finished and resources freed. Rejected: no suitable placement. Expired: waiting deadline passed. Cancelled: you stopped or cancelled it.')
        with st.expander('All task fields and decision reasons'):st.dataframe(df,hide_index=True)
    else:st.info('No jobs in your workspace yet. Open Submit task to add your own, or load the sample workload.')""")
s=s.replace("    st.subheader('Your simulated VMs');", "    st.subheader('Your simulated VMs');st.caption('A VM is a booking ticket for CPU and RAM. Stopping a running VM cancels its task and returns those resources. No actual virtual machine starts.');")
s=s.replace("with tabs[0]:\n    with st.form('submit'):","""with tabs[0]:
    st.subheader('Create your own task')
    st.write('Give your job a name and tell us what it needs. The chooser will find a suitable server or explain why it cannot fit.')
    st.caption(f'Owner: {tenant}. Your task arrives now, at {e.clock:.2f} ms. Nothing is sent to a real cloud.')
    with st.expander('What should I enter? Example: a small urgent job',expanded=False):
        st.write('Use 2 CPU, 1 GB RAM, High sensitivity and 80 work units. On an empty default Edge server: 80 ÷ (2 × 1) = 40 ms processing, plus 5 ms network = 45 ms response. High sensitivity permits at most 60 ms. Waiting, if any, adds to that response.')
    receipt=st.session_state.get('submission_receipt')
    if receipt and receipt[0]==tenant:
        result=e.get_task(tenant,receipt[1])
        if result['start_ms'] is not None:
            st.success(f\"Task {result['id']} accepted on {result['node']}. Current status: {result['status']}.\")
            st.info(f\"Predicted response: {result['response_ms']:.2f} ms = {result['wait_ms']:.2f} waiting + {result['processing_ms']:.2f} processing + {result['response_ms']-result['wait_ms']-result['processing_ms']:.2f} network. Budget: {result['budget_ms']} ms.\")
            st.caption('Next: Advance 50 ms or Run until complete, then inspect Tasks and VMs. Decision explorer explains the server scores.')
        elif result['status']=='queued':st.info(f\"Task {result['id']} is waiting for capacity. It has no VM yet. Advance the clock to retry; its deadline is {result['deadline_ms']:.2f} ms.\")
        else:st.warning(f\"Task {result['id']}: {result['status']}. {result['reason']}\")
    with st.form('submit'):
""")
s=s.replace("id=st.text_input('Task ID',f'custom-{len(e.history)}')", "id=st.text_input('Task ID',f'custom-{len(e.history)}',help='A unique name, such as my-drawing or camera-job-1. Sample IDs and scheduled IDs cannot be reused.')")
s=s.replace("cpu=st.number_input('CPU units',min_value=0.1,value=2.0)","cpu=st.number_input('CPU units',min_value=0.1,value=2.0,help='How many processing helpers to reserve. Example: 2 uses half of default Edge CPU. More CPU speeds this task up but leaves less for other jobs.')")
s=s.replace("ram=st.number_input('RAM (GB)',min_value=0.1,value=1.0)","ram=st.number_input('RAM (GB)',min_value=0.1,value=1.0,help='Memory/table space needed while processing. A task must fit in the server’s currently free RAM.')")
s=s.replace("sensitivity=st.selectbox('Latency sensitivity',['high','medium','low'])", "sensitivity=st.selectbox('Latency sensitivity',['high','medium','low'],format_func=lambda s:{'high':'High: urgent, up to 60 ms','medium':'Medium: up to 180 ms','low':'Low: can wait up to 600 ms'}[s],help='How quickly the whole response must arrive: waiting + processing + network trip.')")
s=s.replace("work=st.number_input('Work units',min_value=0.1,value=80.0)","work=st.number_input('Work units',min_value=0.1,value=80.0,help='Job size. Larger numbers take longer. 80 work / 2 CPU / Edge speed 1 = 40 ms processing.')\n        st.caption('A task needs both enough free resources and a response within its budget. Pressing Place task makes a simulated reservation; it does not run a real program.')")
s=s.replace("result=e.submit(Task(id,tenant,cpu,ram,sensitivity,work,e.clock)); st.session_state.last_decision=result['reason']; st.rerun()", "result=e.submit(Task(id,tenant,cpu,ram,sensitivity,work,e.clock)); st.session_state.submission_receipt=(tenant,result['id']); st.rerun()")
s=s.replace("        st.button('Refresh resource display',on_click=lambda:None)","")
s=s.replace("with tabs[2]:\n    st.caption", "with tabs[2]:\n    st.subheader('Compare the rules fairly')\n    st.write('These are saved, repeatable classroom experiments. They are separate from your live playground. Regenerate runs the fixed workloads again and overwrites the saved results.')\n    st.caption")
s=s.replace("with tabs[3]:\n    target", "with tabs[3]:\n    st.subheader('Try opening another tenant’s job')\n    st.write('First load the 18 sample tasks. Choose Tenant B in the sidebar, leave task ID T01 below, then attempt View task or Stop VM. Both should be denied because T01 belongs to Tenant A.')\n    target")
s=s.replace("    st.subheader('Why was this node selected?')", "    st.subheader('Why was this node selected?')\n    st.write('Choose one of your tasks, then an evaluation attempt. A server can win only when both capacity and QoS checks pass. Among those servers, the lowest score wins. The selected column marks the winner.')")
p.write_text(s,encoding='utf-8')
