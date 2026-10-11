# -*- coding: utf-8 -*-
"""解析 subs.ass -> 渲染47张透明字幕PNG + 生成 filter_complex_script"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.environ.get("SM_BASE", os.path.expanduser("~/single-video-demo"))
FONT = os.environ.get("SM_FONT", os.path.expanduser("~/fonts/SourceHanSansCN-Heavy.otf"))
SUBDIR = os.path.join(BASE, "subpng")
os.makedirs(SUBDIR, exist_ok=True)

INK = (234, 242, 255, 255)
f = ImageFont.truetype(FONT, 56)

events = []
with open(os.path.join(BASE, "subs.ass")) as fp:
    for line in fp:
        if not line.startswith("Dialogue:"):
            continue
        parts = line.strip().split(",", 9)
        st, en, txt = parts[1], parts[2], parts[9]
        def sec(t):
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
        events.append((sec(st), sec(en), txt.replace("\\N", "\n")))

img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
img.close()
for i, (st, en, txt) in enumerate(events, 1):
    im = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    lines = txt.split("\n")
    lh = 76
    total = lh * len(lines)
    y = 1355 - total + lh / 2
    for ln in lines:
        d.text((540, y), ln, font=f, fill=INK, anchor="mm", stroke_width=7, stroke_fill=(0, 0, 0, 255))
        y += lh
    im.save(f"{SUBDIR}/s{i:02d}.png")

# filter script
lines = ["[0:v]fps=30[b0];"]
prev = "b0"
for i in range(len(events)):
    nxt = f"c{i+1}"
    lines.append(f"[{prev}][{i+3}:v]overlay=0:0:enable='between(t,{events[i][0]:.2f},{events[i][1]:.2f})'[{nxt}];")
    prev = nxt
lines.append(f"[1:v]crop=720:720:0:100,scale=300:300,format=rgba,geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':a='if(lt(hypot(X-150,Y-150),148),255,0)'[win];")
lines.append(f"[{prev}][win]overlay=x=390:y=1400:shortest=0[vout]")
with open(os.path.join(BASE, "filter.txt"), "w") as fp:
    fp.write("\n".join(lines))

# 输入参数
inputs = ["-f concat -safe 0 -i list.txt", "-stream_loop 2 -i '<你的BGM文件>.mp4'", "-i koubo.wav"]
for i in range(len(events)):
    inputs.append(f"-i subpng/s{i:02d}.png")
with open(os.path.join(BASE, "inputs.txt"), "w") as fp:
    fp.write(" ".join(inputs))

print(f"{len(events)} sub pngs + filter.txt + inputs.txt done")
