"""
generate_textures.py
============================================================
  Generator Tekstur Programatik
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Membuat semua file tekstur (.png) secara programatik
  menggunakan Pillow, sehingga tidak perlu download gambar.

  Jalankan SEKALI sebelum main.py:
      python generate_textures.py

  Menghasilkan di folder textures/:
    ground.png    – rumput berbintik-bintik
    metal.png     – logam abu berkilap
    camo.png      – kamuflase militer hijau
    bark.png      – kulit kayu coklat
    leaves.png    – daun hijau
    concrete.png  – beton abu bertekstur
    missile.png   – badan rudal merah metalik
============================================================
"""

import os
import random
import math

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    print("ERROR: Pillow belum terinstal.")
    print("Jalankan: pip install Pillow")
    exit(1)

OUT_DIR = os.path.join(os.path.dirname(__file__), "textures")
os.makedirs(OUT_DIR, exist_ok=True)
SIZE = 256   # resolusi setiap tekstur


def save(img, name):
    path = os.path.join(OUT_DIR, name)
    img.save(path)
    print(f"[GEN] Dibuat: {name}")


# ──────────────────────────────────────────────────────────
#  1. GROUND – rumput hijau berbintik
# ──────────────────────────────────────────────────────────
def gen_ground():
    img = Image.new("RGBA", (SIZE, SIZE))
    pix = img.load()
    rng = random.Random(1)
    for y in range(SIZE):
        for x in range(SIZE):
            # Warna dasar hijau gelap
            r = int(22 + rng.uniform(-6, 6))
            g = int(75 + rng.uniform(-15, 15))
            b = int(22 + rng.uniform(-5, 5))
            # Tambahkan variasi gelap/terang per baris
            noise = math.sin(x*0.3)*4 + math.cos(y*0.5)*4
            r = max(0, min(255, r + int(noise)))
            g = max(0, min(255, g + int(noise*1.5)))
            b = max(0, min(255, b + int(noise)))
            pix[x, y] = (r, g, b, 255)
    # Blur ringan untuk tekstur yang lebih alami
    img = img.filter(ImageFilter.GaussianBlur(1))
    save(img, "ground.png")


# ──────────────────────────────────────────────────────────
#  2. METAL – logam abu-abu berkilap
# ──────────────────────────────────────────────────────────
def gen_metal():
    img = Image.new("RGBA", (SIZE, SIZE))
    pix = img.load()
    rng = random.Random(2)
    for y in range(SIZE):
        for x in range(SIZE):
            # Arah kilap horizontal (garis-garis halus)
            streak = int(math.sin(y * 0.8) * 12 + math.sin(y * 3.1) * 5)
            base = 135 + streak
            noise = int(rng.uniform(-8, 8))
            v = max(60, min(210, base + noise))
            pix[x, y] = (v, v, v+8, 255)
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    save(img, "metal.png")


# ──────────────────────────────────────────────────────────
#  3. CAMO – kamuflase militer (hijau-coklat-hitam)
# ──────────────────────────────────────────────────────────
def gen_camo():
    img = Image.new("RGBA", (SIZE, SIZE), (55, 85, 35, 255))
    draw = ImageDraw.Draw(img)
    rng  = random.Random(3)
    patches = [
        (70, 55, 30),    # coklat tua
        (30, 50, 20),    # hijau gelap
        (20, 20, 15),    # hitam kehijauan
        (80, 70, 25),    # tan/khaki
    ]
    # Gambar 35 patch blob acak
    for _ in range(35):
        color = patches[rng.randint(0, len(patches)-1)]
        cx = rng.randint(0, SIZE)
        cy = rng.randint(0, SIZE)
        rw = rng.randint(18, 55)
        rh = rng.randint(14, 40)
        draw.ellipse([cx-rw, cy-rh, cx+rw, cy+rh],
                     fill=color+(255,))
    img = img.filter(ImageFilter.GaussianBlur(3))
    save(img, "camo.png")


# ──────────────────────────────────────────────────────────
#  4. BARK – kulit kayu coklat berkerut
# ──────────────────────────────────────────────────────────
def gen_bark():
    img = Image.new("RGBA", (SIZE, SIZE))
    pix = img.load()
    rng = random.Random(4)
    for y in range(SIZE):
        for x in range(SIZE):
            # Garis-garis vertikal seperti serat kayu
            grain = int(math.sin(x*0.25 + math.sin(y*0.08)*3)*18)
            noise = int(rng.uniform(-10, 10))
            r = max(0, min(255, 95 + grain + noise))
            g = max(0, min(255, 58 + grain//2 + noise))
            b = max(0, min(255, 28 + noise//2))
            pix[x, y] = (r, g, b, 255)
    img = img.filter(ImageFilter.GaussianBlur(0.8))
    save(img, "bark.png")


# ──────────────────────────────────────────────────────────
#  5. LEAVES – daun hijau bertotol
# ──────────────────────────────────────────────────────────
def gen_leaves():
    img = Image.new("RGBA", (SIZE, SIZE))
    pix = img.load()
    rng = random.Random(5)
    for y in range(SIZE):
        for x in range(SIZE):
            # Pola daun: gelombang 2D
            pattern = (math.sin(x*0.4)*math.cos(y*0.4) +
                       math.sin(x*1.2 + y*0.8)*0.5)
            noise   = rng.uniform(-0.15, 0.15)
            v       = pattern + noise
            if v > 0.2:
                r, g, b = 18, 88, 18      # hijau tua
            elif v > -0.1:
                r, g, b = 28, 108, 28     # hijau sedang
            else:
                r, g, b = 12, 65, 12      # hijau sangat gelap
            pix[x, y] = (r, g, b, 255)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    save(img, "leaves.png")


# ──────────────────────────────────────────────────────────
#  6. CONCRETE – beton abu-abu kasar
# ──────────────────────────────────────────────────────────
def gen_concrete():
    img = Image.new("RGBA", (SIZE, SIZE))
    pix = img.load()
    rng = random.Random(6)
    for y in range(SIZE):
        for x in range(SIZE):
            noise = int(rng.uniform(-22, 22))
            # Pola blok beton (garis horizontal & vertikal tipis)
            is_line = (y % 32 < 2) or (x % 64 < 2)
            base = 88 if not is_line else 65
            v = max(40, min(180, base + noise))
            pix[x, y] = (v, v, v-4, 255)
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    save(img, "concrete.png")


# ──────────────────────────────────────────────────────────
#  7. MISSILE – badan rudal merah metalik
# ──────────────────────────────────────────────────────────
def gen_missile():
    img = Image.new("RGBA", (SIZE, SIZE))
    pix = img.load()
    rng = random.Random(7)
    for y in range(SIZE):
        for x in range(SIZE):
            # Efek silinder: lebih terang di tengah
            cx = SIZE // 2
            dist = abs(x - cx)
            highlight = max(0, int((1 - dist/(SIZE*0.5)) * 60))
            noise = int(rng.uniform(-8, 8))
            r = max(120, min(255, 175 + highlight + noise))
            g = max(0,   min(80,  35  + noise//2))
            b = max(0,   min(60,  30  + noise//2))
            # Garis panel horizontal tipis
            if y % 40 < 2:
                r = max(0, r - 30)
                g = max(0, g - 10)
            pix[x, y] = (r, g, b, 255)
    img = img.filter(ImageFilter.GaussianBlur(0.5))
    save(img, "missile.png")


# ──────────────────────────────────────────────────────────
#  8. MOON – tekstur bulan berlubang (crater)
# ──────────────────────────────────────────────────────────
def gen_moon():
    img = Image.new("RGBA", (SIZE, SIZE))
    pix = img.load()
    rng = random.Random(8)
    for y in range(SIZE):
        for x in range(SIZE):
            # Warna dasar abu-abu keputihan
            v = int(215 + rng.uniform(-15, 15))
            pix[x, y] = (v, v, v - 10, 255)
    
    draw = ImageDraw.Draw(img)
    # Tambahkan kawah-kawah (craters)
    for _ in range(45):
        cx = rng.randint(0, SIZE)
        cy = rng.randint(0, SIZE)
        r  = rng.randint(3, 22)
        # Warna kawah sedikit lebih gelap
        v  = rng.randint(150, 195)
        # Gambar bayangan kawah sederhana
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(v, v, v, 255))
        # Tambahkan sedikit highlight di pinggiran kawah
        draw.arc([cx-r, cy-r, cx+r, cy+r], 45, 225, fill=(v+20, v+20, v+20, 255))
    
    img = img.filter(ImageFilter.GaussianBlur(1.5))
    save(img, "moon.png")


# ──────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Generator Tekstur – OPENGL_RUDAL")
    print("  Kelompok 58 – UNSIL 2026")
    print("=" * 50)

    gen_ground()
    gen_metal()
    gen_camo()
    gen_bark()
    gen_leaves()
    gen_concrete()
    gen_missile()
    gen_moon()

    print("=" * 50)
    print(f"  Selesai! 8 tekstur disimpan di: {OUT_DIR}")
    print("  Sekarang jalankan: python main.py")
    print("=" * 50)
