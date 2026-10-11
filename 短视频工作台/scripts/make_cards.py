# -*- coding: utf-8 -*-
"""暗黑科技风图层化卡片: 深空渐变背景+星点, 青蓝描边, 橙点缀 + 持续动效 -> anim.json"""
import os, json, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.environ.get("SM_BASE", os.path.expanduser("~/single-video-demo"))
FONT = os.environ.get("SM_FONT", os.path.expanduser("~/fonts/SourceHanSansCN-Heavy.otf"))
ART = os.path.join(BASE, "art_dark")
ASSETS = os.path.join(BASE, "hypit_assets")
OUT = os.path.join(BASE, "cards")

W, H = 1080, 1920
WHT = (234, 242, 255)        # 主文字
ORANGE = (255, 159, 46)      # 强调橙
CYAN = (110, 224, 255)       # 科技青
GRAY = (138, 155, 185)       # 次要灰蓝
DBLOCK = (22, 36, 66)        # 深蓝块底
DBLOCK2 = (30, 52, 92)       # 深蓝块底(亮一档)
LINEGRAY = (90, 110, 140)    # 弱化线条/文字

def F(s): return ImageFont.truetype(FONT, s)
def ctext(d, y, text, size, fill, x=W//2, ls=0):
    f = F(size)
    if ls <= 0:
        d.text((x, y), text, font=f, fill=fill, anchor="mm"); return
    ws = [d.textlength(ch, font=f) for ch in text]
    total = sum(ws) + ls * (len(text) - 1); cx = x - total / 2
    for ch, w in zip(text, ws):
        d.text((cx + w / 2, y), ch, font=f, fill=fill, anchor="mm"); cx += w + ls

def dark_bg():
    top = np.array([3, 4, 8], dtype=np.float32); bot = np.array([7, 9, 16], dtype=np.float32)
    g = np.linspace(0, 1, H)[:, None].astype(np.float32)
    arr = np.repeat(((top * (1 - g) + bot * g)).astype(np.uint8)[:, None, :], W, axis=1)
    img = Image.fromarray(arr)
    d = ImageDraw.Draw(img)
    rnd = random.Random(42)
    for _ in range(160):
        x = rnd.randint(0, W); y = rnd.randint(0, H); r = rnd.randint(1, 2)
        v = rnd.randint(60, 175)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(v, v + 15, min(255, v + 50)))
    return img

def A(typ, delay=0.0, dur=0.6, motion="float", amp=10, period=3.5, phase=0.0):
    return {"type": typ, "delay": delay, "dur": dur, "motion": motion, "amp": amp, "period": period, "phase": phase}
def U(delay=0.0, dur=0.6, amp=10, period=3.5, phase=0.0): return A("up", delay, dur, "float", amp, period, phase)
def S(delay=0.0, dur=0.6, amp=0.045, period=6.0, phase=0.0): return A("scale", delay, dur, "breathe", amp, period, phase)
def P(delay=0.0, dur=0.6, amp=0.055, period=2.5, phase=0.0): return A("scale", delay, dur, "pulse", amp, period, phase)
def L(delay=0.0, dur=0.5, amp=8, period=3.0, phase=0.0): return A("slide_l", delay, dur, "float", amp, period, phase)
def R(delay=0.0, dur=0.5, amp=8, period=3.0, phase=0.0): return A("slide_r", delay, dur, "float", amp, period, phase)
def Fs(delay=0.0, dur=0.5, amp=8, period=2.8, phase=0.0): return A("up", delay, dur, "float", amp, period, phase)

class Card:
    def __init__(self, tag="AI 视频实测 · EP01"):
        self.bg = dark_bg()
        d = ImageDraw.Draw(self.bg)
        d.ellipse((70, 66, 86, 82), fill=ORANGE)
        d.text((104, 74), tag, font=F(30), fill=GRAY, anchor="lm")
        d.text((540, 1730), os.environ.get("CARD_FOOTER", "你的品牌 · AI+电商"), font=F(28), fill=GRAY, anchor="mm")
        self.layers = []
    def L(self, anim):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.layers.append((im, anim))
        return ImageDraw.Draw(im)

def title_two(c, l1, l2, c2=ORANGE):
    d = c.L(U(0.0)); ctext(d, 170, l1, 92, WHT)
    d = c.L(U(0.08, period=4.0)); ctext(d, 292, l2, 92, c2)

def art_layer(path, y0, box=880):
    a = Image.open(path).convert("RGB").crop((82, 82, 942, 942)).resize((box, box), Image.LANCZOS)
    li = Image.new("RGBA", (W, H), (0, 0, 0, 0)); li.paste(a, ((W - box) // 2, y0))
    return li

def browser_card(path, y0, w=820, url="hypit.ai"):
    """官网界面特效: 浏览器窗口(标题栏+三圆点+地址栏) + 青蓝辉光边框 + 圆角 + 来源角标"""
    im = Image.open(path).convert("RGBA")
    ratio = w / im.width
    ih = int(im.height * ratio)
    im = im.resize((w, ih), Image.LANCZOS)
    x0 = (W - w) // 2
    bar = 54
    total_h = ih + bar
    win = Image.new("RGBA", (w, total_h), (0, 0, 0, 0))
    wd = ImageDraw.Draw(win)
    wd.rounded_rectangle((0, 0, w, total_h), 16, fill=(12, 17, 32, 255))
    wd.rounded_rectangle((0, 0, w, bar), 16, fill=(16, 24, 44, 255))
    wd.rectangle((0, bar // 2, w, bar), fill=(16, 24, 44, 255))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        wd.ellipse((20 + i * 30, bar // 2 - 6, 20 + i * 30 + 12, bar // 2 + 6), fill=c)
    wd.rounded_rectangle((120, 14, w - 20, bar - 14), 10, fill=(8, 12, 24, 255))
    wd.text((134, bar // 2), url, font=F(24), fill=GRAY, anchor="lm")
    win.paste(im, (0, bar), im)
    win_mask = Image.new("L", (w, total_h), 0)
    ImageDraw.Draw(win_mask).rounded_rectangle((0, 0, w, total_h), 16, fill=255)
    win.putalpha(win_mask)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pad = 12
    d.rounded_rectangle((x0 - pad - 6, y0 - pad - 6, x0 + w + pad + 6, y0 + total_h + pad + 6), 28, fill=(110, 224, 255, 26))
    d.rounded_rectangle((x0 - pad - 2, y0 - pad - 2, x0 + w + pad + 2, y0 + total_h + pad + 2), 24, fill=(110, 224, 255, 38))
    d.rounded_rectangle((x0 - pad, y0 - pad, x0 + w + pad, y0 + total_h + pad), 22, fill=(10, 14, 28, 255))
    layer.paste(win, (x0, y0), win)
    d.text((x0 + w, y0 + total_h + pad + 10), "Hypit 官网界面", font=F(26), fill=GRAY, anchor="rm")
    return layer

ALL = {}

c = Card(); title_two(c, "一句台词要改", "整条片子重来")
c.layers.append((art_layer(f"{ART}/Flat_minimal_tech_illustration_2026-09-23T13-27-17.png", 340, box=820), S(0.18)))
ALL["card1"] = c

c = Card()
d = c.L(U(0.0)); ctext(d, 300, "核心就四个字", 52, GRAY)
d = c.L(P(0.08, amp=0.04, period=3.0)); ctext(d, 500, "Hypit", 200, WHT, ls=6)
d = c.L(P(0.16, amp=0.05, period=2.4)); ctext(d, 800, "词锚定", 250, ORANGE, ls=10)
li = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(li)
labels = ["字幕", "画面", "音效", "特效"]; bw, bh, gap = 190, 100, 40
x0 = (W - (bw * 4 + gap * 3)) / 2
for i, lab in enumerate(labels):
    x = x0 + i * (bw + gap)
    dd.line((x + bw / 2, 935, x + bw / 2, 1055), fill=CYAN, width=4)
    dd.ellipse((x + bw / 2 - 9, 1042, x + bw / 2 + 9, 1060), fill=CYAN)
    dd.rounded_rectangle((x, 1075, x + bw, 1075 + bh), 24, fill=DBLOCK, outline=CYAN, width=3)
    ctext(dd, 1075 + bh / 2, lab, 48, WHT, x=x + bw / 2)
c.layers.append((li, Fs(0.28, amp=7, period=2.8)))
ALL["card2"] = c

c = Card(); title_two(c, "传统剪辑", "钉死在秒数上")
rows = ["画面", "字幕", "特效"]; gx, gy, gw, gh, gg = 120, 660, 150, 260, 20
for i in range(5):
    li = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(li)
    x = gx + i * (gw + gg); hot = (i == 3); after = (i == 4)
    oc = ORANGE if hot else (LINEGRAY if after else CYAN)
    if after:
        for k in range(3):
            dd.arc((x + 20, gy + 30 + k * 78, x + gw - 20, gy + 30 + k * 78 + 56), 0, 360, fill=LINEGRAY, width=4)
        dd.text((x + gw / 2, gy + gh / 2), "?", font=F(120), fill=LINEGRAY, anchor="mm")
    else:
        for k, lab in enumerate(rows):
            dd.rounded_rectangle((x + 18, gy + 26 + k * 78, x + gw - 18, gy + 26 + k * 78 + 58), 14, fill=DBLOCK2 if not hot else (70, 40, 10))
            ctext(dd, gy + 26 + k * 78 + 29, lab, 34, WHT, x=x + gw / 2)
    dd.rounded_rectangle((x, gy, x + gw, gy + gh), 20, outline=oc, width=4)
    ctext(dd, gy + gh + 60, f"0{i+1}s", 44, ORANGE if hot else GRAY, x=x + gw / 2)
    c.layers.append((li, U(0.2 + i * 0.06, amp=7, period=3.0, phase=i * 0.6)))
d = c.L(Fs(0.55)); ctext(d, 1180, "第几秒放什么 · 全部写死", 44, GRAY)
ALL["card3"] = c

c = Card(); title_two(c, "锚在词上", "不是秒上")
lx, rx, cw2, chh = 90, 620, 370, 110
li = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(li)
dd.rounded_rectangle((lx, 480, lx + cw2, 520), 16, fill=(28, 44, 76))
ctext(dd, 500, "秒", 40, GRAY, x=lx + cw2 / 2)
for i in range(4):
    y = 570 + i * (chh + 26)
    dd.rounded_rectangle((lx, y, lx + cw2, y + chh), 20, fill=(18, 30, 56))
    ctext(dd, y + chh / 2, f"0{i+1}s", 52, GRAY, x=lx + cw2 / 2)
c.layers.append((li, L(0.15, amp=9, period=4.0)))
li = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(li)
dd.rounded_rectangle((rx, 480, rx + cw2, 520), 16, fill=(70, 40, 10))
ctext(dd, 500, "词", 40, ORANGE, x=rx + cw2 / 2)
for i, wd in enumerate(["改一句词", "删一句话", "换台词", "换产品"]):
    y = 570 + i * (chh + 26)
    dd.rounded_rectangle((rx, y, rx + cw2, y + chh), 20, fill=DBLOCK, outline=ORANGE, width=3)
    ctext(dd, y + chh / 2, wd, 50, WHT, x=rx + 150)
    for k in range(3):
        dd.ellipse((rx + 262, y + 22 + k * 24, rx + 286, y + 46 + k * 24), fill=CYAN)
c.layers.append((li, R(0.15, amp=9, period=4.0)))
li = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(li)
dd.polygon((505, 940, 575, 940, 575, 900, 615, 990, 575, 1080, 575, 1040, 505, 1040), fill=ORANGE)
c.layers.append((li, P(0.32, amp=0.06, period=2.0)))
d = c.L(Fs(0.45)); ctext(d, 1180, "素材跟着词走 · 不跟着秒走", 44, GRAY)
ALL["card4"] = c

c = Card(); title_two(c, "改一行文案", "整条片子跟着变")
c.layers.append((browser_card(f"{ASSETS}/svml.png", 340, w=820), S(0.18)))
ALL["card5"] = c

c = Card(); title_two(c, "用自己的声音?", "只重录那一句")
li = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(li)
cx, cy, r = 540, 880, 175
dd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ORANGE)
dd.rounded_rectangle((cx - 42, cy - 88, cx + 42, cy + 20), 42, fill=(20, 30, 56))
dd.arc((cx - 70, cy - 55, cx + 70, cy + 62), 20, 160, fill=(20, 30, 56), width=12)
dd.line((cx, cy + 62, cx, cy + 108), fill=(20, 30, 56), width=12)
dd.line((cx - 42, cy + 108, cx + 42, cy + 108), fill=(20, 30, 56), width=12)
random.seed(7); bx = cx - 330
for i in range(22):
    h2 = random.randint(16, 90)
    dd.rounded_rectangle((bx + i * 30, 1160 - h2 / 2, bx + i * 30 + 14, 1160 + h2 / 2), 7, fill=CYAN if abs(i - 10) <= 4 else (40, 70, 120))
c.layers.append((li, P(0.2, amp=0.04, period=2.8)))
d = c.L(Fs(0.42)); ctext(d, 1200, "剩下的对齐 · 自动排好", 46, GRAY)
ALL["card6"] = c

c = Card(); title_two(c, "爆款复刻最头疼的", "一致性")
c.layers.append((browser_card(f"{ASSETS}/svml.png", 420, w=820), S(0.18)))
ALL["card7"] = c

c = Card()
d = c.L(Fs(0.0, amp=6, period=4.0)); d.text((250, 500), '"', font=F(260), fill=ORANGE, anchor="mm")
d = c.L(U(0.05)); ctext(d, 640, "把最熬人的", 100, WHT)
d = c.L(U(0.12, period=4.0)); ctext(d, 800, "重复劳动", 160, WHT, ls=6)
d = c.L(P(0.2, amp=0.05, period=2.2)); ctext(d, 1000, "干掉。", 160, ORANGE, ls=6)
ALL["card8"] = c

c = Card()
d = c.L(U(0.0, amp=8, period=3.6)); ctext(d, 560, "实测开始", 150, WHT, ls=8)
li = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(li)
dd.rounded_rectangle((190, 780, 890, 980), 40, fill=ORANGE)
ctext(dd, 880, "评论区扣【词锚定】", 72, (16, 10, 4))
c.layers.append((li, P(0.15, amp=0.05, period=2.2)))
d = c.L(Fs(0.38)); ctext(d, 1180, "从选题到成片 · 全流程拆解", 48, GRAY)
ALL["card9"] = c

anim = {}
for name, c in ALL.items():
    os.makedirs(os.path.join(OUT, name), exist_ok=True)
    c.bg.save(os.path.join(OUT, name, "bg.png"))
    aspec = []
    for i, (im, a) in enumerate(c.layers, 1):
        im.save(os.path.join(OUT, name, f"L{i}.png")); aspec.append(a)
    anim[name] = aspec
json.dump(anim, open(os.path.join(OUT, "anim.json"), "w"), ensure_ascii=False, indent=1)
print("dark cards done:", len(ALL))
