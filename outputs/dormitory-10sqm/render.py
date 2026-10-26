import bpy
from pathlib import Path
R=Path(__file__).parent;s=bpy.context.scene
arch=bpy.data.collections['01_Architecture'];cut=[o for o in arch.objects if o.name.startswith(('Wall_South','Wall_West'))]
for cn,fn in [('Camera_Top','top_view'),('Camera_Perspective_A','perspective_a'),('Camera_Perspective_B','perspective_b')]:
 s.camera=bpy.data.objects[cn]
 for o in arch.objects:
  if o.name.startswith('Wall_'):o.hide_render=cn=='Camera_Top' or o in cut
 s.render.filepath=str(R/(fn+'.png'));bpy.ops.render.render(write_still=True)
for o in arch.objects:
 if o.name.startswith('Wall_'):o.hide_render=o in cut
s.camera=bpy.data.objects['Camera_Perspective_A'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'dormitory_10sqm.blend'))
