#!/usr/bin/env python3
"""CDP 驱动无头 Chromium：真实点击语言按钮 + 诊断页面状态。
用法: python3 cdp.py <html文件> [输出前缀] [--click-en]
"""
import base64, json, os, re, socket, subprocess, sys, time, urllib.request

PORT = int(os.environ.get('CDP_PORT', '9340'))

def start(profile):
    return subprocess.Popen(
        ["chromium", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
         f"--remote-debugging-port={PORT}", f"--user-data-dir={profile}",
         "--window-size=1200,900", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def wait_port(timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1) as r:
                return json.load(r)["webSocketDebuggerUrl"]
        except Exception:
            time.sleep(0.4)
    raise SystemExit("调试端口未就绪")

class WS:
    def __init__(self, url):
        m = re.match(r"ws://([^:/]+):(\d+)(/.*)", url)
        host, port, path = m.group(1), int(m.group(2)), m.group(3)
        self.s = socket.create_connection((host, port))
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall(("GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\n"
                        "Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n"
                        % (path, host, port, key)).encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.s.recv(4096)
        self.buf = buf.split(b"\r\n\r\n", 1)[1]
        self._id = 0

    def _send(self, data):
        p = data.encode(); mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(p)); n = len(p)
        if n < 126: hdr = bytes([0x81, 0x80 | n])
        elif n < 65536: hdr = bytes([0x81, 0x80 | 126]) + n.to_bytes(2, "big")
        else: hdr = bytes([0x81, 0x80 | 127]) + n.to_bytes(8, "big")
        self.s.sendall(hdr + mask + masked)

    def _recv(self):
        while True:
            if len(self.buf) < 2:
                self.buf += self.s.recv(65536); continue
            b1, b2 = self.buf[0], self.buf[1]; ln = b2 & 0x7F; off = 2
            if ln == 126:
                while len(self.buf) < 4: self.buf += self.s.recv(65536)
                ln = int.from_bytes(self.buf[2:4], "big"); off = 4
            elif ln == 127:
                while len(self.buf) < 10: self.buf += self.s.recv(65536)
                ln = int.from_bytes(self.buf[2:10], "big"); off = 10
            while len(self.buf) < off + ln: self.buf += self.s.recv(65536)
            pay = self.buf[off:off+ln]; self.buf = self.buf[off+ln:]
            if (b1 & 0x0F) == 1: return pay.decode("utf-8", "replace")

    def cmd(self, method, params=None):
        self._id += 1; mid = self._id
        self._send(json.dumps({"id": mid, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(self._recv())
            if msg.get("id") == mid:
                if "error" in msg: raise SystemExit("CDP %s: %s" % (method, msg["error"]))
                return msg.get("result", {})

    def ev(self, expr):
        r = self.cmd("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
        if r.get("exceptionDetails"):
            return "JS_ERROR: " + json.dumps(r["exceptionDetails"].get("exception", {}), ensure_ascii=False)[:300]
        return r["result"].get("value")

    def shot(self, path):
        d = self.cmd("Page.captureScreenshot", {"format": "png"})
        if d.get("data"):
            open(path, "wb").write(base64.b64decode(d["data"])); return path
        return None

CN = r'[\u4e00-\u9fff]'

def zh_nodes(ws):
    return ws.ev("""(function(){
      const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
      const bad=[]; let n;
      while((n=w.nextNode())){
        const t=n.nodeValue.trim(); if(!t) continue;
        const p=n.parentNode;
        if(p && /^(script|style)$/i.test(p.tagName)) continue;
        if(new RegExp('%s').test(t)) bad.push((p?p.tagName:'?')+': '+t.slice(0,70));
      }
      return bad;
    })()""" % CN)

def main():
    target = os.path.abspath(sys.argv[1])
    prefix = sys.argv[2] if len(sys.argv) > 2 else "/tmp/t"
    proc = start("/tmp/cdp-prof-%d" % PORT)
    try:
        wait_port()
        pages = json.load(urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT))
        page = next(t for t in pages if t["type"] == "page")
        ws = WS(page["webSocketDebuggerUrl"])
        ws.cmd("Page.enable"); ws.cmd("Runtime.enable")
        ws.cmd("Page.navigate", {"url": "file://" + target})
        time.sleep(2.2)

        print("[初始] title:", ws.ev("document.title"))
        print("[初始] SiteLang:", ws.ev("typeof window.SiteLang"), " getLang:", ws.ev("window.SiteLang?window.SiteLang.getLang():'NA'"))
        print("[初始] 中文节点数:", len(zh_nodes(ws) or []))

        print("\n[点击 EN]", ws.ev("(function(){const b=document.querySelector('[data-lang=en]'); if(!b)return 'NO_BUTTON'; b.click(); return 'ok'})()"))
        time.sleep(1.6)

        print("[切换后] title:", ws.ev("document.title"), "| lang:", ws.ev("document.documentElement.lang"))
        bad = zh_nodes(ws) or []
        print("[切换后] 残留中文节点 %d 个:" % len(bad))
        for x in bad: print("   ", x)

        p = ws.shot(prefix + "_en.png");  print("\n截图:", p)

        # 关键诊断：字典本身能否取到英文
        print("\n[字典直测] tr('(恒定)') =", ws.ev("tr('(恒定)')"))
        print("[字典直测] tr('当前理论末速度 √(2gh) =') =", ws.ev("tr('当前理论末速度 √(2gh) =')"))

        ws.ev("document.querySelector('[data-lang=zh]').click()"); time.sleep(1.2)
        print("\n[切回中文] 含中文 th 数:", ws.ev("[...document.querySelectorAll('th')].filter(e=>new RegExp('%s').test(e.textContent)).length" % CN))
        ws.shot(prefix + "_zh.png")
    finally:
        proc.terminate()

if __name__ == '__main__':
    main()
