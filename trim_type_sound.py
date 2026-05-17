"""
trim_type_sound.py
Potong type.wav menjadi 0.08 detik pertama saja.
Jalankan sekali: python trim_type_sound.py
"""
import wave
import os

src  = "sound/type.wav"
dst  = "sound/type.wav"
DURATION = 0.08   # detik — ubah sesuai selera

if not os.path.exists(src):
    print(f"[ERROR] File tidak ditemukan: {src}")
    exit()

with wave.open(src, 'rb') as wf:
    params     = wf.getparams()
    rate       = wf.getframerate()
    n_keep     = int(rate * DURATION)
    frames     = wf.readframes(n_keep)

tmp = src + ".tmp"
with wave.open(tmp, 'wb') as out:
    out.setparams(params)
    out.writeframes(frames)

os.replace(tmp, dst)
print(f"[SELESAI] {dst} dipotong menjadi {DURATION*630:.0f} ms")
