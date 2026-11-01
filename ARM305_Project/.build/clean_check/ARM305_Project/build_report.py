from pathlib import Path
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
R=Path(__file__).parent
fig,ax=plt.subplots(figsize=(11,6)); ax.set_xlim(0,11); ax.set_ylim(-.2,6.1); ax.axis('off')
boxes=[(4,5,'Demo tenants / tasks'),(4,3.8,'Streamlit + ownership checks'),(4,2.6,'Placement + simulation clock'),(.4,1.2,'Edge: 4 CPU / 4 GB'),(4,1.2,'Fog: 12 CPU / 16 GB'),(7.6,1.2,'Cloud: 32 CPU / 64 GB'),(4,0,'VM records / metrics / CSV')]
for x,y,label in boxes:
    ax.add_patch(FancyBboxPatch((x,y),3,.65,boxstyle='round,pad=0.05',facecolor='#e9f0f3',edgecolor='#24556a')); ax.text(x+1.5,y+.325,label,ha='center',va='center',fontsize=10)
for x1,y1,x2,y2 in [(5.5,5,5.5,4.45),(5.5,3.8,5.5,3.25),(5.5,2.6,1.9,1.85),(5.5,2.6,5.5,1.85),(5.5,2.6,9.1,1.85),(1.9,1.2,5.5,.65),(5.5,1.2,5.5,.65),(9.1,1.2,5.5,.65)]: ax.annotate('',(x2,y2),(x1,y1),arrowprops=dict(arrowstyle='->',color='#24556a'))
fig.tight_layout(); fig.savefig(R/'docs/architecture.png',dpi=180); plt.close(fig)
styles=getSampleStyleSheet(); styles['BodyText'].fontSize=10; styles['BodyText'].leading=15
story=[]
def p(t): story.extend([Paragraph(t,styles['BodyText']),Spacer(1,10)])
def title(t): story.extend([Paragraph(t,styles['Heading1']),Spacer(1,12)])
def table(data,widths=None):
    t=Table(data,colWidths=widths,hAlign='LEFT'); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9f0f3')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('LINEBELOW',(0,0),(-1,-1),.3,colors.lightgrey)])); story.extend([t,Spacer(1,12)])
def page(): story.append(PageBreak())
title('ARM 305 | Edge, Fog and Cloud Resource Simulator')
p('Mini project report - deterministic local Python simulation')
p('<b>Objective.</b> Accept tenant-owned computing tasks, select suitable Edge, Fog or Cloud resources, maintain simulated VM records and report placement, resource use, QoS and access-control outcomes. The project runs locally without paid infrastructure.')
p('<b>Scope.</b> Three configurable nodes, 18 baseline tasks, two placement policies, virtual time, create/stop VM operations, tenant ownership checks, CSV exports and matplotlib charts. All numerical results in this report come from the included experiment runner.')
p('<b>Approach.</b> A Python engine owns state and authorization. Streamlit supplies controls and tables. A separate runner executes the same engine without the interface, making results repeatable and inspectable.')
p('<b>Submission guide.</b> README.md contains setup and demonstration instructions. results/ contains task, VM and utilization CSVs. evidence/ contains experimental setup, expected outcomes, actual outcomes, security and lifecycle records. docs/ contains this report, architecture and slides.')
p('<b>Student details.</b> The team must add its actual names, roll numbers and contribution record in docs/team_details.md before final submission.')
p('<b>Interpretation.</b> These are model predictions rather than physical server benchmarks. CPU units and node speeds are abstract parameters. No hypervisor or cloud account is required.')
page(); title('2. Architecture and data model'); story.append(Image(str(R/'docs/architecture.png'),width=470,height=256))
p('Tasks pass through resource and latency admission checks. Placement reserves CPU/RAM and creates one VM per task. The clock processes completion events, releases reservations and records utilization snapshots. Protected record methods check the acting tenant before returning or modifying data.')
table([['Node','CPU','RAM GB','Delay ms','Speed'],['Edge','4','4','5','1'],['Fog','12','16','25','2'],['Cloud','32','64','100','4']])
p('Task fields: ID, tenant, CPU, RAM, sensitivity, work and arrival time. VM fields: ID, task ID, owner, host, reserved CPU/RAM, creation/stop time and status. Engine records include selected node, response estimate, finish time and decision reason. Duplicate IDs and invalid numeric inputs are rejected.')
page(); title('3. Placement algorithms and QoS model')
p('Processing time in ms = work / (reserved CPU units x node processing speed). Work is CPU-ms at speed 1. Predicted response time = processing time + total network delay. CPU/RAM remain allocated through processing; network delay does not reserve compute resources. Completed status denotes compute completion.')
p('Budgets are 60 ms for high sensitivity, 180 ms for medium, and 600 ms for low. Every policy first removes nodes lacking CPU/RAM or exceeding the predicted response budget. If none remain, it rejects the task and logs per-node capacity and QoS checks. No queue or migration is modelled.')
p('<b>Lowest latency first.</b> Choose the feasible node with minimum network delay. This does not necessarily minimize total response time because node processing speed differs.')
p('<b>Capacity aware.</b> For each feasible node compute projected utilization U = max(projected CPU fraction, projected RAM fraction). Score = w x (response / budget) + (1-w) x U. Choose the minimum. Weights are .8, .5 and .2 for high, medium and low sensitivity. Node name breaks equal scores deterministically.')
p('Example: 2 CPU, 1 GB, 80 work, high sensitivity on Edge requires 40 ms compute and 45 ms predicted response, satisfying the 60 ms budget. High-sensitivity tasks cannot use Cloud at its baseline network delay of 100 ms.')
p('The clock is absolute and finite. At equal timestamps, completions free resources before new arrivals. Simultaneous arrivals follow workload list order. A task keeps its reserved CPU rather than sharing it dynamically. These choices make repeated experiments identical.')
page(); title('4. Implementation, VM lifecycle and access control')
p('simulator/engine.py contains Task and Engine. submit validates inputs, advances to arrival time, evaluates candidates, stores a decision and optionally creates a VM. advance processes due completions in timestamp/ID order. stop verifies ownership and cancels running work. run_until_complete advances to the final compute completion.')
p('VM creation is a reservation record, not a guest operating system. A VM starts running and becomes completed or stopped. A manually stopped task becomes cancelled. Release checks current VM status so repeated stopping and later clock advancement cannot release resources twice.')
p('records(tenant), vms(tenant), get_task(tenant, id) and stop(tenant, vm_id) enforce ownership. Callers receive copies rather than mutable internal records. Denied operations produce an audit entry. Shared aggregate resource utilization is intentionally public.')
p('The demo identity selector deliberately allows classroom impersonation. It demonstrates authorization boundaries, not authenticated identity. Published experiments contain synthetic cross-tenant data and are not a confidential production datastore. No real passwords or sensitive information are used.')
p('Streamlit stores the engine in session state. Policy and Edge parameter edits take effect on reset. Custom submissions use current virtual time. Sample loading advances through three arrival batches at 0, 50 and 100 ms. Earlier tasks can therefore complete during loading.')
p('Automated tests cover resource bounds, completion timing, rejection/fallback, denied view/stop, idempotent stopping, invalid numeric input, duplicate IDs, backward time, policy difference and repeatability. Tests run with the standard unittest module.')
page(); title('5. Experiment design and evidence')
for name,setup,expected,evidence in [('Policy comparison','18 tasks, same order and arrivals, fresh state for both policies','Compare allocation, response time and peak utilization','baseline_* CSVs'),('Overload','20 simultaneous tasks requesting 4 CPU and 4 GB each','Fallback, then reject when no feasible capacity remains','overload_* CSVs'),('Capacity change','Increase Edge CPU/RAM from 4/4 to 12/12','More Edge placements may change latency','capacity_increase_* CSVs'),('Latency change','Increase Edge network delay from 5 to 90 ms','High-sensitivity tasks become ineligible for Edge','latency_increase_* CSVs'),('Tenant isolation','Tenant B requests view and stop of Tenant A task','Both denied with resources unchanged','evidence/security.json'),('VM lifecycle','Stop a running VM twice, then advance the clock','Resources restored once; task cancelled','evidence/lifecycle.json')]:
    p(f'<b>{name}.</b> Setup: {setup}. Expected: {expected}. Evidence: {evidence}.')
p('The baseline has 18 tasks over two tenants with CPU requirements 1-4 units, RAM 1-4 GB and all sensitivity classes. Three batches preserve overlap and resource contention. Exact inputs are saved in workloads/baseline.json. Every scenario uses a new engine, preventing state contamination.')
p('evidence/experiments.json records actual outcomes alongside expectations. Resource CSVs retain every allocation/release snapshot, including peaks that disappear after all tasks finish. CSVs and charts regenerate with python -m experiments.run_experiments.')
page(); title('6. Measured results')
df=pd.read_csv(R/'results/summary.csv')
table([['Scenario','Done / total','Rejected','Mean ms','P95 ms']]+[[r.experiment.replace('baseline_',''),f'{r.completed} / {r.total}',str(r.rejected),str(r.mean_ms),str(r.p95_ms)] for r in df.itertuples()])
story.append(Image(str(R/'results/charts/qos.png'),width=470,height=235))
p('Both baseline policies completed 18/18 tasks. Capacity-aware increased mean predicted response from 68.06 to 89.17 ms while reducing peak Fog CPU utilization from 100% to 41.67%. It selected 9 Fog and 9 Cloud tasks; latency-first selected 2 Edge, 15 Fog and 1 Cloud task. This is a headroom/latency trade-off, not universal superiority.')
p('Overload completed 12/20 tasks and rejected 8: Edge accepted 1, Fog 3 and Cloud 8. Every accepted task met its predicted budget. Increasing Edge capacity shifted its placements from 2 to 8, but mean response increased to 70.56 ms because more tasks used the slower Edge processor.')
page(); title('7. Utilization, conclusions and limitations')
story.append(Image(str(R/'results/charts/utilization.png'),width=470,height=235))
p('Increasing Edge delay to 90 ms produced mean response 76.39 ms and p95 170 ms. Aggregate placement counts stayed the same in this workload. The absence of a count change is an observed result; it does not mean latency had no QoS effect. Strict admission retained 100% predicted compliance among completed tasks in every scenario.')
p('Read QoS beside rejected counts. Response mean and p95 use completed tasks only; p95 uses linear interpolation. Peak CPU/RAM fractions use event snapshots. There is no measured wall-clock server execution, and no claim of scheduling optimality.')
p('Security evidence shows both unauthorized view and stop denied, with resources unchanged. Lifecycle evidence shows a stopped VM releases its reservation exactly once. Automated checks verify bounds and deterministic execution. These results support the required local simulation and basic tenant separation.')
p('Limitations include synthetic capacities, fixed network delay, no queueing, no VM boot overhead, no failures, no dynamic contention or migration, and demo identity selection. Future work could add queues, randomized latency with fixed seeds, authenticated sessions and additional nodes. Such extensions would require fresh validation.')
p('Reproduction: install requirements.txt, run unittest, then run experiments.run_experiments. Open app.py with Streamlit for the live demonstration. Evidence and results are generated from the same engine used by the interface. The assignment brief supplies the project requirements; model parameters and formulas are explicit project assumptions.')
def footer(c,d):
    c.setFont('Helvetica',9); c.setFillColor(colors.grey); c.drawString(45,25,'ARM 305 - Local resource simulation'); c.drawRightString(550,25,str(d.page))
SimpleDocTemplate(str(R/'docs/report.pdf'),pagesize=(595,842),rightMargin=45,leftMargin=45,topMargin=40,bottomMargin=45).build(story,onFirstPage=footer,onLaterPages=footer)
print('Report and architecture created')

