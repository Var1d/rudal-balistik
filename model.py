"""
model.py
============================================================
  Konfigurasi & Data Model Simulasi
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Semua parameter simulasi yang bisa dikustomisasi ada di sini.
  Ubah nilai-nilai ini tanpa perlu menyentuh main.py.
============================================================
"""

import math


# ──────────────────────────────────────────────────────────
#  Parameter Fisika
# ──────────────────────────────────────────────────────────
class PhysicsConfig:
    GRAVITY   = 9.8      # m/s² (percepatan gravitasi)
    V0        = 80.0     # m/s  (kecepatan awal rudal)
    ANGLE_DEG = 60.0     # derajat (sudut peluncuran)
    SCALE     = 0.05     # faktor skala meter → unit OpenGL

    @classmethod
    def angle_rad(cls):
        return math.radians(cls.ANGLE_DEG)

    @classmethod
    def flight_time(cls):
        return (2.0 * cls.V0 * math.sin(cls.angle_rad())
                / cls.GRAVITY)

    @classmethod
    def max_range(cls):
        return (cls.V0**2 * math.sin(2.0 * cls.angle_rad())
                / cls.GRAVITY)

    @classmethod
    def max_height(cls):
        return ((cls.V0 * math.sin(cls.angle_rad()))**2
                / (2.0 * cls.GRAVITY))

    @classmethod
    def pos_x(cls, t):
        return cls.V0 * math.cos(cls.angle_rad()) * t

    @classmethod
    def pos_y(cls, t):
        return (cls.V0 * math.sin(cls.angle_rad()) * t
                - 0.5 * cls.GRAVITY * t**2)

    @classmethod
    def vel_x(cls, t):
        return cls.V0 * math.cos(cls.angle_rad())

    @classmethod
    def vel_y(cls, t):
        return cls.V0 * math.sin(cls.angle_rad()) - cls.GRAVITY * t


# ──────────────────────────────────────────────────────────
#  Konfigurasi Rendering
# ──────────────────────────────────────────────────────────
class RenderConfig:
    WINDOW_W      = 1200
    WINDOW_H      = 700
    WINDOW_TITLE  = b"OPENGL_RUDAL - Simulasi Balistik 3D - Kelompok 58 UNSIL 2026"
    TIMER_MS      = 16        # ~60 FPS
    DT            = 0.016
    FOV           = 45.0
    NEAR_CLIP     = 0.01
    FAR_CLIP      = 300.0
    BG_COLOR      = (0.04, 0.04, 0.13, 1.0)  # langit malam

    # Slow-motion: aktif saat rudal < threshold meter dari tanah
    SLOWMO_HEIGHT_THRESHOLD = 2.0    # meter
    SLOWMO_FACTOR           = 0.15   # 15% kecepatan normal


# ──────────────────────────────────────────────────────────
#  Posisi Objek di Scene
# ──────────────────────────────────────────────────────────
class SceneConfig:
    # Posisi launcher (titik asal peluncuran)
    LAUNCHER_X = 0.0
    LAUNCHER_Z = 0.0

    # Posisi kendaraan militer pendukung (relatif dari launcher)
    VEHICLES = [
        {"x": -1.5, "z":  0.4},
        {"x": -2.2, "z": -0.3},
        {"x": -3.0, "z":  0.1},
    ]

    # Pohon: dihasilkan secara acak di sekitar scene
    TREE_COUNT_LEFT  = 20   # sisi kiri (area launcher)
    TREE_COUNT_RIGHT = 10   # sisi kanan (area target)
    TREE_SEED        = 7    # seed random untuk reproduksibilitas

    # Terrain grid
    TERRAIN_COLS = 60
    TERRAIN_ROWS = 30
    TERRAIN_W    = 22.0
    TERRAIN_D    = 12.0
    TERRAIN_X0   = -11.0
    TERRAIN_Z0   = -6.0

    # Bintang
    STAR_COUNT = 380
    STAR_SEED  = 42


# ──────────────────────────────────────────────────────────
#  Info Kelompok (untuk HUD dan laporan)
# ──────────────────────────────────────────────────────────
class GroupInfo:
    KELOMPOK = "58"
    PRODI    = "Informatika"
    FAKULTAS = "Teknik"
    UNIV     = "Universitas Siliwangi"
    TAHUN    = "2026"

    ANGGOTA = [
        ("Jamal Abdul Nasir",    "247006111015", "Particle VFX"),
        ("Fiqri Mochamad Fadillah", "247006111051", "Lighting & Material"),
        ("Faisal Hadi Saik",    "247006111052", "Camera & Slow-Motion"),
        ("Irsyad Khoerul Umam", "247006111055", "Terrain, Sky, Vegetasi"),
        ("Farid Dhiya Fairuz",  "247006111058", "3D Model & Texture"),
    ]

    @classmethod
    def print_info(cls):
        print("=" * 56)
        print(f"  OPENGL_RUDAL – Kelompok {cls.KELOMPOK}")
        print(f"  {cls.PRODI} – {cls.FAKULTAS} – {cls.UNIV} {cls.TAHUN}")
        print("-" * 56)
        for nama, nim, peran in cls.ANGGOTA:
            print(f"  {nim}  {nama:<28} [{peran}]")
        print("=" * 56)

        pc = PhysicsConfig
        print(f"  Sudut     : {pc.ANGLE_DEG:.0f}°")
        print(f"  V0        : {pc.V0:.0f} m/s")
        print(f"  Jangkauan : {pc.max_range():.1f} m")
        print(f"  T. terbang: {pc.flight_time():.2f} s")
        print(f"  T. maks   : {pc.max_height():.1f} m")
        print("=" * 56)
