#!/usr/bin/env python3
"""生成双语缩略图：用 CDP 在页面里设好状态与语言后截图。
用法: python3 gen_thumbs.py <page.html> <out_base.jpg>
"""
import base64, json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp_lang_test import WS, start, wait_port

PORT = os.environ.get('CDP_PORT', '9350')

def shoot(page_abs, out_base):
    target = "file://" + page_abs
    for lang in ('zh', 'en'):
        proc = start("/tmp/thumb-prof-%s-%s" % (lang, PORT))
        try:
            wait_port()
            pages = json.load(urllib.request.urlopen("http://127.0.0.1:%s/json" % PORT))
            page = next(t for t in pages if t["type"] == "page")
            ws = WS(page["webSocketDebuggerUrl"])
            ws.cmd("Page.enable"); ws.cmd("Runtime.enable")
            ws.cmd("Emulation.setDeviceMetricsOverride",
                   {"width": 1200, "height": 760, "deviceScaleFactor": 1.5, "mobile": False})
            ws.cmd("Page.navigate", {"url": target})
            time.sleep(2.0)

            # 先设语言（触发 langchange → 页面重绘 canvas），再把小球放到斜面中段并重绘
            setup = """(function(){
              window.SiteLang.setLang('%s');
              const d=derived();
              state.s=d.L*0.45; state.v=Math.sqrt(2*d.a*state.s);
              simTime=Math.sqrt(2*state.s/d.a); state.running=true;
              buildTable(); readouts(); draw();
              return 'ok';
            })()""" % lang
            print(lang, ws.ev(setup))
            time.sleep(0.6)

            d = ws.cmd("Page.captureScreenshot", {"format": "png"})
            png_path = "%s_%s.png" % (out_base, lang)
            open(png_path, "wb").write(base64.b64decode(d["data"]))
            print('  saved', png_path)
        finally:
            proc.terminate()
        time.sleep(1.0)

if __name__ == '__main__':
    page = os.path.abspath(sys.argv[1])
    base = sys.argv[2]
    shoot(page, base)
