import bpy,os
from pathlib import Path
ROOT=Path(__file__).resolve().parent
src=(ROOT/'mouse_build.py').read_text();exec(src[:src.index('if STAGE==1:')])
SCENE=bpy.data.scenes['Mouse_Product_Studio'];bpy.context.window.scene=SCENE
preview=os.environ.get('PREVIEW')=='1'
views=[('right_side','Camera_Right'),('rear','Camera_Rear'),('bottom','Camera_Bottom')] if preview else [('top','Camera_Top'),('left_side','Camera_Left'),('right_side','Camera_Right'),('front','Camera_Front'),('three_quarter','Camera_ThreeQuarter'),('rear','Camera_Rear'),('bottom','Camera_Bottom')]
for label,cam in views:
    res=((600,800) if label=='bottom' else (800,600)) if preview else ((1200,1600) if label=='bottom' else (1200,900))
    render(('check_' if preview else 'mouse_')+label+'.png',cam,res,16 if preview else 32)
SCENE.camera=bpy.data.objects['Camera_ThreeQuarter'];bpy.data.objects['Studio_Floor'].hide_render=False;bpy.data.objects['Bottom_Softbox'].hide_render=True
if not preview:bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'photo_mouse_editable.blend'))
