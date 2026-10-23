# Final geometric checks and adjustments, executed before placement / parenting.
for ob in list(DETAILS.objects):
    if ob.name.startswith('CRV_Logo_'):
        bpy.data.objects.remove(ob,do_unlink=True)
logo=bpy.data.materials['M_BlackGeometricLogo']
polys=[[(0,-.011),(-.010,0),(-.008,.022),(0,.038),(.008,.022),(.010,0)],
       [(-.004,-.012),(-.025,-.038),(-.053,-.040),(-.070,-.025),(-.058,-.009),(-.023,-.015),(-.021,-.021),(-.051,-.017),(-.058,-.026),(-.046,-.034),(-.030,-.033),(-.017,-.016)],
       [(-.012,-.007),(-.051,.0),(-.026,.034),(-.039,.006),(-.008,-.002)],
       [(-.007,.002),(-.029,.013),(-.012,.043),(-.020,.014),(-.004,.007)],
       [(-.006,-.012),(-.005,-.030),(-.001,-.017)]]
for i,poly in enumerate(polys):
    for sign in ([1] if i==0 else [-1,1]):
        vs=[(sign*x,.25+y,surface(sign*x,.25+y)+.0065) for x,y in poly]
        ob=link_mesh(f'SM_Replaceable_SpiderMark_{i}_{sign}',vs,[tuple(range(len(vs)))],DETAILS,logo)
        so=ob.modifiers.new('Thin printed mark','SOLIDIFY');so.thickness=.00025
tr=bpy.data.objects['SM_CentralGlossTrim_Editable']
tr.modifiers['Trim wall thickness'].thickness=.009
bm=bmesh.new();bm.from_mesh(tr.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.000001);bm.to_mesh(tr.data);bm.free()
# Clamp bevel amounts below half-thickness to avoid collapsed bevel rings.
for ob in MOUSE.all_objects:
    if ob.type=='MESH':
        for mod in ob.modifiers:
            if mod.type=='BEVEL':
                coords=[v.co for v in ob.data.vertices]
                extent=[max(v[i] for v in coords)-min(v[i] for v in coords) for i in range(3)]
                mod.width=min(mod.width,min(extent)*.20)
core=bpy.data.objects['SM_LowerBody_EditableRings']
bm=bmesh.new();bm.from_mesh(core.data)
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-7)
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
bm.to_mesh(core.data);bm.free()
# A rim is a ring, not a second overlapping solid bottom plate.
rim=bpy.data.objects['SM_Base_Perimeter_DarkLip']
for mod in list(rim.modifiers):
    if mod.type=='BOOLEAN':rim.modifiers.remove(mod)
outer=[(x*1.006,y*1.008) for x,y in outline];inner=[(x*.94,y*.97) for x,y in outline];nn=len(outer)
vv=[(x,y,z) for poly,z in [(outer,.018),(inner,.018),(inner,.031),(outer,.031)] for x,y in poly]
ff=[(j*nn+i,j*nn+(i+1)%nn,((j+1)%4)*nn+(i+1)%nn,((j+1)%4)*nn+i) for j in range(4) for i in range(nn)]
me=bpy.data.meshes.new('PerimeterRing_NoOverlappingPlate');me.from_pydata(vv,[],ff);me.materials.append(dark);rim.data=me
for ob in [rim,tr]:
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
for sign in [-1,1]:
    ob=bpy.data.objects[f'SM_Replaceable_SpiderMark_3_{sign}']
    for vert in ob.data.vertices:
        vert.co.x-=.007*sign;vert.co.z=surface(vert.co.x,vert.co.y)+.0065
palm=bpy.data.objects['SM_PalmShell_EditableGrid']
for mod in palm.modifiers:
    if mod.type=='SOLIDIFY':mod.thickness=.001;mod.thickness_clamp=.8
# One continuous trim surface with an actual wheel opening replaces touching patches.
vs=[];fs=[];ny=72;nx=20
for j in range(ny+1):
    y=-.482+j*.555/ny
    taper=1 if y<.028 else math.sqrt(max(.0001,1-((y-.028)/.047)**2))
    for k in range(nx+1):
        x=(k/nx*2-1)*.050*taper;vs.append((x,y,surface(x,y)+.012))
for j in range(ny):
    for k in range(nx):
        a=j*(nx+1)+k;fs.append((a,a+1,a+nx+2,a+nx+1))
me=bpy.data.meshes.new('Continuous_Trim_Control_Surface');me.from_pydata(vs,[],fs);me.materials.append(bpy.data.materials['M_CentralTrim_Gloss']);tr.data=me
for po in me.polygons:po.use_smooth=True
tr.modifiers['Trim wall thickness'].thickness=.010
bo=tr.modifiers.new('Editable wheel aperture','BOOLEAN');bo.operation='DIFFERENCE';bo.solver='EXACT';bo.object=bpy.data.objects['CONSTRUCTION_WheelCut']
# Close the tail pole explicitly instead of leaving a narrow open strip.
bm=bmesh.new();bm.from_mesh(palm.data)
for vert in bm.verts:
    if vert.co.y>.4999:vert.co=(0,.5,.025)
bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-7)
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(palm.data);bm.free()
# Keep the hidden core behind the closed palm tip, without coincident tail faces.
for vert in core.data.vertices:
    t=max(0,min(1,(vert.co.y-.46)/.04));t=t*t*(3-2*t)
    vert.co.y-=.0015*t;vert.co.z-=.001*t
# Conceal mechanical hinge roots fully below the rebuilt curved click surfaces.
for name in ['SM_LeftClick_HingeRoot','SM_RightClick_HingeRoot']:
    bpy.data.objects[name].location.z-=.005
# Stabilize tail-pole shading with the smooth limiting normal of the rear dome.
palm.data.update()
normals=[]
for vert in palm.data.vertices:
    n=vert.normal.copy();x,y,z=vert.co
    if y>.30:
        t=min(1,(y-.30)/.12);t=t*t*(3-2*t)
        target=Vector((x/(.30*.30),(y-.15)/(.35*.35),(z-.025)/(.31*.31))).normalized()
        n=(n*(1-t)+target*t).normalized()
    normals.append(tuple(n))
palm.data.normals_split_custom_set_from_vertices(normals)
# Preserve the editable thickness source, then set final shell normals after thickness.
control=palm.copy();control.data=palm.data.copy();control.name='CONSTRUCTION_Palm_ControlSurface';HELPERS.objects.link(control)
control.hide_render=True;control.hide_set(True)
outer_count=len(palm.data.vertices)
bpy.context.view_layer.objects.active=palm
for mod in list(palm.modifiers):
    if mod.type=='SOLIDIFY':
        mod.use_quality_normals=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
palm.data.update();normals=[]
for idx,vert in enumerate(palm.data.vertices):
    n=vert.normal.copy();x,y,z=vert.co
    if y>.30:
        t=min(1,(y-.30)/.12);t=t*t*(3-2*t)
        target=Vector((x/.09,(y-.15)/.1225,(z-.025)/.0961)).normalized()
        if idx>=outer_count:target=-target
        n=(n*(1-t)+target*t).normalized()
    normals.append(tuple(n))
palm.data.normals_split_custom_set_from_vertices(normals)
palm['edit_note']='Thickness applied to preserve tail shading. Original editable thickness source retained in 04_Construction / CONSTRUCTION_Palm_ControlSurface.'
