import bpy,bmesh
from pathlib import Path
R=Path(__file__).parent;s=bpy.data.scenes['Chibi_Reference_Character'];bpy.context.window.scene=s;C=bpy.data.collections['Character_Editable']
groups={}
for name in ['01_Head_Face','02_Hair','03_Outfit','04_Limbs']:
 c=bpy.data.collections.new(name);C.children.link(c);groups[name]=c
for o in list(C.objects):
 if o.type=='MESH':
  if o.name.startswith('Hair_') and o.name!='Hair_Crown':
   for v in o.data.vertices:
    threshold=1.45 if 'BackLock' in o.name else 1.78
    t=max(0,min(1,(v.co.z-threshold)/.15));v.co.x*=1-.12*t;v.co.y*=1-.20*t
  bm=bmesh.new();bm.from_mesh(o.data)
  bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
  bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 name='02_Hair' if o.name.startswith('Hair_') else '04_Limbs' if o.name.startswith(('Leg','Hand','Thumb','Sock','Shoe')) else '01_Head_Face' if o.name.startswith(('Head','Neck','Eye','Ear','UpperLid','Brow','Mouth')) else '03_Outfit'
 C.objects.unlink(o);groups[name].objects.link(o)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_editable.blend'))
for view in ['front','side','back','three_quarter']:
 bpy.data.objects['Studio_Ground'].hide_render=view!='three_quarter';s.camera=bpy.data.objects['Camera_'+view];s.render.filepath=str(R/(view+'.png'));bpy.ops.render.render(write_still=True)
s.camera=bpy.data.objects['Camera_three_quarter'];bpy.data.objects['Studio_Ground'].hide_render=False;bpy.ops.wm.save_as_mainfile(filepath=str(R/'chibi_character_editable.blend'))
