from PIL import Image,ImageDraw
from pathlib import Path
files=list(Path('.build').glob('report-*.png'))+list(Path('.build').glob('slide-*.png'))
out=Image.new('RGB',(1500,((len(files)+4)//5)*430),'#ddd')
for i,p in enumerate(files):
 im=Image.open(p);im.thumbnail((292,400));x=i%5*300;y=i//5*430;out.paste(im,(x,y+20));ImageDraw.Draw(out).text((x,y),p.name,fill='black')
out.save('.build/contact.png')
