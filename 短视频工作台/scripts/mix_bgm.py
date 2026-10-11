# -*- coding: utf-8 -*-
"""真实 BGM 循环混音: bgm_real.wav(60s) 循环铺满 85.35s + 口播 -> mixed.wav"""
import os
import wave, numpy as np

BASE = os.environ.get("SM_BASE", os.path.expanduser("~/single-video-demo"))
SR = 48000
DUR = 85.35
N = int(SR * DUR)

with wave.open(f"{BASE}/bgm_real.wav", "rb") as w:
    b = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32767
nb = len(b)
# 循环
tiles = int(np.ceil(N / nb))
bgm = np.tile(b, tiles)[:N]
# 淡入淡出
t = np.arange(N) / SR
env = np.clip(np.minimum(t / 1.0, (DUR - t) / 3.0), 0, 1)
bgm *= env
bgm *= 0.20  # 音量

with wave.open(f"{BASE}/koubo.wav", "rb") as w:
    kd = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32767
kt = np.arange(len(kd)) / 16000
ko = np.interp(t, kt, kd).astype(np.float32)

mix = ko + bgm
mix = np.clip(mix, -1, 1)
mix16 = (mix * 32767).astype(np.int16)
with wave.open(f"{BASE}/mixed.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(mix16.tobytes())
print("mixed.wav done with real bgm, tiles=", tiles)
