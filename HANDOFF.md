# HANDOFF · 给下一个对话的交接摘要

> 用途：这是一个「上下文接力」文件。新开对话时只要说一句
> **「先读 ~/project1/HANDOFF.md」**，我就能完整接手，不需要你复述历史。
> 项目状态本身在 Git 里，这个文件只是省 token 用的索引。

## 环境（每次都要重新确认的事实）

- Open Terminal = Debian 13 (trixie) aarch64，用户 uid 1000
- 已装：git 2.47.3、node v22、python3（含 PIL）、`/usr/bin/chromium`、Noto CJK 中文字体
- **无浏览器 tab 可用**（`browser_action` 会报 HTTP 404 no tab）→ 要看页面效果只能用无头 Chromium 截图，或自写 CDP 脚本（见 `tools/`）
- `git config --global --list` 会卡在分页器 → 用 `git --no-pager ...` 或直接 `cat ~/.gitconfig`

## Git / GitHub

- 全局配置：`user.name=blueskyicanfly`、`user.email=blueskyicanfly@mail.com`、`init.defaultBranch=main`
- SSH key `~/.ssh/id_ed25519` 已加到 GitHub 并验证通过
- 仓库：`/home/user/project1`（目录名连写），remote = `git@github.com:blueskyicanfly/project1.git`
- **Pages 线上地址：https://blueskyicanfly.github.io/project1/**
- Pages CDN 缓存约 10 分钟（`max-age=600`），push 后不会立刻生效 → 验证前先 `sleep 45`

## 已完成并上线的东西

| 文件 | 内容 |
|---|---|
| `index.html` | 首页，四分类：交互模拟(蓝)/题目讲解(红)/演示动画(紫)/视频实验(绿)；粘性导航、Hero、卡片 hover、占位卡 `class="card soon"`；`nTotal` 由 JS 统计 `a.card` 数量 |
| `incline-energy.html` | 斜面模型机械能守恒模拟。h/b/m 滑块+数字框联动；**画布上可直接拖拽**：顶点黄点上下拖改 h、右下角黄点左右拖改 b（悬停变小手，与滑块实时联动）；**点画布空白处=释放/暂停切换**（按钮保留）；释放小车/暂停/复位/**慢动作×1→5→10** 四钮；画布上是**带轮子的小车**（已删「考虑滚动」选项与所有小球叙事，避免滞动误解）；Canvas 标注 h/b/θ、速度箭头沿法向抬离斜面线、实时读数表、Ek vs mgΔh 对照、底部扫 5 种倾角验证「末速度只取决于高度」。全文无「动量」字样 |
| `site-lang.js` | **全站共用中英切换引擎**（见下） |
| `thumbnails/` | 双语缩略图 `incline-energy-zh.jpg` / `-en.jpg`，由 CDP 真实渲染截图生成 |
| `tools/` | `cdp_lang_test.py`（点击 EN 并报告残留中文）、`gen_thumbs.py`（生成双语缩略图）、`test_cross_page.py`（跨页语言同步测试） |

（首页/模拟器已改「中文页纯中文」，见下；新提交信息以 `git log` 为准。）

## site-lang.js 的关键设计（改它之前必读）

- 每页只需：放 `[data-lang]` 按钮（不放则自动注入右上角悬浮按钮）+ 在 `</body>` 前 `<script src="site-lang.js">`，**且必须在页面自己的 script 之前**
- 语言存 `localStorage['site-lang']`，全站共享、跨页同步（已实测）
- 翻译靠扫描文本节点按 `DICT` 替换；**没配英文的内容保持中文**（不会空白），漏配是安全的
- Canvas 文字不在 DOM → 页面用 `tr('中文')` 取词，词条仍写进 `DICT`
- 含标签的整块文案走 `BLOCKS`（按元素 id）；`alt/title/placeholder` 走 `ATTRS`；图片换源用 `data-lang-zh` / `data-lang-en`，双语图的 alt 用 `data-lang-zh-alt` / `data-lang-en-alt`

### 中文页纯中文（最新一轮改动，改样式前先读）

- **原则：HTML 源文件只写中文**；英文只在 EN 态出现。做法三件套：
  1. 常驻英文后缀（`.en-name`、`.logo-en`）默认 `display:none`，`html[lang="en"]` 时显示（site-lang.js 会改 `<html lang>`）
  2. 只在 EN 出现的文字（如首页 h1 副标题）：DOM 里放空占位 `<span id="heroEn">`，页面脚本从 `window.SITE_DICT['@@hero-sub']` 取英文填入；`@@` 开头的 DICT key 不参与扫描
  3. 双语缩略图（canvas 文字烘进像素）：`thumbnails/incline-energy-{zh,en}.jpg` 由 `tools/gen_thumbs.py` 重新生成，改了模拟器页面文字后必须重跑并裁成 16:10
- `<title>` 也只写中文；英文标题靠 `TITLE_MAP`（key 已改成纯中文）。若页面在 EN 态直接打开，boot 会反查回中文存原文
- site-lang.js 的 scanDom：zh 态下若节点文本是某词条的英文译文（旧 localStorage 缓存导致），会先经 `EN2ZH` 反查回中文再登记，切 EN 才能命中

### 曾经踩过的坑（别再犯）

1. **boot 必须同步执行**，不能等 DOMContentLoaded——否则页面脚本里的 `tr()` 拿不到字典，中文会被缓存进动态内容
2. **每次切换要重新扫描 DOM**，否则 boot 之后生成的动态节点扫不到
3. **顺序必须是：先派发 `langchange` 让页面重建动态内容 → 再扫描翻译**；并有 EN→ZH 反向表，保证切回中文能还原
4. **字典 key 必须与页面文本一字不差**（含空格标点）。实例：页脚真实节点是 `' · Physics Lab  |  '`，前面带中点
5. `<th>理论 v=√(2gh)</th>` 里的 `<` 会被当标签开头 → 用 `&#40;` 转义
6. 截图时 `setLang()` 会触发重绘、动画循环会把小球跑到底端 → 需把 `requestAnimationFrame` 换成空函数冻结

## 验证方式（省 token，优先用它而不是反复截图）

```bash
# 双语审计：查「中文页有无可见英文」+「英文页有无残留中文」
CDP_PORT=9370 python3 tools/audit_bilingual.py index.html /tmp/out
# 模拟器交互冒烟测试（拖拽/点击释放/慢动作，14 项断言）
CDP_PORT=9395 python3 tools/smoke_interact.py
```
判据：ZH 态只剩 `BUTTON: EN`、`GitHub 源码仓库`、含 HTML/公式字母的合理保留；EN 态只剩 `BUTTON: 中文`。截图：`/tmp/shot_freeze.py <page> <prefix> <zh|en>`（全页+冻结动画）；缩略图用 `tools/gen_thumbs.py` + PIL 裁 16:10。
慢动作物理注意：×5 时同一段真实时间内滑行距离是 ×1 的 **1/25**（t² 效应），不是 1/5——写断言时用 25。拖 h 跟手换算：`newH=(y-padT)*pxPerM/availH`（pxPerM 随 h/b 自动缩放，不能线性直算）。

## 待办 / 下一步候选

首页已挂占位卡，按教学价值排序：
1. **碰撞与动量守恒模拟**（补上最初提的动量主题；斜面模型讲不了动量）
2. 单摆 / 弹簧振子（机械能的另一种呈现，与斜面模型对照）
3. 有摩擦的斜面版本（加 μ → 让学生看到「有摩擦时末速度才和倾角有关」，打破刚建立的结论，教学冲击力强）

## 用户偏好（沟通方式）

- 教师，非计算机专业：要大白话、明确定案、可复制的具体步骤；别罗列多方案让他选
- 操作前强调「先备份」会让他安心
- **只用简体中文或英文**，绝不夹杂繁体/日文等。他的输入常是语音转文字，会有同音错别字（如「鞋面」=斜面、「机能守恒」=机械能守恒、「手艺」=首页），先推断纠正再作答，不必刻意指出
- 关心 token 消耗：优先用脚本自动验证，少截图
