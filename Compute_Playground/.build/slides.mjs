import fs from 'node:fs/promises';
import {Presentation,PresentationFile} from 'file:///C:/Users/bhavi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const p=Presentation.create({slideSize:{width:1280,height:720}});
const content=[
['Compute Playground\nEdge, Fog and Cloud','CDEF Computing mini project\nDeterministic resource simulation\nTimeline, deadlines and explainable decisions'],
['Architecture and state','Tenant-owned tasks enter a placement engine.\nThree tiers reserve CPU and RAM through simulated VMs.\nA virtual clock processes arrivals and completions.\nOptional queues hold temporarily blocked jobs.\nProtected timelines and decision snapshots explain outcomes.'],
['Placement and deadlines','Latency first minimizes eligible network delay.\nCapacity aware balances response and projected utilization.\nEnergy aware balances response and modeled task energy.\nResponse = waiting + processing + network delay.\nEarliest deadlines get queue priority. Expired jobs never start.\nAll policies must pass CPU, RAM and response checks.'],
['Baseline policy comparison','Same 18 tasks, queues off: both policies complete all tasks.\nMean response: 68.06 ms latency first, 89.17 ms capacity aware.\nPeak Fog CPU: 100% versus 41.67%.\nCapacity aware preserves headroom at a response cost.'],
['Queue and security evidence','Same 14 tasks with queue off: 12 completed, 2 rejected.\nQueue on: 13 completed, 1 expired, 0 rejected.\nWaiting counts against each job\'s response deadline.\nTenant B cannot view or stop Tenant A records.\nTimelines and decision details also enforce ownership.\nStopping a running VM releases resources exactly once.'],
['Ten paired workload seeds','40 tasks per seed, identical for each policy, queues on.\nAverage completions: 32.8 latency, 33.5 capacity, 32.9 energy.\nMean response: 74.30, 89.40 and 72.48 ms respectively.\nModeled energy: 16.232, 21.424 and 16.456 J.\nEnergy aware did not produce the lowest total energy.\nCompare energy alongside completed task counts.'],
['Energy assumptions and real resources','Power coefficients are hypothetical: 2 / 6 / 18 W per CPU.\nJoules = CPU x coefficient x processing seconds.\nIdle, network, RAM, cooling and VM boot costs are omitted.\nReal execution requires an unimplemented infrastructure adapter.\nIt must launch, monitor and stop work and reconcile resources.\nDemo identities and predicted durations are not production services.']
];
function text(s,t,x,y,w,h,size,color='#163343'){const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});a.text=t;a.text.style={fontFamily:'Aptos',fontSize:size,color};}
for(let i=0;i<content.length;i++){
 const s=p.slides.add();s.background.fill='#F7FAFB';text(s,'CDEF COMPUTING / COMPUTE PLAYGROUND',64,30,1120,30,18,'#54717F');
 text(s,content[i][0],64,95,1140,i===0?170:90,i===0?58:42);
 text(s,content[i][1],64,i===0?310:210,i===3?580:1140,380,i===0?30:27);
 text(s,`${i+1} / 7`,1100,665,120,30,18);
 if(i===3)s.charts.add('bar',{position:{left:725,top:230,width:470,height:370},categories:['Latency first','Capacity aware'],series:[{name:'Mean predicted response (ms)',values:[68.06,89.17],fill:'#286680'}],hasLegend:false,dataLabels:{showValue:true,position:'outEnd'}});
 await fs.writeFile(`.build/slide-${i+1}.png`,new Uint8Array(await(await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));
}
await(await PresentationFile.exportPptx(p)).save('.build/extended-draft.pptx');console.log('Seven slides exported');
