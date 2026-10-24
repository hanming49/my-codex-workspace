import bpy,math,sys,runpy,json
from pathlib import Path
R=Path(__file__).parent;s=bpy.data.scenes['Chibi_Reference_Character'];bpy.context.window.scene=s;C=bpy.data.collections['Character_Editable']
for o in C.all_objects:
 if o.type=='MESH' and o.name.startswith('Hair_') and o.name!='Hair_Crown':
  m=o.modifiers.new('Editable_Hair_Smoothing','SUBSURF');m.levels=1;m.render_levels=1
 if o.type=='MESH' and (o.name.startswith('Eye_') or o.name.startswith('UpperLid')):
  for v in o.data.vertices:v.co.z=1.51+(v.co.z-1.51)*.78
# Eyes are reprojected after shortening so they remain on the curved face.
for o in C.all_objects:
 if o.type=='MESH' and o.name.startswith('Eye_'):
  offsets={'Outline':.005,'Ivory':.007,'Iris':.009,'Pupil':.010,'Glint':.012}
  off=next(val for key,val in offsets.items() if key in o.name)
  for v in o.data.vertices:
   x,z=v.co.x,v.co.z;v.co.y=-.345*math.sqrt(max(.03,1-(x/.49)**2-((z-1.49)/.435)**2))-off
# Plaid: blend projections according to face direction, preventing contour-like third-axis stripes.
m=bpy.data.materials['Dress_NavyPlaid'];ns=m.node_tree.nodes;ls=m.node_tree.links
seps=[n for n in ns if n.type=='SEPXYZ'];sep=seps[0]
less=[n for n in ns if n.type=='MATH' and n.operation=='LESS_THAN']
maxs=[n for n in ns if n.type=='MATH' and n.operation=='MAXIMUM']
g=ns.new('ShaderNodeNewGeometry');sp=ns.new('ShaderNodeSeparateXYZ');ls.new(g.outputs['Normal'],sp.inputs[0]);ab=ns.new('ShaderNodeMath');ab.operation='ABSOLUTE';ls.new(sp.outputs['X'],ab.inputs[0]);gt=ns.new('ShaderNodeMath');gt.operation='GREATER_THAN';gt.inputs[1].default_value=.7;ls.new(ab.outputs[0],gt.inputs[0]);mix=ns.new('ShaderNodeMixRGB');ls.new(gt.outputs[0],mix.inputs[0]);ls.new(less[0].outputs[0],mix.inputs[1]);ls.new(less[1].outputs[0],mix.inputs[2]);ls.new(mix.outputs[0],maxs[1].inputs[0]);ls.new(less[2].outputs[0],maxs[1].inputs[1])
for n in ns:
 if n.type=='MIX_RGB' and n!=mix:n.inputs[2].default_value=(.20,.22,.27,1)
for o in C.all_objects:
 if o.type=='MESH' and o.name.startswith(('Skirt_','Waist_','Torso_')):
  be=o.modifiers.new('Soft_Cloth_Edges','BEVEL');be.width=.004;be.segments=2
for o in bpy.data.collections['Presentation'].objects:
 if o.type in ['LIGHT','CAMERA']:o.hide_set(True)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_editable.blend'))
for view in ['front','side','back','three_quarter']:
 bpy.data.objects['Studio_Ground'].hide_render=view!='three_quarter';s.camera=bpy.data.objects['Camera_'+view];s.render.filepath=str(R/(view+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['Camera_three_quarter'];bpy.data.objects['Studio_Ground'].hide_render=False;bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_editable.blend'))
