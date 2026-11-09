#!/usr/bin/env python3
"""跨页语言持久化测试：首页切 EN -> 导航到模拟器 -> 检查是否仍为英文。"""
import json, os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cdp_lang_test import WS, start, wait_port

PORT = os.environ.get('CDP_PORT', '9360')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CN = r'[\u4e00-\u9fff]'

def zh_count(ws):
    return ws.ev("""(function(){
      const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
      let n,c=0; const bad=[];
      while((n=w.nextNode())){
        const t=n.nodeValue.trim(); if(!t) continue;
        const p=n.parentNode;
        if(p && /^(script|style)$/i.test(p.tagName)) continue;
        if(new RegExp('%s').test(t)){ c++; if(p && p.tagName!=='BUTTON') bad.push(p.tagName+': '+t.slice(0,50)); }
      }
      return {count:c, sample:bad.slice(0,6)};
    })()""" % CN)

def main():
    proc = start("/tmp/cross-prof-%s" % PORT)
    try:
        wait_port()
        pages = json.load(urllib.request.urlopen("http://127.0.0.1:%s/json" % PORT))
        page = next(t for t in pages if t["type"] == "page")
        ws = WS(page["webSocketDebuggerUrl"])
        ws.cmd("Page.enable"); ws.cmd("Runtime.enable")

        print("① 打开首页（默认中文）")
        ws.cmd("Page.navigate", {"url": "file://" + ROOT + "/index.html"})
        time.sleep(2)
        print("   lang =", ws.ev("window.SiteLang.getLang()"), "| 中文节点:", zh_count(ws)["count"])

        print("\n② 首页点击 EN")
        print("  ", ws.ev("document.querySelector('[data-lang=en]').click()") or "clicked")
        time.sleep(1.2)
        r = zh_count(ws)
        print("   lang =", ws.ev("window.SiteLang.getLang()"), "| 残留中文节点:", r["count"], r["sample"])
        print("   img src =", ws.ev("document.querySelector('img[data-lang-en]').getAttribute('src')"))

        print("\n③ 点击卡片链接进入模拟器（同浏览器会话，localStorage 应保留）")
        ws.cmd("Page.navigate", {"url": "file://" + ROOT + "/incline-energy.html"})
        time.sleep(2.2)
        r = zh_count(ws)
        print("   lang =", ws.ev("window.SiteLang.getLang()"))
        print("   title =", ws.ev("document.title"))
        print("   残留中文节点:", r["count"], r["sample"])
        print("   canvas 状态文字是否英文:", ws.ev("""(function(){
            // canvas 内容无法读文本，改测 tr() 结果与表格表头
            return {th0: document.querySelector('table th') ? document.querySelector('table th').textContent : 'none',
                    trTest: tr('运动进行中…')};
        })()"""))
    finally:
        proc.terminate()

main()
