from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
paths=list(Path('.build').glob('report-*.png'))+list(Path('.build').glob('slide-*.png'))
out=Image.new('RGB',(1200,((len(paths)+3)//4)*420),'#dddddd')
for i,p in enumerate(paths):
    im=Image.open(p); im.thumbnail((290,390)); x=(i%4)*300;y=(i//4)*420;out.paste(im,(x,y+20));ImageDraw.Draw(out).text((x+5,y+3),p.name,fill='black')
out.save('.build/contact.png')
