import json
from pathlib import Path
import pandas as pd
import streamlit as st
from simulator.engine import Engine,Task,DEFAULT_NODES
from experiments.run_experiments import workload
st.set_page_config(page_title='ARM305 Resource Lab',layout='wide')
st.title('ARM305 Resource Lab')
st.caption('Deterministic Edge / Fog / Cloud simulation. CPU units, RAM in GB, time in ms. Shared node utilization is public; task and VM records are tenant protected.')
with st.sidebar:
    st.subheader('Simulation controls')
    tenant=st.selectbox('Demo identity',['tenant_a','tenant_b'])
    st.caption('Identity switching is for the classroom demonstration. No passwords or real authentication.')
    policy=st.selectbox('Policy',['latency_first','capacity_aware'])
    edge_cpu=st.number_input('Edge CPU capacity',1,64,4)
    edge_ram=st.number_input('Edge RAM (GB)',1,128,4)
    edge_latency=st.number_input('Edge network delay (ms)',0,500,5)
    if st.button('Reset with these settings') or 'engine' not in st.session_state:
        nodes=[dict(n) for n in DEFAULT_NODES]; nodes[0].update(cpu=edge_cpu,ram=edge_ram,latency=edge_latency)
        st.session_state.engine=Engine(nodes,policy); st.session_state.loaded=False
    st.caption('Policy and capacity changes apply when you reset.')
e=st.session_state.engine
if 'last_decision' in st.session_state:
    st.info(st.session_state.pop('last_decision'))
st.write(f'Clock: **{e.clock:.2f} ms** · Active policy: **{e.policy}** · Identity: **{tenant}**')
a,b,c=st.columns(3)
if a.button('Load 18 sample tasks',disabled=st.session_state.loaded):
    ids={r['id'] for t in ('tenant_a','tenant_b') for r in e.records(t)}
    if ids.intersection(t.id for t in workload()):
        st.warning('Sample task IDs already exist. Reset before loading samples.')
    else:
        offset=e.clock
        for t in workload(): e.submit(Task(t.id,t.tenant,t.cpu,t.ram,t.sensitivity,t.work,offset+t.arrival))
        st.session_state.loaded=True; st.rerun()
if b.button('Advance 50 ms'): e.advance(e.clock+50); st.rerun()
if c.button('Run until complete'): e.run_until_complete(); st.rerun()
for col,n in zip(st.columns(3),e.snapshot()):
    with col:
        st.subheader(n['name'])
        st.write(f"CPU {n['cpu_used']:g} / {n['cpu']:g} units"); st.progress(n['cpu_used']/n['cpu'])
        st.write(f"RAM {n['ram_used']:g} / {n['ram']:g} GB"); st.progress(n['ram_used']/n['ram'])
        st.caption(f"Network {n['latency']} ms · speed {n['speed']} work units / CPU / ms")
tabs=st.tabs(['Tasks and VMs','Submit task','Experiments','Security demonstration'])
with tabs[0]:
    rows=e.records(tenant); df=pd.DataFrame(rows)
    st.write(f"Your tasks: {len(rows)} · completed: {sum(r['status']=='completed' for r in rows)} · rejected: {sum(r['status']=='rejected' for r in rows)}")
    st.dataframe(df,width='stretch',hide_index=True)
    st.download_button('Export my task records',df.to_csv(index=False),'my_tasks.csv','text/csv')
    st.subheader('Your simulated VMs'); vms=e.vms(tenant); st.dataframe(pd.DataFrame(vms),hide_index=True)
    active=[v['id'] for v in vms if v['status']=='running']
    if active:
        vm=st.selectbox('Running VM',active)
        if st.button('Stop selected VM'): e.stop(tenant,vm); st.rerun()
with tabs[1]:
    with st.form('submit'):
        id=st.text_input('Task ID',f'custom-{len(e.history)}')
        cpu=st.number_input('CPU units',min_value=0.1,value=2.0)
        ram=st.number_input('RAM (GB)',min_value=0.1,value=1.0)
        sensitivity=st.selectbox('Latency sensitivity',['high','medium','low'])
        work=st.number_input('Work units',min_value=0.1,value=80.0)
        submitted=st.form_submit_button('Place task')
    if submitted:
        try:
            result=e.submit(Task(id,tenant,cpu,ram,sensitivity,work,e.clock)); st.session_state.last_decision=result['reason']; st.rerun()
        except ValueError as ex: st.error(str(ex))
        st.button('Refresh resource display',on_click=lambda:None)
with tabs[2]:
    st.caption('Published classroom experiments contain synthetic demo data from both tenants. Live task exports remain tenant scoped.')
    if st.button('Regenerate reproducible experiments'):
        from experiments.run_experiments import main
        main(); st.success('Saved CSV tables, charts, and experiment evidence.')
    path=Path(__file__).parent/'results/summary.csv'
    if path.exists():
        st.dataframe(pd.read_csv(path),hide_index=True)
        for name in ['placements','qos','utilization']: st.image(str(path.parent/'charts'/f'{name}.png'))
with tabs[3]:
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
