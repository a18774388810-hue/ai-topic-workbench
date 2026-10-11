# -*- coding: utf-8 -*-
"""生成科技氛围 BGM 垫底 + 与口播混音 -> mixed.wav (48k stereo)"""
import os
import wave, numpy as np

BASE = os.environ.get("SM_BASE", os.path.expanduser("~/single-video-demo"))
SR = 48000
DUR = 85.35
N = int(SR * DUR)
t = np.arange(N) / SR

# 和弦 pad: A2 E3 A3 C#4 E4
freqs = [110.0, 164.81, 220.0, 277.18, 329.63]
amps = [1.0, 0.65, 0.55, 0.45, 0.38]
phases = [0.0, 0.4, 0.9, 1.4, 2.0]
sig = sum(a * np.sin(2 * np.pi * f * t + p) for f, a, p in zip(freqs, amps, phases))
sig /= len(freqs)
# 呼吸 LFO + 轻微第二 LFO
lfo = 0.62 + 0.38 * np.sin(2 * np.pi * 0.12 * t) + 0.12 * np.sin(2 * np.pi * 0.05 * t + 1.3)
sig *= lfo
# 整体音量
sig *= 0.20
# 淡入淡出
env = np.clip(np.minimum(t / 1.5, (DUR - t) / 3.0), 0, 1)
sig *= env
# 立体声(右声道相位微移制造宽度)
right = np.roll(sig, 40) * 0.98 + sig * 0.02
left = sig
bgm = np.stack([left, right], axis=1)
bgm = np.clip(bgm, -1, 1)
bgm16 = (bgm * 32767).astype(np.int16)

with wave.open(f"{BASE}/bgm.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(bgm16.tobytes())

# ---- 混音: 口播(16k mono) 上采样到 48k + bgm ----
with wave.open(f"{BASE}/koubo.wav", "rb") as w:
    assert w.getframerate() == 16000 and w.getnchannels() == 1
    kd = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32767
kt = np.arange(len(kd)) / 16000
ko = np.interp(t, kt, kd).astype(np.float32)
mix = ko + 0.30 * (left + right) / 2  # bgm 垫底,口播为主
mix = np.clip(mix, -1, 1)
mix16 = (mix * 32767).astype(np.int16)
with wave.open(f"{BASE}/mixed.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(mix16.tobytes())
print("bgm.wav + mixed.wav done", N)
