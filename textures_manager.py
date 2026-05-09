"""
textures_manager.py
============================================================
  Manajemen Tekstur Terpusat
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
============================================================
"""

import os
from OpenGL.GL import *


class TextureManager:
    def __init__(self):
        # ID tekstur (None = belum dimuat / tidak ada file)
        self.ground    = None
        self.metal     = None
        self.camo      = None
        self.bark      = None
        self.leaves    = None
        self.concrete  = None
        self.missile_t = None
        self.moon      = None

    def load_all(self):
        base = os.path.join(os.path.dirname(__file__), "textures")
        mapping = {
            "ground":    "ground.png",
            "metal":     "metal.png",
            "camo":      "camo.png",
            "bark":      "bark.png",
            "leaves":    "leaves.png",
            "concrete":  "concrete.png",
            "missile_t": "missile.png",
            "moon":      "moon.png",
        }
        for attr, fname in mapping.items():
            path = os.path.join(base, fname)
            tid  = self._load(path)
            setattr(self, attr, tid)

    def _load(self, path):
        if not os.path.exists(path):
            return None
        try:
            from PIL import Image
            img      = Image.open(path).convert("RGBA")
            data     = img.tobytes("raw", "RGBA", 0, -1)
            w, h     = img.size
            tid      = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, tid)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                         GL_RGBA, GL_UNSIGNED_BYTE, data)
            print(f"[TEX] Dimuat: {os.path.basename(path)}")
            return tid
        except ImportError:
            print("[TEX] Pillow tidak terinstal. Jalankan: pip install Pillow")
            return None
        except Exception as e:
            print(f"[TEX] Gagal memuat {path}: {e}")
            return None

    @staticmethod
    def bind(tid):
        if tid is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tid)

    @staticmethod
    def unbind():
        glDisable(GL_TEXTURE_2D)
