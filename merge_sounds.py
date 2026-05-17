"""
merge_sounds.py
Gabungkan typewriter1-8.wav menjadi type.wav
Jalankan sekali: python merge_sounds.py
"""
import wave
import os

input_files = [f"sound/typewriter{i}.wav" for i in range(1, 9)]
output_file = "sound/type.wav"

# Baca semua file dan gabungkan
frames_all = []
params = None

for path in input_files:
    if not os.path.exists(path):
        print(f"[SKIP] Tidak ditemukan: {path}")
        continue
    with wave.open(path, 'rb') as wf:
        if params is None:
            params = wf.getparams()
        frames_all.append(wf.readframes(wf.getnframes()))
    print(f"[OK] Dibaca: {path}")

if frames_all and params:
    with wave.open(output_file, 'wb') as out:
        out.setparams(params)
        for f in frames_all:
            out.writeframes(f)
    print(f"\n[SELESAI] Disimpan ke: {output_file}")
else:
    print("[ERROR] Tidak ada file yang berhasil dibaca.")
