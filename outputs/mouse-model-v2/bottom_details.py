# Executed in mouse_build.py stage 3, before global placement.
# Photo-guided external underside, no invented internal mechanism.
import bmesh
base=bpy.data.materials['M_WarmWhite_Lower']
buttonmat=bpy.data.materials['M_TopButton']
dark=bpy.data.materials['M_Seams_Dark']
sole=mat('M_Underside_Ivory',(.70,.69,.63),.56)
feet=mat('M_PTFE_Skates',(.79,.78,.72),.30)
ink=mat('M_Label_Ink',(.025,.030,.028),.75)
metal=mat('M_Sensor_Metal',(.20,.25,.25),.25,.65)
lensmat=mat('M_Sensor_Lens',(.03,.09,.10),.13,.35)

def smooth_poly(poly,n=2):
    for _ in range(n):
        poly=[v for a,b in zip(poly,poly[1:]+poly[:1]) for v in [(a[0]*.75+b[0]*.25,a[1]*.75+b[1]*.25),(a[0]*.25+b[0]*.75,a[1]*.25+b[1]*.75)]]
    return poly

def plate(name,poly,zlo,zhi,material,bevel=.001):
    n=len(poly);v=[(x,y,z) for z in (zlo,zhi) for x,y in poly]
    f=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    ob=link_mesh(name,v,f,DETAILS,material)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
    for po in ob.data.polygons:po.use_smooth=len(po.vertices)==4
    if bevel:
        be=ob.modifiers.new('Rounded moulded edges','BEVEL');be.width=bevel;be.segments=3
        ob.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL')
    return ob

def rrpoly(cx,cy,hx,hy,r):
    pts=[]
    for x,y,a in [(hx-r,hy-r,0),(-hx+r,hy-r,90),(-hx+r,-hy+r,180),(hx-r,-hy+r,270)]:
        for k in range(9):
            t=math.radians(a+90*k/8);pts.append((cx+x+r*math.cos(t),cy+y+r*math.sin(t)))
    return pts

# Keys on the side seen in the newly supplied front-left / rear-right profile.
# Positive X is explicitly designated the photographed button side in this file.
for idx,(yy,zz) in enumerate([(-.135,.124),(.060,.137)],1):
    ratio=(zz-bottom(yy))/(h(yy)-bottom(yy))
    co=2*ratio-1 if ratio>=.5 else math.sqrt(2*ratio)-1
    sn=math.sqrt(1-co*co)
    xx=w(yy)*(sn if co>=0 else sn**.25)
    yz=rrpoly(yy,zz,.081,.022,.014)
    yz=[(y+.20*(z-zz),z) for y,z in yz]
    for label,depth,scale,material in [('Pocket',.003,1.12,dark),('Cap',.017,1,buttonmat)]:
        verts=[]; n=len(yz)
        for x,r in [(xx-(.007 if label=='Pocket' else .005),scale),(xx+depth-.004,scale),(xx+depth,scale*.86)]:
            verts.extend((x,yy+(y-yy)*r,zz+(z-zz)*r) for y,z in yz)
        faces=[tuple(reversed(range(n)))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(2) for i in range(n)]
        faces.append(tuple(range(2*n,3*n)))
        ob=link_mesh(f'SM_PhotoLeftSideKey_{idx}_{label}',verts,faces,PARTS,material)
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
        ob.modifiers.new('Key weighted normals','WEIGHTED_NORMAL')

# Thin perimeter pan and rim, following the waisted outline.
outline=[(w(-.497+i*.994/100)*.98,-.497+i*.994/100) for i in range(101)]
outline+= [(-x,y) for x,y in reversed(outline)]
plate('SM_Base_Perimeter_DarkLip',[(x*1.006,y*1.008) for x,y in outline],.018,.031,dark,.002)
plate('SM_Base_Editable_Underside',[(x*.986,y*.996) for x,y in outline],.016,.035,sole,.002)
# PTFE pads: broad front pad, two curved rear pads.
front=smooth_poly([(-.235,-.365),(-.235,-.435),(-.155,-.480),(0,-.491),(.155,-.480),(.235,-.435),(.235,-.365)],3)
plate('SM_Front_Skate_Recess',front,.013,.017,base)
plate('SM_Front_PTFE_Skate',[(x*.98,(y+.42)*.95-.42) for x,y in front],.004,.014,feet)
left=smooth_poly([(-.264,.205),(-.202,.203),(-.105,.300),(-.103,.435),(-.14,.454),(-.222,.395),(-.267,.302)],3)
for sg,label in [(1,'Left'),(-1,'Right')]:
    poly=[(x*sg,y) for x,y in left]
    plate('SM_Rear_'+label+'_Skate_Recess',poly,.013,.017,base)
    cx=-.185*sg;cy=.325
    plate('SM_Rear_'+label+'_PTFE_Skate',[(cx+(x-cx)*.95,cy+(y-cy)*.97) for x,y in poly],.004,.014,feet)

# Nameplate inset, with editable typography, not a photograph pasted over the body.
plate('SM_Nameplate_Inset',rrpoly(0,-.205,.226,.137,.025),.0135,.017,base)
def text_obj(name,body,x,y,size,material=ink):
    cu=bpy.data.curves.new(name,'FONT');cu.body=body;cu.size=size;cu.extrude=0;cu.space_character=1.05
    ob=bpy.data.objects.new(name,cu);DETAILS.objects.link(ob);cu.materials.append(material)
    ob.location=(x,y,.0128);ob.rotation_euler=(math.pi,0,0)
    return ob
text_obj('TXT_AULA','AULA',-.040,-.296,.046)
chfont=bpy.data.fonts.load('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
ob=text_obj('TXT_Model','无线鼠标   型号: SC525',-.040,-.262,.016);ob.data.font=chfont
ob=text_obj('TXT_Power','充电电压/电流: DC5V ⎓ 200mA',-.040,-.238,.012);ob.data.font=chfont
text_obj('TXT_Origin','Made in China',-.040,-.216,.014)
text_obj('TXT_Website','www.aulacn.com',-.040,-.194,.016)
text_obj('TXT_Recycle','CE   RECYCLABLE',-.040,-.167,.012)
for i in range(3):
    cylinder(f'SM_Base_Indicator_{i+1}',(-.172+i*.027,-.26,.013),.0045,.005,dark,DETAILS,32,axis='Z')
    cylinder(f'SM_Base_IndicatorRim_{i+1}',(-.172+i*.027,-.26,.0148),.006,.002,sole,DETAILS,32,axis='Z')
cylinder('SM_Base_RoundButton_Rim',(-.147,-.198,.012),.031,.007,feet,DETAILS,64,axis='Z')
cylinder('SM_Base_RoundButton',(-.147,-.198,.008),.024,.006,sole,DETAILS,64,axis='Z')

# Central textured field and receiver door.
field=smooth_poly([(-.228,-.059),(.228,-.059),(.234,.24),(.083,.364),(-.083,.364),(-.234,.24)],2)
plate('SM_DiagonalGrip_Field',field,.014,.016,sole)
# Shallow moulded diagonal lines, trimmed around sensor, switch, receiver door.
for i in range(-35,45):
    c=i*.012; pts=[]
    for j in range(180):
        y=-.05+j*.385/179;x=c+.72*y
        inside=abs(x)<(.222 if y<.22 else .222-(y-.22)*1.25)
        excluded=(abs(x)<.064 and -.072<y<.11) or (-.193<x<-.101 and .028<y<.145) or (abs(x)<.136 and .20<y<.33)
        if inside and not excluded:pts.append((x,y,.0136))
        elif pts:
            if len(pts)>1:curve(f'CRV_Base_Ridge_{i}_{j}',pts,base,.00035,DETAILS)
            pts=[]
    if len(pts)>1:curve(f'CRV_Base_Ridge_{i}_End',pts,base,.00035,DETAILS)

# Oval sensor opening has a genuine cut in the base pan; inset dark well + separate optical pieces.
sensorpoly=rrpoly(0,.018,.037,.062,.032)
cut=plate('CONSTRUCTION_SensorCut',sensorpoly,.008,.065,dark,0)
cut.hide_render=True;cut.hide_set(True)
for name in ['SM_Base_Editable_Underside','SM_Base_Perimeter_DarkLip','SM_DiagonalGrip_Field']:
    ob=bpy.data.objects[name];bo=ob.modifiers.new('Sensor opening','BOOLEAN');bo.operation='DIFFERENCE';bo.object=cut;bo.solver='EXACT'
plate('SM_Sensor_DeepWell',sensorpoly,.029,.032,dark,.002)
curve('CRV_Sensor_IvoryRaisedRim',[(x,y,.012) for x,y in rrpoly(0,.018,.046,.072,.039)],feet,.004,DETAILS,True)
plate('SM_Sensor_OpticalModule',rrpoly(0,.018,.024,.048,.015),.026,.030,metal)
cylinder('SM_Sensor_Lens',(0,-.002,.024),.012,.006,lensmat,DETAILS,48,axis='Z')
plate('SM_Sensor_RectangularWindow',rrpoly(0,.043,.020,.011,.003),.023,.027,dark)
# Offset power slider.
plate('SM_PowerSwitch_Pocket',rrpoly(-.145,.086,.029,.047,.024),.010,.017,base)
plate('SM_PowerSwitch_Track',rrpoly(-.145,.086,.022,.039,.019),.008,.011,feet)
plate('SM_PowerSwitch_Slider',rrpoly(-.145,.067,.019,.019,.017),.0065,.012,sole)
for i in range(7):
    y=.053+i*.004;curve(f'CRV_Switch_Grip_{i}',[(-.157,y,.0061),(-.133,y+.006,.0061)],base,.0006,DETAILS)

hatch=smooth_poly([(-.083,.207),(.083,.207),(.137,.267),(.109,.300),(-.109,.300),(-.137,.267)],3)
plate('SM_Receiver_Door_Seam',hatch,.011,.0154,base)
plate('SM_Receiver_StorageDoor',[(x*.97,(y-.25)*.95+.25) for x,y in hatch],.009,.013,sole)
plate('SM_Receiver_LatchSlot',rrpoly(0,.306,.069,.004,.003),.007,.011,dark)
text_obj('TXT_USB_Hatch','USB',-.016,.259,.016,base)
# Replaceable QC label; no claim to transcribing unreadable holographic microprint.
cylinder('SM_QC_Sticker',(0,.402,.013),.047,.001,mat('M_QC_Silver',(.37,.40,.43),.30,.7),DETAILS,64,axis='Z')
ob=text_obj('TXT_QC','QC PASS',-.033,.405,.013,ink);ob.location.z=.0118
# Bottom camera uses front-at-top orientation, matching the supplied underside photo.
bpy.data.objects['Camera_Bottom'].rotation_euler.rotate_axis('Z',math.pi)
area('Bottom_Softbox',(-.3,-.3,-1.2),(0,0,0),100,(1.5,1.2))
bpy.data.objects['Bottom_Softbox'].hide_render=True
SCENE['side_orientation']='Positive X = photographed side with exactly two keys; opposite side has none.'
