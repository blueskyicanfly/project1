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
