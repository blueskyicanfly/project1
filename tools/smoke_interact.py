#!/usr/bin/env python3
"""模拟器交互冒烟测试：拖拽改 h/b、点画布释放/暂停、慢动作倍率。
用法: CDP_PORT=94xx python3 tools/smoke_interact.py
全部断言打印 PASS/FAIL，最后统计。
"""
import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit_bilingual import WS, start, wait_port

PORT = int(os.environ.get('CDP_PORT', '9395'))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
results = []

def check(name, ok, detail=''):
    results.append((name, bool(ok)))
    print(('PASS  ' if ok else 'FAIL  ') + name + ('  | ' + str(detail) if detail else ''))

def cdp_mouse(ws, ctype, x, y, button=None, click_count=None):
    """在页面坐标 (x,y) 派发真实鼠标事件（canvas 监听 pointer*，CDP 会合成）"""
    params = {"type": ctype, "x": x, "y": y}
    if button is not None: params["button"] = button
    if click_count is not None: params["clickCount"] = click_count
    ws.cmd("Input.dispatchMouseEvent", params)

def main():
    proc = start("/tmp/smoke-prof-%d" % PORT)
    try:
        wait_port()
        pages = json.load(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT))
        page = next(t for t in pages if t["type"] == "page")
        ws = WS(page["webSocketDebuggerUrl"])
        ws.cmd("Page.enable"); ws.cmd("Runtime.enable")
        ws.cmd("Emulation.setDeviceMetricsOverride", {"width":1200,"height":900,"deviceScaleFactor":1,"mobile":False})
        ws.cmd("Page.navigate", {"url": "file://" + ROOT + "/incline-energy.html"})
        time.sleep(2.2)

        # 冻结 rAF，手动控制 loop 步进（用页面自己的 loop 函数喂假时间戳）
        ws.ev("""window.__step = function(ms){
            window.__t = (window.__t||0) + ms;
            // 找到当前注册的循环不可行；直接手工按 loop 的积分逻辑不行。
            // 改为：不冻结 rAF，改用真实时间观察 —— 见下方各步。
        };""")

        def ev(e): return ws.ev(e)

        # ---- 1. 初始状态：小车在顶端、静止 ----
        s0 = ev("JSON.stringify({h:state.h,b:state.b,s:state.s,v:state.v,run:state.running})")
        check('初始 h=3 b=4 静止', s0 and '"h":3' in s0 and '"s":0' in s0 and '"run":false' in s0, s0)

        # ---- 2. 悬停到顶点手柄：cursor 变 grab，hoverHandle='h' ----
        pos = ev("JSON.stringify((function(){const g=geom();return {x:g.top.x,y:g.top.y,cx:cv.getBoundingClientRect().left,cy:cv.getBoundingClientRect().top,sc:cv.getBoundingClientRect().width/W}})())")
        P = json.loads(pos)
        px, py = P['cx'] + P['x']*P['sc'], P['cy'] + P['y']*P['sc']
        cdp_mouse(ws, "mouseMoved", px, py)
        time.sleep(0.3)
        hv = ev("hoverHandle")
        cur = ev("cv.style.cursor")
        # 默认 h=3,b=4 时小车停在坡顶、正好压住顶点黄点：命中优先判给小车（两者都是改 h，行为一致）
        check('悬停顶点/小车 hoverHandle∈{h,cart}', hv in ('h','cart'), hv)
        check('光标变小手 grab', cur == 'grab', cur)

        # ---- 3. 拖动顶点向下 120px：h 应变小（把坡往下拽塌）----
        h_before = json.loads(ev("JSON.stringify(state.h)"))
        cdp_mouse(ws, "mousePressed", px, py, button="left", click_count=1)
        for i in range(1, 7):
            cdp_mouse(ws, "mouseMoved", px, py + i*20, button="left")
            time.sleep(0.05)
        cdp_mouse(ws, "mouseReleased", px, py + 120, button="left")
        time.sleep(0.4)
        h_after = float(ev("state.h"))
        hnum = ev("document.getElementById('hNum').value")
        check('向下拽 h 变小（底边不变）', h_after < h_before, '%s -> %s' % (h_before, h_after))
        check('数字框与滑块联动', abs(float(hnum) - h_after) < 0.05, hnum)

        # ---- 4. 悬停右下角手柄并右拖：b 变大 ----
        pos2 = ev("JSON.stringify((function(){const g=geom();return {x:g.br.x,y:g.br.y,cx:cv.getBoundingClientRect().left,cy:cv.getBoundingClientRect().top,sc:cv.getBoundingClientRect().width/W}})())")
        P2 = json.loads(pos2)
        bx, by = P2['cx'] + P2['x']*P2['sc'], P2['cy'] + P2['y']*P2['sc'] - 3   # 手柄中心附近（文字在其右侧）
        cdp_mouse(ws, "mouseMoved", bx, by)
        time.sleep(0.3)
        check('悬停右下角 hoverHandle=b', ev("hoverHandle") == 'b', ev("hoverHandle"))
        b_before = float(ev("state.b"))
        cdp_mouse(ws, "mousePressed", bx, by, button="left", click_count=1)
        for i in range(1, 7):
            cdp_mouse(ws, "mouseMoved", bx + i*20, by, button="left")
            time.sleep(0.05)
        cdp_mouse(ws, "mouseReleased", bx + 120, by, button="left")
        time.sleep(0.4)
        b_after = float(ev("state.b"))
        check('向右拖 b 变大', b_after > b_before, '%s -> %s' % (b_before, b_after))

        # ---- 4b. 悬停小车本体：变小手，抓着上下拽同样改 h（往下拽 h 变小）----
        # 先把 h/b 复位到默认值再测抓车（前面拖拽已把 h 拉到极值、车贴住顶点手柄）
        ws.ev("setHB(3,4)")
        cp = ev("JSON.stringify((function(){const p=cartPos(state.s),r=cv.getBoundingClientRect();return {x:p.x,y:p.y,cx:r.left,cy:r.top,sc:r.width/W}})())")
        CP = json.loads(cp)
        ccx, ccy = CP['cx']+CP['x']*CP['sc'], CP['cy']+CP['y']*CP['sc']
        cdp_mouse(ws, "mouseMoved", ccx, ccy); time.sleep(0.3)
        check('悬停小车 hoverHandle=cart 且变小手', ev("hoverHandle")=='cart' and ev("cv.style.cursor")=='grab', (ev("hoverHandle"), ev("cv.style.cursor")))
        h_c_before = float(ev("state.h")); b_c_before = float(ev("state.b"))
        cdp_mouse(ws, "mousePressed", ccx, ccy, button="left", click_count=1)
        for i in range(1, 6):
            cdp_mouse(ws, "mouseMoved", ccx, ccy + i*25, button="left"); time.sleep(0.05)
        cdp_mouse(ws, "mouseReleased", ccx, ccy+125, button="left")
        time.sleep(0.4)
        h_c_after = float(ev("state.h")); b_c_after = float(ev("state.b"))
        check('抓小车往下拽 h 变小', h_c_after < h_c_before, '%s -> %s' % (h_c_before, h_c_after))
        check('抓小车拽时 b 不变', abs(b_c_after-b_c_before) < 1e-6, (b_c_before, b_c_after))

        # ---- 4c. 图形居中：三角形包围盒中心 ≈ 画布中心 ----
        ctr = ev("JSON.stringify((function(){const g=geom();return {cx:(g.top.x+g.br.x)/2, cy:(g.top.y+g.groundY)/2, W:W, H:H}})())")
        C = json.loads(ctr)
        check('三角形中心≈画布中心', abs(C['cx']-C['W']/2)<2 and abs(C['cy']-C['H']/2)<2, (round(C['cx']),round(C['W']/2),round(C['cy']),round(C['H']/2)))

        # ---- 5. 点画布空白处 = 释放；再点 = 暂停 ----
        cx0, cy0 = P2['cx'] + 60*P2['sc'], P2['cy'] + 60*P2['sc']   # 画布左上空白区
        cdp_mouse(ws, "mouseMoved", cx0, cy0); time.sleep(0.2)
        cdp_mouse(ws, "mousePressed", cx0, cy0, button="left", click_count=1)
        cdp_mouse(ws, "mouseReleased", cx0, cy0, button="left")
        time.sleep(0.8)
        st_run = json.loads(ev("JSON.stringify({run:state.running,v:state.v})"))
        check('点画布=释放（running=true 且已加速）', st_run['run'] and st_run['v'] > 0, st_run)
        v1 = st_run['v']
        time.sleep(0.6)
        cdp_mouse(ws, "mousePressed", cx0, cy0, button="left", click_count=1)
        cdp_mouse(ws, "mouseReleased", cx0, cy0, button="left")
        time.sleep(0.3)
        vA = float(ev("state.v"))
        time.sleep(0.8)
        vB = float(ev("state.v"))
        check('再点画布=暂停（速度不再变化）', abs(vA-vB) < 1e-9, (vA, vB))

        # 第三次点 = 继续：小车从停住处接着加速，位置不清零
        s_paused = float(ev("state.s"))
        HPT = json.loads(ws.ev("JSON.stringify((function(){const r=cv.getBoundingClientRect();return {x:r.left+r.width*0.85,y:r.top+r.height*0.12}})())"))
        cdp_mouse(ws, "mousePressed", HPT['x'], HPT['y'], button="left", click_count=1)
        cdp_mouse(ws, "mouseReleased", HPT['x'], HPT['y'], button="left")
        time.sleep(0.6)
        run3 = ev("state.running")
        v3 = float(ev("state.v")); s3 = float(ev("state.s"))
        check('三点画布=继续（running 恢复且速度增大）', run3 and v3 > vB, (run3, vB, v3))
        check('继续时位置不清零（s 只增不减）', s3 >= s_paused, (s_paused, s3))

        # 到底后再点 = 重新释放：先让车跑到底（done），点击后应从头再跑
        ws.ev("state.s = Math.hypot(state.b,state.h) - 0.01; state.running=true")
        time.sleep(1.2)
        done_now = ev("state.done")
        cdp_mouse(ws, "mousePressed", HPT['x'], HPT['y'], button="left", click_count=1)
        cdp_mouse(ws, "mouseReleased", HPT['x'], HPT['y'], button="left")
        time.sleep(0.4)
        s_re = float(ev("state.s")); run_re = ev("state.running"); done_re = ev("state.done")
        check('到底后再点=重新释放（从头再跑）', bool(done_now) and (not done_re) and bool(run_re) and s_re < 0.5, (done_now, done_re, round(s_re,3)))

        # ---- 6. 慢动作滑块：对数刻度，拖到 log10(5)≈×5、log10(10)=×10，读数联动 ----
        def set_slow(t):
            ws.ev("document.getElementById('slowRange').value=%r; slowFromSlider();" % t)
        set_slow(0);            f1 = int(ev("slowFactor"))
        set_slow(0.69897);      f2 = int(ev("slowFactor")); v2 = ev("document.getElementById('slowVal').textContent")
        set_slow(1);            f3 = int(ev("slowFactor"))
        set_slow(2);            f4 = int(ev("slowFactor"))
        set_slow(0);            f5 = int(ev("slowFactor"))
        check('慢动作滑块 1→5→10→100→1', f1==1 and f2==5 and f3==10 and f4==100 and f5==1, (f1,f2,f3,f4,f5))
        check('读数显示 ×5', ('×5' in v2 or '\\u00d75' in str(v2)), v2)

        # ---- 7. 慢动作物理：同一段动画时长内，×5 时走过的距离应约为 ×1 的 1/25
        #（时间缩 5 倍，s=½at² → 距离缩 25 倍；末速度只缩 5 倍）----
        ws.ev("slowFactor=1; reset(); state.running=true;")
        time.sleep(1.0)
        s_fast = float(ev("state.s"))
        ws.ev("reset(); state.running=false; slowFactor=5; state.running=true;")
        time.sleep(1.0)
        s_slow = float(ev("state.s"))
        ratio = s_fast / max(s_slow, 1e-9)
        check('慢动作×5：距离比≈25（t²效应）', 18 < ratio < 32, round(ratio,2))
        ws.ev("slowFactor=1; reset();")

        # ---- 8. 小车绘制存在（canvas 非空像素统计无法做，退而查函数与文案）----
        check('drawCart/cartPos 已定义', ev("(typeof drawCart)+'/'+(typeof cartPos)") == 'function/function')
        check('释放按钮文案=释放小车', '小车' in str(ev("document.getElementById('btnRelease').textContent")))

        n_fail = sum(1 for _,ok in results if not ok)
        print('\n===== %d/%d 通过 =====' % (len(results)-n_fail, len(results)))
        sys.exit(1 if n_fail else 0)
    finally:
        proc.terminate()

if __name__ == '__main__':
    main()
