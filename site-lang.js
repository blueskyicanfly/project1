/* ============================================================
   site-lang.js —— 全站中英切换（所有页面共用）
   ------------------------------------------------------------
   用法（每个 HTML 只需两步）：
     1) </body> 前引入：  <script src="site-lang.js"></script>
     2) 放一个按钮：      <div class="lang"><button data-lang="zh">中文</button>
                             <button data-lang="en">EN</button></div>
   没有放按钮的页面也会自动注入一个右上角悬浮按钮，无需手写 HTML。

   翻译机制：
     · 启动时扫描 body 内所有文本节点，存下原文；切英文按 DICT 替换，
       切中文还原原文。新增中文文案会被自动登记（无英文则保持中文，不会空白）。
     · 属性类文字（title / alt / placeholder）走 ATTRS 字典。
     · Canvas 里的文字不在 DOM 里，扫不到；页面自己用 tr('中','英') 取词。

   ⚠️ 新增文案后要补词典：DICT（网页文字）/ ATTRS（属性）/ CANVAS（画布文字）。
   ============================================================ */
(function () {
  'use strict';

  /* ---------- 词条字典：中文原文 -> 英文 ---------- */
  const DICT = {
    /* ===== 通用 / 导航 ===== */
    '物理实验室': 'Physics Lab',
    '· 物理实验室': '· Physics Lab',
    '模拟': 'Simulations',
    '解题': 'Problems',
    '动画': 'Animations',
    '视频': 'Videos',
    'GitHub 源码仓库': 'Source on GitHub',

    /* ===== 首页 Hero ===== */
    '物理教学资源': 'Interactive Physics · Teaching Resources',
    /* 首页 h1 下的英文副标题：中文页 DOM 里根本没有这段文字，
       所以用一个带 @@ 标记的条目存放，页面脚本自己取用（扫描器会跳过 @@ 开头的 key） */
    '@@hero-sub': 'Simulation · Problem-solving · Animation · Video',
    '可交互的物理模拟、题目讲解与演示动画。每一个都可以直接在浏览器里运行，拖动参数即时看到结果——不用装软件，手机也能用。':
      'Interactive simulations, worked solutions and demonstration animations. Everything runs directly in the browser — drag a parameter and see the result instantly. No software to install, works on phones too.',
    '个资源已上线': 'resources published',
    '个分类栏目': 'categories',
    '浏览直器接运行': 'run in the browser',
    '浏览器直接运行': 'run in the browser',

    /* ===== 首页：分类标题与说明 ===== */
    /* 中文页只显示纯中文小标题，英文后缀 .en-name 由 CSS 默认隐藏；
       切到 EN 时页面脚本把 <html lang> 改为 en，CSS 让 .en-name 显示出来，
       同时下面两条把 h2 换成英文，避免出现「Simulations Simulations」 */
    '交互模拟': 'Interactive Simulations',
    '可动手调参数的物理模型。改一个数值，结果当场重算——最适合用来建立直觉、验证守恒律。':
      'Hands-on physical models. Change one number and everything recalculates — ideal for building intuition and checking conservation laws.',
    '题目讲解': 'Worked Problems',
    '典型题目的分步解析：受力分析、方程建立、结果讨论。会做成可展开步骤的形式，而不是只给答案。':
      'Step-by-step solutions: free-body analysis, setting up equations, discussing results. Shown as expandable steps rather than just an answer.',
    '演示动画': 'Demonstration Animations',
    '用动画把抽象概念可视化：过程拆解、慢放、逐步叠加。偏「看懂原理」，不含交互调参。':
      'Animations that visualise abstract ideas: breaking a process down, slow motion, step-by-step overlays. Focused on understanding, not parameter tweaking.',
    '视频实验': 'Experiment Videos',
    '实拍或录屏的实验视频、解题讲解视频，配文字要点与关键时间点索引。':
      'Recorded experiments and solution walkthroughs, with written key points and timestamps.',

    /* ===== 首页：卡片 ===== */
    '斜面模型机械能守恒': 'Object on Incline · Mechanical Energy Conservation',
    '调高度与底边长，看末速度只取决于高度、与倾角无关。含速度/加速度矢量、实时能量对照表与数值积分验证。':
      'Adjust height and base length to see that the final speed depends only on height, not on angle. Includes velocity/acceleration vectors, a live energy table and numeric-integration checks.',
    '力学': 'Mechanics',
    '机械能守恒': 'Energy conservation',
    '打开 →': 'Open →',
    '即将上线': 'Coming soon',
    '计划中': 'Planned',
    '碰撞与动量守恒': 'Collisions & Momentum Conservation',
    '两球正碰 / 斜碰，弹性与非弹性对比，动量守恒但动能不一定守恒。':
      'Head-on and oblique collisions, elastic vs inelastic: momentum is conserved but kinetic energy need not be.',
    '斜面类题目精解': 'Incline Problems, Worked Through',
    '含摩擦、连接体、斜面自身运动等常见变式的受力分析与解题套路。':
      'Free-body analysis and solution patterns for common variants: friction, connected bodies, a moving wedge.',
    '运动学图像逐步生成': 'Kinematic Graphs Built Step by Step',
    'x-t、v-t、a-t 三张图同步生长，看清斜率与面积的对应关系。':
      'x-t, v-t and a-t graphs grow together so the link between slope and area becomes visible.',
    '运动学': 'Kinematics',
    '实验视频合集': 'Experiment Video Collection',
    '课堂演示与家庭小实验，附测量数据处理与误差分析。':
      'Classroom demos and simple home experiments, with data handling and error analysis.',
    '实验': 'Experiments',

    /* ===== 页脚 ===== */
    '所有页面为纯静态 HTML，无外部依赖，可离线打开。新资源发布后会自动出现在对应栏目。':
      'All pages are plain static HTML with no external dependencies and work offline. New resources appear automatically in the right category.',
    /* 页脚：「物理实验室」在 <span> 里单独翻；英文后缀在隐藏 span 里，
       EN 下由 CSS 显示，内容就是字面「· Physics Lab」，无需词条 */

    /* ===== 模拟器：控件与读数 ===== */
    '光滑斜面（无摩擦）· 可实时调高度 h 与底边长 b · 黄色箭头 = 瞬时速度矢量':
      'Frictionless incline · adjust height h and base b live · yellow arrow = instantaneous velocity',
    '斜面高度 h（米）': 'Incline height h (m)',
    '斜面底边长 b（米）': 'Incline base b (m)',
    '物体质量 m（千克）': 'Mass m (kg)',
    '释放小车': 'Release cart',
    '暂停 / 继续': 'Pause / Resume',
    '复位': 'Reset',
    '底端速度 v': 'Speed at bottom v',
    '动能 Ek = ½mv²': 'Kinetic energy Ek = \u00bdmv\u00b2',
    '斜面高度 h': 'Incline height h',
    '斜面底边 b': 'Incline base b',
    '斜面长度 L（斜边）': 'Slope length L (hypotenuse)',
    '倾角 θ': 'Angle \u03b8',
    '加速度 a': 'Acceleration a',
    '下滑时间 t': 'Travel time t',
    '实时读数（小车运动过程中）': 'Live readings (during motion)',
    '物理量': 'Quantity',
    '当前值': 'Current',
    '底端时': 'At bottom',
    '已下滑距离 s': 'Distance travelled s',
    '剩余高度 Δh': 'Remaining height \u0394h',
    '速度 v': 'Speed v',
    '减少的重力势能 mgΔh': 'Lost GPE mg\u0394h',
    '机械能合计 Ek + 剩余Ep': 'Total energy Ek + PE',
    '最右两列若始终相等（Ek 增加量 = Ep 减少量），即验证了机械能守恒。':
      'If the last two columns stay equal (gain in Ek = loss in PE), mechanical energy is conserved.',
    '核心验证：末速度只取决于高度，与倾角无关': 'Key check: final speed depends only on height, not on angle',
    '高度 h': 'Height h',
    '底边 b': 'Base b',
    '理论 v=√(2gh)': 'Theory v=\u221a(2gh)',
    '模拟 v（数值积分）': 'Simulated v (integration)',
    '偏差': 'Deviation',
    '很缓': 'Very gentle',
    '中等': 'Moderate',
    '45°附近': 'Near 45\u00b0',
    '较陡': 'Steep',
    '很陡': 'Very steep',
    '当前理论末速度 √(2gh) =': 'Theoretical final speed \u221a(2gh) = ',
    '当前数值积分结果 =': 'Numeric-integration result = ',
    '慢动作': 'Slow motion',
    '动画速度（慢动作倍率）': 'Animation speed (slow-motion factor)',
    '动画放慢，物理数值不变': 'Animation slowed; physics values unchanged',
    '拖动改高度': 'drag to change height',
    '拖动改底边': 'drag to change base',
    '抓小车上下拖也改高度': 'grab the cart to drag height',

    /* ===== 模拟器：画布文字（Canvas 扫不到，页面用 tr() 取词）===== */
    '静止待释放': 'At rest \u2014 ready to release',
    '运动进行中…': 'Running\u2026',
    '已到达底端': 'Reached the bottom',
    '斜面高度': 'Incline height',
    '斜面底边': 'Incline base',
    '倾角': 'Angle',
  };

  /* 含 HTML 标签、必须整块替换的元素（按 id 索引） */
  const BLOCKS = {
    formulaBox: {
      zh: '下滑加速度 <code>a = g·sinθ</code>　沿斜面位移 <code>L = √(h² + b²)</code><br>'
        + '底端速度 <code>v = √(2gh)</code>　动能 <code>Ek = ½mv²</code>　减少的势能 <code>= mgh</code>',
      en: 'Acceleration <code>a = g\u00b7sin\u03b8</code> \u00b7 Distance along slope <code>L = \u221a(h\u00b2 + b\u00b2)</code><br>'
        + 'Speed at bottom <code>v = \u221a(2gh)</code> \u00b7 Kinetic energy <code>Ek = \u00bdmv\u00b2</code> \u00b7 Lost PE <code>= mgh</code>',
    },
    noteBox: {
      zh: '伽利略的结论：同一高度、不同倾角，末速度相同；但倾角越陡用时越短。 '
        + '「模拟」列是用 a = g·sinθ 做数值积分跑出来的结果，与理论公式对得上即证明模型正确。',
      en: "Galileo's result: at the same height the final speed is the same for every angle; a steeper slope simply takes less time. "
        + 'The "Simulated" column comes from numerically integrating a = g\u00b7sin\u03b8; agreement with the formula validates the model.',
    },
  };

  /* 属性类文字：img alt / title / placeholder */
  const ATTRS = {
    '斜面模型模拟截图：小车沿斜面下滑，带速度与加速度矢量箭头':
      'Screenshot of the Object on Incline simulation: a cart sliding down an incline with velocity and acceleration vectors',
  };

  /* 标题（<title>）按页面区分 */
  /* 标题：任意页面都按「含中文则翻」处理，不依赖精确匹配 */
  const TITLE_MAP = {
    '物理实验室': 'Physics Lab \u00b7 Interactive Physics Teaching Resources',
    '斜面模型机械能守恒': 'Object on Incline \u00b7 Mechanical Energy Conservation',
  };

  /* ---------- 状态 ---------- */
  const STORE_KEY = 'site-lang';
  let LANG = 'zh';
  try { LANG = localStorage.getItem(STORE_KEY) || 'zh'; } catch (e) {}

  const NODES = [];        // [文本节点, 当前中文形式]
  const ATTR_NODES = [];   // [元素, 属性名, 原值]
  /* 英文 -> 中文 反向表：页面脚本可能已在英文状态下重建内容，
     此时存下的“原文”是英文，切回中文靠它反查 */
  const EN2ZH = (function () {
    const m = Object.create(null);
    Object.keys(DICT).forEach(function (zh) {
      if (zh.charAt(0) === '@') return;
      const en = DICT[zh]; if (en && !m[en]) m[en] = zh;
    });
    return m;
  })();
  let origTitle = '';
  let ready = false;

  /* ---------- 对外接口 ---------- */
  function tr(s) { return LANG === 'en' && DICT[s] ? DICT[s] : s; }
  /* 暴露字典：页面需要取纯英文词条（如首页副标题）时用 SITE_DICT[key] */
  window.SITE_DICT = DICT;
  function getLang() { return LANG; }

  function syncButtons() {
    document.querySelectorAll('[data-lang]').forEach(function (b) {
      b.classList.toggle('on', b.getAttribute('data-lang') === LANG);
    });
  }

  /* 页面没放按钮时，自动注入一个右上角悬浮切换条 */
  function ensureSwitch() {
    if (document.querySelector('[data-lang]')) return;
    const box = document.createElement('div');
    box.className = 'lang-float';
    box.innerHTML = '<div class="lang"><button data-lang="zh">中文</button>'
      + '<button data-lang="en">EN</button></div>';
    document.body.appendChild(box);
  }

  function injectStyle() {
    if (document.getElementById('site-lang-style')) return;
    const css = [
      '.lang{display:inline-flex;border:1px solid #232e3a;border-radius:999px;overflow:hidden;background:#0b0e11;flex:none}',
      '.lang button{border:0;background:transparent;color:#8a97a6;padding:7px 15px;font-size:13px;',
      '  border-radius:0;cursor:pointer;font-family:inherit;line-height:1.4}',
      '.lang button.on{background:#4da3ff;color:#04121f;font-weight:600}',
      '.lang-float{position:fixed;top:14px;right:16px;z-index:9999;',
      '  background:rgba(8,11,16,.85);backdrop-filter:blur(8px);border-radius:999px;padding:3px}',
    ].join('\n');
    const s = document.createElement('style');
    s.id = 'site-lang-style';
    s.textContent = css;
    document.head.appendChild(s);
  }

  function applyLang() {
    /* 先让页面重建自己的动态内容（表格/canvas/整块文字），再扫描翻译。
       顺序不能反：否则新节点扫不到，或扫到的已是译文。*/
    document.dispatchEvent(new CustomEvent('langchange', { detail: { lang: LANG } }));
    scanDom();
    for (const [node, raw] of NODES) {
      if (LANG === 'zh') { node.nodeValue = raw; continue; }
      const key = raw.trim();
      const en = DICT[key];
      if (en && en !== key) {
        const lead = raw.match(/^\s*/)[0], tail = raw.match(/\s*$/)[0];
        node.nodeValue = lead + en + tail;
      }
    }
    for (const [el, attr, val] of ATTR_NODES) {
      el.setAttribute(attr, LANG === 'en' ? ATTRS[val] : val);
    }
    /* 图片随语言切换：<img data-lang-zh="a.jpg" data-lang-en="b.jpg"> */
    document.querySelectorAll('img[data-lang-en], img[data-lang-zh]').forEach(function (el) {
      if (!el.dataset.origSrc) el.dataset.origSrc = el.getAttribute('src');
      const pick = (LANG === 'en') ? el.dataset.langEn : el.dataset.langZh;
      const src = pick || el.dataset.origSrc;
      if (el.getAttribute('src') !== src) el.setAttribute('src', src);
      /* alt 也随语言走：双语图直接取 data-lang-*alt；
         否则先反查回中文原值再查 ATTRS，避免 EN 态扫到的英文 alt 切不回中文 */
      let altPick = (LANG === 'en') ? el.dataset.langEnAlt : el.dataset.langZhAlt;
      if (!altPick) {
        const cur = el.getAttribute('alt');
        const base = (LANG === 'zh') ? cur : (EN2ZH[(cur || '').trim()] || cur);
        altPick = (LANG === 'en' && ATTRS[base]) ? ATTRS[base] : base;
      }
      if (altPick && el.getAttribute('alt') !== altPick) el.setAttribute('alt', altPick);
    });

    Object.keys(BLOCKS).forEach(function (id) {
      const el = document.getElementById(id);
      if (!el) return;
      const b = BLOCKS[id];
      if (b.innerhtmlSafe) el.innerHTML = b[LANG];
      else el.textContent = b[LANG];
    });
    /* formulaBox 需要保留 <code> 标签，单独走 innerHTML */
    const fb = document.getElementById('formulaBox');
    if (fb && BLOCKS.formulaBox) fb.innerHTML = BLOCKS.formulaBox[LANG];

    /* 标题：记住首次见到的原文，切回中文时能还原 */
    /* 只在见到中文标题时记原文；若页面已在 EN 态（如跨页同步后直接打开），
       记下英文形式并反查回中文，保证切回 ZH 能还原 */
    if (!origTitle) {
      const t = document.title;
      origTitle = (LANG === 'zh' || !TITLE_MAP[t]) ? t : (EN2ZH[t] || t);
    }
    document.title = (LANG === 'en') ? (TITLE_MAP[origTitle] || origTitle) : origTitle;

    document.documentElement.lang = LANG === 'en' ? 'en' : 'zh-CN';
    syncButtons();
    /* 通知页面：需要重绘 canvas / 重建动态表格 */
  }

  function setLang(l) {
    if (LANG === l) return;
    LANG = l;
    try { localStorage.setItem(STORE_KEY, l); } catch (e) {}
    applyLang();   // applyLang 内部会先派发 langchange 让页面重建，再扫描
  }

  /* ---------- 启动 ---------- */
  function scanDom() {
    NODES.length = 0; ATTR_NODES.length = 0;
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      const raw = n.nodeValue;
      if (!raw.trim()) continue;
      /* '@@' 开头的是只供页面取用的纯英文词条，不参与扫描 */
      if (raw.trim().charAt(0) === '@') continue;
      const p = n.parentNode;
      if (p && (/^(script|style)$/i.test(p.tagName))) continue;
      let base = raw;
      if (LANG === 'zh') {
        /* 浏览器表单自动填充可能留着上次的英文译文：整段命中就换回中文 */
        if (EN2ZH[raw.trim()]) base = EN2ZH[raw.trim()];
        else {
          for (const en in EN2ZH) {
            if (en.length > 10 && raw.indexOf(en) !== -1) {
              base = raw.replace(en, EN2ZH[en]); break;
            }
          }
        }
      }
      NODES.push([n, base]);
    }
    document.querySelectorAll('[alt],[title],input[placeholder]').forEach(function (el) {
      ['alt', 'title', 'placeholder'].forEach(function (a) {
        const v = el.getAttribute(a);
        if (v && ATTRS[v]) ATTR_NODES.push([el, a, v]);
      });
    });
  }

  function boot() {
    if (ready) return;
    ready = true;
    injectStyle();
    ensureSwitch();
    document.addEventListener('click', function (e) {
      const b = e.target.closest && e.target.closest('[data-lang]');
      if (b) setLang(b.getAttribute('data-lang'));
    });
    applyLang();
  }

  /* 暴露给页面：tr() / getLang() / setLang() */
  window.SiteLang = { tr: tr, getLang: getLang, setLang: setLang };
  if (typeof window.tr !== 'function') window.tr = tr;

  /* 脚本写在 </body> 前：此刻 DOM 已就绪，直接同步启动。
     不能推迟到 DOMContentLoaded——否则页面脚本里的 tr() 会拿不到字典。*/
  if (document.body) {
    boot();
  } else {
    document.addEventListener('DOMContentLoaded', boot);
  }
})();
