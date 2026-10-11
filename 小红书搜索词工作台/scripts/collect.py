#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小红书搜索下拉词采集

思路（关键，别改成别的）：
  不逆向 x-s 签名（脆、易封），也不解析易碎的下拉 DOM。
  做法 = CDP 接管一个**真实 Chrome**，在搜索框里逐字打字，
        然后抓页面自己发出的 /api/sns/web/v1/search/recommend 响应体。
  这样既拿到结构化 JSON，又让页面自己处理签名与登录态。

前置：先跑 start-chrome.sh 起好浏览器（端口 9335）。
用法：
  python3 collect.py --seeds seeds.txt --out output
  python3 collect.py --expand 5 --wait 3.5
"""
import argparse
import base64
import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

import websocket

PORT = int(os.environ.get("XHS_PORT", "9335"))

# 选输入框：**必须挑可见且尺寸正常的那个**。
# 2026-10-10 踩坑：`#search-input` 是个 0×0 的隐藏元素，往里打字毫无反应；
# 真正可见的是 `#search-input-in-feeds`（placeholder「我在小红书搞装修」）。
FOCUS_JS = (
    "(() => {"
    "  const ok = e => { const r = e.getBoundingClientRect();"
    "    return r.width > 120 && r.height > 12 && (e.offsetParent || e.getClientRects().length); };"
    "  const c = [...document.querySelectorAll('input,textarea,[contenteditable=true]')].filter(ok);"
    "  const el = c.find(e => e.id === 'search-input-in-feeds')"
    "          || c.find(e => e.id === 'search-input') || c[0];"
    "  if (!el) return 'no-visible-input';"
    "  el.scrollIntoView({block:'center'}); el.focus(); el.click();"
    "  return 'ok:' + (el.id || el.tagName);"
    "})()"
)

CLEAR_JS = (
    "(() => {"
    "  const el = document.activeElement; if (!el) return 'no-active';"
    "  const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype"
    "              : el.tagName === 'INPUT'    ? window.HTMLInputElement.prototype : null;"
    "  if (proto) { const set = Object.getOwnPropertyDescriptor(proto, 'value').set;"
    "    set.call(el, ''); el.dispatchEvent(new Event('input', {bubbles: true})); }"
    "  else { el.innerText = ''; el.dispatchEvent(new Event('input', {bubbles: true})); }"
    "  return 'cleared';"
    "})()"
)


def http_json(path):
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}{path}", timeout=6) as r:
        return json.loads(r.read())


class Session:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(
            ws_url, timeout=20, max_size=128 * 1024 * 1024, suppress_origin=True
        )
        self.n = 0
        self.log = []

    def call(self, method, **params):
        self.n += 1
        mid = self.n
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})
            self.log.append(m)

    def pump(self, seconds):
        end = time.time() + seconds
        self.ws.settimeout(0.3)
        while time.time() < end:
            try:
                self.log.append(json.loads(self.ws.recv()))
            except Exception:
                pass
        self.ws.settimeout(20)


def find_page():
    pages = [t for t in http_json("/json/list") if t.get("type") == "page"]
    for t in pages:
        if "xiaohongshu.com" in (t.get("url") or ""):
            return t
    return pages[0] if pages else None


def kw_of(url: str):
    """从 recommend 的 URL 里解出 keyword（注意空格是 + 而不是 %20）。"""
    try:
        q = urllib.parse.urlparse(url).query
        raw = urllib.parse.parse_qs(q).get("keyword", [""])[0]
        return raw.replace("+", " ")
    except Exception:
        return ""


def suggest(s: Session, kw: str, wait: float = 2.8):
    """在真实搜索框里打一个词，返回下拉联想词。"""
    s.log.clear()
    s.call("Page.bringToFront")          # 窗口不在前台时 Input.insertText 会被丢弃
    s.call("Runtime.evaluate", expression=FOCUS_JS, returnByValue=True)
    s.call("Runtime.evaluate", expression=CLEAR_JS, returnByValue=True)

    for ch in kw:
        s.call("Input.insertText", text=ch)
        time.sleep(0.1)
    s.pump(wait)

    # 下拉接口是**每敲一个字发一次**（keyword=A → AI → AI+主 → AI+主图），
    # 所以要按 keyword 精确匹配，取整词那一条；匹配不到再退回最后一条。
    hits = []
    for m in s.log:
        if m.get("method") == "Network.responseReceived":
            u = m["params"]["response"]["url"]
            if "/search/recommend" in u:
                hits.append((kw_of(u), m["params"]["requestId"]))
    if not hits:
        return []
    exact = [rid for k, rid in hits if k == kw]
    rid = exact[-1] if exact else hits[-1][1]

    body = s.call("Network.getResponseBody", requestId=rid)
    raw = body.get("body", "")
    if body.get("base64Encoded"):
        raw = base64.b64decode(raw).decode("utf-8", "ignore")
    try:
        data = json.loads(raw)
    except Exception:
        return []
    out = []
    for it in (data.get("data", {}) or {}).get("sug_items", []) or []:
        t = (it.get("text") or "").strip()
        if t and t not in out:
            out.append(t)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="seeds.txt")
    ap.add_argument("--out", default="output")
    ap.add_argument("--expand", type=int, default=0,
                    help="对每个种子词的前 N 个联想词再做一次二级扩展（默认 0＝不做）")
    ap.add_argument("--wait", type=float, default=2.8)
    ap.add_argument("--gap", type=float, default=1.1)
    ap.add_argument("--no-reload", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.seeds):
        print(f"!! 找不到种子词文件：{args.seeds}")
        sys.exit(1)
    seeds = []
    for line in open(args.seeds, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if line:
            seeds.append(line)

    page = find_page()
    if not page:
        print("!! 没找到标签页——先跑 start-chrome.sh")
        sys.exit(1)
    print(f"# 接管标签页: {page.get('url')[:90]}")
    s = Session(page["webSocketDebuggerUrl"])
    s.call("Network.enable")
    s.call("Page.enable")
    s.call("Runtime.enable")
    s.call("Page.bringToFront")

    # 每个词开始前先回到干净状态：页面被登录浮层接管后输入框会变成 0×0（踩过）
    if not args.no_reload:
        print("# 重载页面，回到干净状态…")
        s.call("Page.navigate", url="https://www.xiaohongshu.com/explore")
        time.sleep(6.5)
        s.pump(1)

    st = s.call("Runtime.evaluate", returnByValue=True, expression=(
        "(()=>{const w=[...document.querySelectorAll('input,textarea')]"
        ".filter(e=>{const r=e.getBoundingClientRect();return r.width>120&&r.height>12;});"
        "return JSON.stringify({url:location.href,visibleInputs:w.map(e=>e.id||e.tagName)});})()"
    ))
    print("# 页面状态:", st["result"]["value"])
    if "'visibleInputs':[]" in st["result"]["value"] or '"visibleInputs":[]' in st["result"]["value"]:
        print("!! 找不到可见输入框，终止（页面可能弹了登录框）")
        sys.exit(2)

    result, failed = {}, []
    for i, kw in enumerate(seeds, 1):
        words = []
        for attempt in (1, 2):
            try:
                words = suggest(s, kw, args.wait)
            except Exception as e:
                print(f"   ! {kw} 第{attempt}次异常: {e}")
            if words:
                break
            time.sleep(1.6)
        if not words:
            failed.append(kw)
        result[kw] = words
        print(f"[{i}/{len(seeds)}] {kw} → {len(words)} 个")
        if args.expand:
            second = {}
            for w in words[:args.expand]:
                try:
                    second[w] = suggest(s, w, args.wait)
                except Exception:
                    second[w] = []
                time.sleep(0.6)
            result[f"__二级__{kw}"] = second
        time.sleep(args.gap)

    os.makedirs(args.out, exist_ok=True)
    today = date.today().isoformat()

    jp = os.path.join(args.out, f"raw-{today}.json")
    json.dump(result, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    cp = os.path.join(args.out, f"keywords-{today}.csv")
    with open(cp, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["种子词", "序号", "联想词"])
        for kw, words in result.items():
            if kw.startswith("__二级__"):
                continue
            for n, t in enumerate(words, 1):
                w.writerow([kw, n, t])

    md = [f"# 小红书搜索词表（{today}）", "",
          f"> 种子词 {len(seeds)} 个；来源＝小红书站内搜索下拉联想词；抓取日期 {today}。", ""]
    if failed:
        md += [f"> ⚠️ 本次未取到词的种子：{'、'.join(failed)}", ""]
    for kw, words in result.items():
        if kw.startswith("__二级__"):
            continue
        md.append(f"## {kw}")
        md.append("")
        if words:
            for n, t in enumerate(words, 1):
                md.append(f"{n}. {t}")
        else:
            md.append("（未取到）")
        md.append("")
        sec = result.get(f"__二级__{kw}")
        if sec:
            md.append("<details><summary>二级扩展</summary>")
            md.append("")
            for k2, v2 in sec.items():
                md.append(f"- **{k2}** → {'、'.join(v2) if v2 else '（无）'}")
            md.append("")
            md.append("</details>")
            md.append("")
    mp = os.path.join(args.out, f"词表-{today}.md")
    open(mp, "w", encoding="utf-8").write("\n".join(md))

    total = sum(len(v) for k, v in result.items() if not k.startswith("__二级__"))
    print(f"\n# 完成：{len(seeds) - len(failed)}/{len(seeds)} 个种子词，共 {total} 个联想词")
    print(f"# JSON  → {jp}")
    print(f"# CSV   → {cp}")
    print(f"# 词表  → {mp}")


if __name__ == "__main__":
    main()
