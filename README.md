# project1 · 物理实验室 Physics Lab

物理教学用的可交互网页资源集。纯静态 HTML + JavaScript，无外部依赖，浏览器直接打开即可运行，手机同样可用。

**在线访问：** https://blueskyicanfly.github.io/project1/

## 目录结构

| 文件 | 说明 |
|---|---|
| `index.html` | 首页导航，按四个分类汇总所有资源 |
| `incline-energy.html` | Object on Incline · 斜面模型机械能守恒模拟 |
| `site-lang.js` | **全站共用的中英切换引擎**（所有页面都要引入） |
| `thumbnails/` | 缩略图，每种语言一份：`xxx-zh.jpg` / `xxx-en.jpg` |
| `tools/` | 辅助脚本：截图生成、语言切换自动化测试 |

## 中英切换怎么用

每个页面只需两步（新页面复制这段即可）：

```html
<!-- 1) 放一个切换按钮（可选；不写则自动注入右上角悬浮按钮） -->
<div class="lang">
  <button data-lang="zh">中文</button><button data-lang="en">EN</button>
</div>

<!-- 2) 在 </body> 前引入引擎（必须放在页面自己的 <script> 之前） -->
<script src="site-lang.js"></script>
```

要点：
- **语言选择全站共享**，存在 `localStorage` 的 `site-lang` 键里。首页切了 EN，进任何子页面都是英文。
- 翻译靠自动扫描页面上的文本节点，按 `DICT` 字典替换；**没配英文的内容会保持中文**（不会变空白），所以漏配是安全的。
- 画布（Canvas）里的文字不在 DOM 里、扫不到，页面要用 `tr('中文')` 取词，并把词条写进 `DICT`。
- 含 HTML 标签的整块文案走 `BLOCKS`（按元素 id）；`alt`/`title` 走 `ATTRS`；图片按语言换源用 `data-lang-zh` / `data-lang-en`。

## 新增一个页面后，怎么补翻译

1. 打开页面，切到 EN，看哪些地方还是中文；
2. 在 `site-lang.js` 的 `DICT` 里加一行 `'中文原文': 'English'`（必须**一字不差**，包括空格和标点）；
3. 画布里的文字加进 `DICT` 即可（页面已用 `tr()` 取词）；
4. 跑一遍测试确认：
   ```bash
   CDP_PORT=9370 python3 tools/cdp_lang_test.py index.html /tmp/out
   CDP_PORT=9371 python3 tools/cdp_lang_test.py incline-energy.html /tmp/out
   ```
   输出里「残留中文节点」应只剩 `BUTTON: 中文`（那是切换按钮本身，属正常）。

## 分类规划

1. **交互模拟 Simulations** — 可拖参数即时重算的物理模型
2. **题目讲解 Problem-solving** — 分步解析：受力分析、建方程、讨论
3. **演示动画 Animations** — 抽象概念的可视化，偏「看懂原理」
4. **视频实验 Videos** — 实拍/录屏实验与讲解

## Object on Incline 的物理模型

光滑斜面（无摩擦）条件下：

```
倾角      θ = atan(h / b)
斜面长    L = √(h² + b²)
加速度    a = g·sinθ          （滚动模式为 5/7·g·sinθ）
底端速度  v = √(2gh)
```

核心结论：**末速度只取决于高度 h，与斜面倾角无关**（伽利略斜面实验的结论）。页面底部会自动扫描 5 种不同倾角、用数值积分独立复算，与解析解对比验证。

## 中英切换（全站共用）

所有页面共用同一个语言引擎 **`site-lang.js`**，右上角「中文 / EN」按钮切换，选择会记住并跨页面保持一致。

给新页面接上语言切换只需两步：

```html
<!-- 1) 导航栏里放按钮（放在 </body> 前的任意位置也可，脚本会自动补一个悬浮按钮）-->
<div class="lang">
  <button data-lang="zh">中文</button><button data-lang="en">EN</button>
</div>

<!-- 2) 页面底部引入引擎 -->
<script src="site-lang.js"></script>
```

翻译词典都在 `site-lang.js` 里，分三类：

| 词典 | 覆盖范围 | 说明 |
|---|---|---|
| `DICT` | 网页正文文字 | key 必须与页面上的中文**一字不差**（含标点空格） |
| `ATTRS` | `title` / `alt` / `placeholder` 等属性 | |
| `TITLE_MAP` | 浏览器标签页标题 | |

新增中文文案后若没登记英文，页面会**保持显示中文**（不会变空白），并在浏览器控制台列出待补条目——这是故意设计的安全默认。

Canvas 里画出来的文字不在网页 DOM 中，扫不到；页面代码要用 `tr('斜面高度')` 取词，并把该词条加进 `DICT`。

## 如何新增一个资源

1. 把新的 `.html` 文件放进仓库根目录
2. 生成双语缩略图（中英各一张，会自动切语言并冻结动画）：
   ```bash
   CDP_PORT=9380 python3 tools/gen_thumbs.py 名字.html /tmp/th
   # 得到 /tmp/th_zh.png 与 /tmp/th_en.png，再裁成 thumbnails/名字-zh.jpg、名字-en.jpg
   ```
3. 在 `index.html` 对应的分类里，把占位卡（`class="card soon"`）换成真实链接卡：
   ```html
   <a class="card" href="./名字.html">
     <div class="thumb"><img src="thumbnails/名字-zh.jpg"
          data-lang-zh="thumbnails/名字-zh.jpg" data-lang-en="thumbnails/名字-en.jpg"
          alt="..."></div>
     ...
   </a>
   ```
4. `git add -A && git commit -m "新增 ..." && git push`，约 1–2 分钟后 Pages 自动更新
