from pathlib import Path
p=Path('app.py');s=p.read_text()
s=s.replace('Hatcheddummy','Hatcheddummy')
s=s.replace('blue = processing; a cross marks','filled blue = elapsed processing; outlined blue = remaining planned processing; a cross marks')
s=s.replace("                ax.barh(i,max(.05,end-start),left=start,color='#286680',height=.6)","                if r['status']=='running':ax.barh(i,r['finish_ms']-start,left=start,color='none',edgecolor='#286680',linestyle=':',height=.6)\n                if end>start:ax.barh(i,end-start,left=start,color='#286680',height=.6)\n                else:ax.plot(start,i,'|',color='#286680')")
s=s.replace("        ax.set_yticks(range(len(own))", "        horizon=max([1,e.clock]+[(r['end_ms'] if r['end_ms'] is not None else r['finish_ms'] if r['status']=='running' else r['arrival']) for r in own])\n        ax.set_xlim(0,horizon*1.05)\n        ax.set_yticks(range(len(own))")
p.write_text(s)
p=Path('README.md');s=p.read_text(encoding='utf-8').replace('grey hatch means waiting, blue means processing.','grey hatch means waiting, filled blue means elapsed processing and outlined blue means remaining planned processing.');p.write_text(s,encoding='utf-8')
p=Path('.build/browser.mjs');s=p.read_text().replace('width:1500,height:1050','width:1500,height:2300');p.write_text(s)
