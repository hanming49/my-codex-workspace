# 鼠标照片参考模型

`photo_mouse_editable.blend` 使用 Blender 5.2.0 LTS 制作。打开后选择 `Mouse_Product_Studio` 场景；原有的小屋场景保存在同一文件中，没有被删除。鼠标位于独立的 `Mouse_Model` Collection，分为壳体、操作部件、细节和施工辅助对象。文件中预设了俯视、前视、左侧、右侧和三分之四视角相机。

## 比例与推测

- 将产品长度暂定为 **1.00 单位**。代码中的宽度参数为 **0.59**，高度参数为 **0.305**；这些是从五张照片估计的，尚未用实物尺寸校准。
- 可编辑底壳网格的测量包围盒约为 **0.584 × 1.000 × 0.281 单位**；装饰和按键略超出底壳。照片透视使这些值只适合用作比例起点。
- 鼠标底部、接口舌片深度、按键隐藏支点和标识细线属于依据可见照片作出的简化推测。
- 标识为独立曲线对象，可替换为更准确的矢量图。没有把整张照片投射到模型上。

## 可编辑结构

底壳由纵向轮廓环构成；掌托、左右按键和上侧壳为独立网格，保留 Solidify 修改器。接口通过底壳上的 Boolean 开口和独立的厚壁外框构成。滚轮、顶部按钮、两颗左侧键和标识也各自独立。右侧没有侧键。模型所有材质都是 Blender 内部材质，没有外部贴图需要打包。

## 展示图

- `mouse_top.png`：俯视
- `mouse_left_side.png`：左侧
- `mouse_right_side.png`：右侧
- `mouse_front.png`：正面
- `mouse_three_quarter.png`：三分之四视角

## 重新生成

在装有 Blender 5.2+ 的环境中，依次运行：

```bash
blender -b existing_scene.blend --python mouse_build.py -- --stage 1
blender -b mouse_stage1_grey.blend --python mouse_build.py -- --stage 2
blender -b mouse_stage2_parts.blend --python mouse_build.py -- --stage 3
```

没有现有场景时，第一条可改成 `blender -b --python mouse_build.py -- --stage 1`。在脚本开头修改 `LENGTH`、`WIDTH`、`HEIGHT` 和纵向轮廓控制点后，可以重新生成。当前模型的阶段文件也保存在本地工作目录，正式交付以最终 `.blend` 为准。

质量检查使用 `blender-asset-qa` 的 render 配置：最终版 **18 个网格、31,770 个三角面、0 个错误，最低点 Z=0**。剩余提示来自部分隐藏的贴合面和中央装饰条分段网格的两个重复顶点，渲染中未见闪烁。
