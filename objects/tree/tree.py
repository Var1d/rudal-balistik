"""
objects/tree/tree.py
============================================================
  Model Pohon Pinus Militer (vegetasi scene)
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Komponen:
    - Batang silinder coklat
    - 3 lapisan daun kerucut (pinus)
    - Skala acak untuk variasi ukuran
============================================================
"""

from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *


class Tree:
    def __init__(self, x=0.0, z=0.0, scale=1.0):
        self.x = x
        self.z = z
        self.s = scale

    def draw(self, tex):
        from textures_manager import TextureManager
        q = gluNewQuadric()
        s = self.s

        glPushMatrix()
        glTranslatef(self.x, 0.0, self.z)
        glScalef(s, s, s)

        # ── Batang ─────────────────────────────────────────
        TextureManager.bind(tex.bark if tex else None)
        glColor3f(0.38, 0.25, 0.13)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(q, 0.045, 0.032, 0.35, 10, 1)
        glRotatef(90, 1, 0, 0)
        TextureManager.unbind()

        # ── 3 Lapisan daun (kerucut) ───────────────────────
        layers = [
            (0.30, 0.21, 0.30, 0.32),   # bawah: lebar
            (0.48, 0.17, 0.24, 0.26),   # tengah
            (0.63, 0.13, 0.18, 0.20),   # atas: kecil
        ]
        TextureManager.bind(tex.leaves if tex else None)
        for (ty, base_r, top_r, height) in layers:
            glPushMatrix()
            glTranslatef(0, ty, 0)
            # Warna sedikit bervariasi per lapisan
            shade = 0.08 + layers.index((ty,base_r,top_r,height)) * 0.03
            glColor3f(0.10+shade, 0.32+shade, 0.10+shade)
            glRotatef(-90, 1, 0, 0)
            gluCylinder(q, base_r, top_r * 0.1, height, 14, 1)
            # Tutup bawah daun
            glColor3f(0.08, 0.28, 0.08)
            gluDisk(q, 0.0, base_r, 14, 1)
            glPopMatrix()
        TextureManager.unbind()

        glPopMatrix()
        gluDeleteQuadric(q)
