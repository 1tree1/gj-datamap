from PIL import Image
from pathlib import Path
R=Path(r'C:\Users\OFFICE\Desktop\9_도시')
O=R/'work/20261010_nexus_front/build/assets'
A=R/'work/20261008_presentation_front/assets'
for y in [2015,2021,2025]:
    im=Image.open(A/f'hist/ortho_{y}_F1.jpg')
    im.crop((0,350,1800,2150)).save(O/f'ortho_{y}_square.jpg',quality=95)
im=Image.open(A/'charts/ortho_2025_F1_gray.jpg')
im.crop((0,150,1800,1800)).save(O/'site_frame.jpg',quality=95)
im.crop((225,150,1575,1800)).save(O/'site_frame_narrow.jpg',quality=95)
for sid,page,box,name in [('s06',22,(1138,46,1382,392),'heritage_survey')]:
    Image.open(O/f'{sid}_{page:02}.png').crop(box).save(O/f'{name}.png')
print('source crops prepared')
