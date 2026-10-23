# AULA SC525 鼠标 · 照片重建修订版 V2

本版依据补充的侧视、后视与底部照片修订。原版文件保留在 `outputs/mouse-model/`；本目录为新版本。

## 本次修改
- 重建连续的掌托—侧面曲面，修复旧版掌托仅覆盖半边的问题。
- 调整背部最高点、前部上升曲线和尾部下降；侧壳分界前段抬升、中段较高、后段下落至底缘。
- 照片所示侧面增加两个独立的圆角侧键及深色边缘；另一面不复制侧键。文件坐标 +X 为有键面。
- 调整滚轮嵌入、开口深度和中央装饰件，保留布尔修改器。
- 底部新增前脚贴、两个后脚贴、传感器凹槽与镜片、电源滑块、圆形按钮、三个指示孔、斜向纹理、接收器仓盖和铭牌。
- 蜘蛛标识改为贴合曲面的独立薄层几何，仍是照片手工近似，可单独替换。
- 保留已有小屋场景；鼠标位于 `Mouse_Product_Studio` 场景的 `Mouse_Model` 集合。

## 打开与编辑
打开 `photo_mouse_editable_v2.blend`。若进入其他场景，切换到 `Mouse_Product_Studio`。
选中 `Mouse_Dimensions_Edit_Properties`，在自定义属性中修改 `length / width / height`，所有鼠标零件随之调整。默认主体长宽高约 **1 : 0.59 : 0.335**，尚未实测；接口等外凸件会使包围盒略大。
按键、掌托、底壳、滚轮、侧键、接口、底部零件与标识保持独立可编辑。灯和相机在视口中隐藏，避免遮挡模型；仍可正常渲染。

## 图片
- `mouse_right_side.png`：有侧键面，前端朝左，与新侧视照片方向对应。
- `mouse_left_side.png`：无侧键面。
- `mouse_rear.png`：后视。
- `mouse_bottom.png`：底视，前端朝上。
- `mouse_top.png`、`mouse_front.png`、`mouse_three_quarter.png`：其余产品视图。

## 重新生成
需要 Blender 5.2，以下脚本保持同一目录。`bottom_details.py`、`refine.py` 是主脚本调用的模块。

```bash
blender -b existing_scene.blend --python mouse_build.py -- --stage 1
blender -b mouse_stage1_grey.blend --python mouse_build.py -- --stage 2
blender -b mouse_stage2_parts.blend --python mouse_build.py -- --stage 3
```

Stage 1 在已打开的文件中新增鼠标场景，不删除原场景。也可省略 `existing_scene.blend` 从默认场景开始。脚本的底部铭牌使用 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`，重新运行时可替换为本机中文字体路径；交付的 blend 已打包字体，无须安装此字体即可打开。模型无外部图片贴图依赖。

## 校准与限制
这是照片引导的可编辑近似模型，非扫描或工程 CAD。精确长宽高、最高点位置、按钮厚度、接缝宽度与接口尺寸仍需实测校准。底部外观按新增照片建立，槽深、传感器内部、仓盖内部和接口内部仍属推测。铭牌与 QC 字样为重建，未精确复刻字体、全部小字和全息效果；标识也不是原厂矢量稿。

QA 数值结果见 `qa.json`。针对产品渲染检查法线、重叠、悬空和退化面；内部壳层与底板的少量背向接触面保留，以保持各部件独立可编辑，不作为一体打印网格交付。

最终自动检查：通过，0 项错误；检查网格约 114,100 个三角面。剩余警告仅为内部背向接触面（完整底层壳体与外覆盖壳、底板与贴片/传感器内衬等），为独立编辑保留。另提供随机分件色与线框检查图。

掌托尾端已修正实体化后的法线自遮挡。可见掌托保留实体网格；原始带实体化修改器的控制壳保存在隐藏集合 `04_Construction` 的 `CONSTRUCTION_Palm_ControlSurface` 中，供继续修改厚度与重建使用。
