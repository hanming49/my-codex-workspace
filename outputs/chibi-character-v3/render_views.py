import bpy
from pathlib import Path
R=Path(__file__).parent
s=bpy.data.scenes['Chibi_Reference_Character'];bpy.context.window.scene=s
for view in ['front','side','back','three_quarter']:
 bpy.data.objects['Studio_Ground'].hide_render=view!='three_quarter';s.camera=bpy.data.objects['Camera_'+view];s.render.filepath=str(R/(view+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['Camera_three_quarter'];bpy.data.objects['Studio_Ground'].hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_v3.blend'))
