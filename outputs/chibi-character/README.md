# 参考立绘 Q 版角色

打开 `chibi_character_editable.blend`，选择 `Chibi_Reference_Character` 场景。主集合 `Character_Editable` 下包含头脸、头发、服装、四肢四个分组。此模型用于展示、摆放与继续编辑；未制作骨骼绑定。

基于用户提供的同一角色正面与侧面制作完整三维体积，模型约 1.98 单位高、约两头身。头脸、刘海、左右侧发、七束后发、裙身与褶边、袖子、白领、蝴蝶结、手腿、袜鞋均可单独编辑。发束保留细分修改器，领口保留厚度修改器，裙身保留倒角。

眼睛、眼线、眉毛与嘴巴是贴合脸部的薄片/曲线；藏蓝裙格纹是共享坐标的程序材质。所有材质均包含在 blend 文件中，没有外部图片依赖。预览文件为 front.png、side.png、back.png、three_quarter.png。

## 推定补全与近似
- 后发的七束排列、背面分缝、后领和腰带闭合方式依据正侧面合理补全。
- 背面格纹、裙摆背部褶皱和鞋子隐藏部分为推定设计。
- 简化了手指、袜口、鞋带和领口装饰；发束与脸型为插画的三维近似，并非精确扫描。
- 未制作衣服内部身体结构、骨骼、表情形变或动画。

## 生成过程
使用 Blender 5.2，所有脚本放在同一目录，依次执行：

```bash
blender -b --python build.py
blender -b stage1_blockout.blend --python details.py
blender -b chibi_character_editable.blend --python polish.py
blender -b chibi_character_editable.blend --python finalize.py
```

脚本会新建角色场景；不修改既有文件。后两个脚本是顺序执行的一次性修整步骤，不要在同一结果文件上重复运行。

## 检查
已检查灰模正面/侧面、角色细节与最终四视角。自动网格检查通过，0 错误，约 92,360 个评估后三角面。保留头与发帽内部 2 对隐藏背向接触三角面，便于独立编辑；详见 qa.json。本文件是渲染/编辑资产，不是已合并的打印模型。
