# -*- coding: utf-8 -*-
"""用法: python transcribe.py <音频路径>
   必须在取消代理的环境下跑:
   env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy python transcribe.py koubo.wav
"""
import os
import sys
from faster_whisper import WhisperModel

MODEL = os.environ.get("WHISPER_MODEL", os.path.expanduser(
    "~/.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120"))
if len(sys.argv) < 2:
    sys.exit("用法: python transcribe.py <音频路径>  (不要依赖写死路径!)")
AUDIO = sys.argv[1]

model = WhisperModel(MODEL, device="cpu", compute_type="int8")
segments, info = model.transcribe(AUDIO, language="zh", vad_filter=True, beam_size=5)

print(f"=== language={info.language} prob={info.language_probability:.2f} ===\n")
full = []
for seg in segments:
    t = seg.text.strip()
    full.append(t)
    print(f"[{seg.start:06.2f} - {seg.end:06.2f}] {t}")

print("\n=== 合并全文 ===")
print("".join(full))
