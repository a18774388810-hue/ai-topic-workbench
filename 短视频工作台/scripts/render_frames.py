# -*- coding: utf-8 -*-
"""v4 逐元素动画 + 持续动效(float漂浮/breathe呼吸/pulse脉冲) + 真实BGM"""
import os, math, subprocess, json
from PIL import Image, ImageDraw

BASE = os.environ.get("SM_BASE", os.path.expanduser("~/single-video-demo"))
FPS = 30
DUR = 85.354
W, H = 1080, 1920
WX, WY, WS = 390, 1400, 300
OUT_DUR = 0.2

starts = [0, 10.19, 16.85, 24.79, 35.29, 50.65, 58.07, 71.13, 78.81, DUR]
anim = json.load(open(f"{BASE}/cards/anim.json"))
bgs, clayers = {}, {}
for ci in range(1, 10):
    name = f"card{ci}"
    bgs[ci] = Image.open(f"{BASE}/cards/{name}/bg.png").convert("RGB")
    clayers[ci] = [(Image.open(f"{BASE}/cards/{name}/L{i}.png").convert("RGBA"), a)
                   for i, a in enumerate(anim[name], 1)]

wins_all = [Image.open(f"{BASE}/winf/{n:04d}.jpg").convert("RGB") for n in range(1, 950)]
win_seq = wins_all[239:569] + wins_all[689:]
n_win = len(win_seq)

events = []
with open(f"{BASE}/subs.ass") as fp:
    for line in fp:
        if not line.startswith("Dialogue:"):
            continue
        p = line.strip().split(",", 9)
        def sec(t):
            h, m, s = t.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
        events.append((sec(p[1]), sec(p[2]), Image.open(f"{BASE}/subpng/s{len(events)+1:02d}.png").convert("RGBA")))

mask = Image.new("L", (WS, WS), 0)
ImageDraw.Draw(mask).ellipse((3, 3, WS - 3, WS - 3), fill=255)
ring = Image.new("RGBA", (WS + 12, WS + 12), (0, 0, 0, 0))
d2 = ImageDraw.Draw(ring)
d2.ellipse((1, 1, WS + 11, WS + 11), fill=(255, 255, 255, 255))
d2.ellipse((6, 6, WS + 5, WS + 5), fill=(0, 0, 0, 0))

fp = Image.new("RGBA", (W + 80, H + 80), (0, 0, 0, 0))
fd = ImageDraw.Draw(fp)
fd.ellipse((140, 140, 220, 220), fill=(110, 224, 255, 50))
fd.ellipse((920, 120, 1030, 230), outline=(255, 159, 46, 70), width=5)
fd.line((60, 620, 220, 560), fill=(110, 224, 255, 70), width=6)
fd.ellipse((960, 1600, 1010, 1650), fill=(110, 224, 255, 55))
fd.ellipse((420, 1800, 560, 1940), outline=(110, 224, 255, 50), width=5)
fd.ellipse((200, 1200, 240, 1240), fill=(255, 159, 46, 55))

BLACK = Image.new("RGB", (W, H), (6, 9, 20))
def ease_out_cubic(x): return 1 - (1 - x) ** 3
def ease_out_back(x):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

cmd = ["ffmpeg", "-v", "error", "-y",
       "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:",
       "-i", f"{BASE}/mixed.wav",
       "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "128k", "-shortest", f"{BASE}/成片_v7.mp4"]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

total = int(DUR * FPS)
for i in range(total):
    t = i / FPS
    ci = 0
    for k in range(len(starts) - 1):
        if starts[k] <= t < starts[k + 1]:
            ci = k; break
    else:
        ci = len(starts) - 2
    seg = starts[ci]; dur = starts[ci + 1] - starts[ci]
    e = t - seg
    frame = bgs[ci + 1].copy()
    for idx, (im, a) in enumerate(clayers[ci + 1]):
        te = e - a["delay"]
        if te < 0:
            continue
        typ = a["type"]; alpha = 1.0; u = im; ox = oy = 0
        if te < a["dur"]:
            k = te / a["dur"]
            if typ == "up":
                ease = ease_out_cubic(k); oy = int(90 * (1 - ease)); alpha = ease
            elif typ == "scale":
                ease = ease_out_back(k); s = 1.22 - 0.22 * ease; alpha = min(ease, 1.0)
                w2, h2 = int(W * s), int(H * s); u = im.resize((w2, h2), Image.LANCZOS); ox, oy = (W - w2) // 2, (H - h2) // 2
            elif typ == "slide_l":
                ease = ease_out_cubic(k); ox = int(-100 * (1 - ease)); alpha = ease
            else:
                ease = ease_out_cubic(k); ox = int(100 * (1 - ease)); alpha = ease
        else:
            mo = a.get("motion", "float"); amp = a.get("amp", 8.0); period = a.get("period", 3.5)
            ph = a.get("phase", 0.0) + idx * 1.1
            if mo == "breathe":
                s = 1 + amp * math.sin(2 * math.pi * t / period + ph)
                w2, h2 = int(W * s), int(H * s); u = im.resize((w2, h2), Image.LANCZOS); ox, oy = (W - w2) // 2, (H - h2) // 2
            elif mo == "pulse":
                s = 1 + amp * (0.5 + 0.5 * math.sin(2 * math.pi * t / period + ph))
                w2, h2 = int(W * s), int(H * s); u = im.resize((w2, h2), Image.LANCZOS); ox, oy = (W - w2) // 2, (H - h2) // 2
            else:
                oy = int(amp * math.sin(2 * math.pi * t / period + ph))
        if alpha < 1.0:
            u2 = u.copy(); u2.putalpha(u.getchannel("A").point(lambda v: int(v * alpha)))
            frame.paste(u2, (ox, oy), u2)
        else:
            frame.paste(u, (ox, oy), u)
    dx = int(30 * math.sin(2 * math.pi * t / 7.0)); dy = int(35 * math.sin(2 * math.pi * t / 9.0 + 2.0))
    fl = fp.crop((40 + dx, 40 + dy, 40 + dx + W, 40 + dy + H))
    frame.paste(fl, (0, 0), fl)
    frame.paste(win_seq[int(t * FPS) % n_win], (WX, WY), mask)
    for st, en, sp in events:
        if st <= t < en:
            frame.paste(sp, (0, 0), sp); break
    if e > dur - OUT_DUR:
        frame = Image.blend(BLACK, frame, 1 - (e - (dur - OUT_DUR)) / OUT_DUR * 0.5)
    proc.stdin.write(frame.tobytes())
    if i % 300 == 0:
        print(f"frame {i}/{total}", flush=True)

proc.stdin.close(); proc.wait()
print("done", proc.returncode)
