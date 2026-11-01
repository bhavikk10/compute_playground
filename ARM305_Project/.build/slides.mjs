import fs from 'node:fs/promises';
import { Presentation, PresentationFile } from 'file:///C:/Users/bhavi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs';
const p=Presentation.create({slideSize:{width:1280,height:720}});
const content=[
['Compute Playground\nEdge, Fog and Cloud','CDEF Computing mini project\nDeterministic Python simulation\nLocal execution with Streamlit'],
['Architecture and resource model','Tenant tasks pass through ownership and placement checks.\nEdge: 4 CPU, 4 GB, 5 ms network delay\nFog: 12 CPU, 16 GB, 25 ms network delay\nCloud: 32 CPU, 64 GB, 100 ms network delay\nOne simulated VM reserves resources for each accepted task.'],
['Placement and virtual time','Both policies filter available CPU, RAM and response budgets.\nLatency first minimizes network delay.\nCapacity aware balances response against projected utilization.\nProcessing = work / (CPU x speed).\nResponse = processing + network delay.\nVirtual completion events release resources exactly once.'],
['Policy comparison','18 tasks completed under each policy.\nMean response: 68.06 ms latency first, 89.17 ms capacity aware.\nPeak Fog CPU: 100% latency first, 41.67% capacity aware.\nCapacity aware preserves headroom at a response-time cost.'],
['Overload and security evidence','Overload: 20 simultaneous tasks, 12 completed, 8 rejected.\nFallback placements: 1 Edge, 3 Fog, 8 Cloud.\nTenant B cannot view or stop Tenant A records.\nDenied attempts leave resource allocations unchanged.\nRepeated VM stopping releases resources only once.'],
['Parameter changes and limitations','Edge capacity 4/4 to 12/12: Edge placements rise from 2 to 8.\nMean response rises to 70.56 ms because Edge processes slower.\nEdge delay 5 to 90 ms: mean 76.39 ms, same placement counts.\nFixed latency, reserved CPU and synthetic work are assumptions.\nDemo identities illustrate authorization, not authentication.\nReproduce with the experiment runner and unittest suite.']
];
function text(s,t,x,y,w,h,size,color='#163343'){const a=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});a.text=t;a.text.style={fontFamily:'Arial',fontSize:size,color};return a;}
for(let i=0;i<content.length;i++){
 const s=p.slides.add();s.background.fill='#F7FAFB';
 text(s,'CDEF COMPUTING / COMPUTE PLAYGROUND',64,30,1100,30,18,'#54717F');
 text(s,content[i][0],64,95,1140,i===0?160:90,i===0?58:42);
 text(s,content[i][1],64,i===0?300:210,i===3?570:1140,370,i===0?30:27);
 text(s,`${i+1} / 6`,1100,665,120,30,18);
 if(i===3) s.charts.add('bar',{position:{left:710,top:220,width:480,height:370},categories:['Latency first','Capacity aware'],series:[{name:'Mean response (ms)',values:[68.06,89.17],fill:'#286680'}],hasLegend:false,dataLabels:{showValue:true,position:'outEnd'}});
 await fs.writeFile(`.build/slide-${i+1}.png`,new Uint8Array(await (await p.export({slide:s,format:'png',scale:1})).arrayBuffer()));
}
await (await PresentationFile.exportPptx(p)).save('.build/draft.pptx');
console.log('6 slides exported');

