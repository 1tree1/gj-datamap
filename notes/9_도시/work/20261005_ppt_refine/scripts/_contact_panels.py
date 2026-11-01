from PIL import Image
import os
d = r'C:\Users\OFFICE\Desktop\9_도시\work\20261005_ppt_refine\assets'
names = ['plan_lots','plan_zones','plan_roads','plan_north','plan_center','plan_south']
ims = [Image.open(os.path.join(d, n + '.png')).convert('RGB') for n in names]
H = 900
rs = [im.resize((int(im.width * H / im.height), H)) for im in ims[:3]]
rs2 = [im.resize((int(im.width * H / im.height) // 1, H)) for im in ims[3:]]
W = sum(i.width for i in rs) + sum(i.width for i in rs2) + 20 * 6
sheet = Image.new('RGB', (W, H), 'white'); x = 0
for im in rs + rs2: sheet.paste(im, (x, 0)); x += im.width + 20
sheet.save(os.path.join(d, '_panels_contact.png')); print(sheet.size)
