# project1 · 物理实验室 Physics Lab

物理教学用的可交互网页资源集。纯静态 HTML + JavaScript，无外部依赖，浏览器直接打开即可运行，手机同样可用。

**在线访问：** https://blueskyicanfly.github.io/project1/

## 目录结构

| 文件 | 说明 |
|---|---|
| `index.html` | 首页导航，按四个分类汇总所有资源 |
| `incline-energy.html` | Object on Incline · 斜面模型机械能守恒模拟 |
| `thumbnails/` | 各资源的缩略图（由无头 Chromium 真实渲染截图生成） |

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
2. 生成缩略图：
   ```bash
   chromium --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
     --window-size=1200,760 --screenshot=thumbnails/名字.png "file://$PWD/名字.html"
   ```
3. 在 `index.html` 对应的分类里，把占位卡（`class="card soon"`）换成真实链接卡：
   ```html
   <a class="card" href="./名字.html">
     <div class="thumb"><img src="thumbnails/名字.jpg" alt="..."></div>
     ...
   </a>
   ```
4. `git add -A && git commit -m "新增 ..." && git push`，约 1–2 分钟后 Pages 自动更新
