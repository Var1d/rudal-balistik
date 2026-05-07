"""
comp_model.py
============================================================
  Composite Model – Kelas Dasar untuk Semua Objek 3D
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Menyediakan interface seragam untuk semua objek scene:
    - Posisi & orientasi (translate, rotate, scale)
    - Bounding box (untuk deteksi tabrakan sederhana)
    - Visibility check
    - Debug wireframe mode
============================================================
"""

import math
from OpenGL.GL   import *
from OpenGL.GLUT import *


class CompModel:
    """
    Kelas dasar untuk semua model komposit dalam scene.
    Semua class objek (Missile, Launcher, Bunker, dst.)
    sebaiknya mewarisi (inherit) dari class ini.
    """

    def __init__(self, x=0.0, y=0.0, z=0.0,
                 rot_y=0.0, scale=1.0):
        # Transformasi
        self.pos_x   = x
        self.pos_y   = y
        self.pos_z   = z
        self.rot_y   = rot_y     # rotasi sumbu Y (derajat)
        self.scale   = scale

        # Bounding box (lokal, sebelum transformasi)
        self.bbox_w  = 1.0      # lebar
        self.bbox_h  = 1.0      # tinggi
        self.bbox_d  = 1.0      # kedalaman

        # State
        self.visible      = True
        self.debug_bbox   = False   # tampilkan wireframe bbox

    # ── Transformasi ──────────────────────────────────────
    def apply_transform(self):
        """Push matrix + terapkan transformasi. Dipanggil sebelum draw."""
        glPushMatrix()
        glTranslatef(self.pos_x, self.pos_y, self.pos_z)
        glRotatef(self.rot_y, 0.0, 1.0, 0.0)
        glScalef(self.scale, self.scale, self.scale)

    def pop_transform(self):
        """Pop matrix. Dipanggil setelah draw."""
        if self.debug_bbox:
            self._draw_bbox_wireframe()
        glPopMatrix()

    # ── Bounding Box ──────────────────────────────────────
    def set_bbox(self, w, h, d):
        self.bbox_w = w
        self.bbox_h = h
        self.bbox_d = d

    def get_world_bbox(self):
        """
        Kembalikan AABB (axis-aligned bounding box) dalam
        koordinat dunia sebagai (min_x, max_x, min_y, max_y,
        min_z, max_z).
        """
        hw = self.bbox_w * self.scale * 0.5
        hh = self.bbox_h * self.scale * 0.5
        hd = self.bbox_d * self.scale * 0.5
        return (
            self.pos_x - hw, self.pos_x + hw,
            self.pos_y,      self.pos_y + hh*2,
            self.pos_z - hd, self.pos_z + hd,
        )

    def intersects_point(self, px, py, pz, radius=0.1):
        """
        Cek apakah titik (px,py,pz) dengan radius tertentu
        berpotongan dengan bounding box objek ini.
        Berguna untuk deteksi rudal mengenai target.
        """
        mn_x, mx_x, mn_y, mx_y, mn_z, mx_z = self.get_world_bbox()
        return (mn_x - radius <= px <= mx_x + radius and
                mn_y - radius <= py <= mx_y + radius and
                mn_z - radius <= pz <= mx_z + radius)

    def _draw_bbox_wireframe(self):
        """Gambar wireframe bounding box (mode debug)."""
        hw = self.bbox_w * 0.5
        hh = self.bbox_h
        hd = self.bbox_d * 0.5
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 1.0, 0.0)
        glLineWidth(1.5)
        glBegin(GL_LINE_LOOP)
        glVertex3f(-hw, 0,   -hd)
        glVertex3f( hw, 0,   -hd)
        glVertex3f( hw, 0,    hd)
        glVertex3f(-hw, 0,    hd)
        glEnd()
        glBegin(GL_LINE_LOOP)
        glVertex3f(-hw, hh, -hd)
        glVertex3f( hw, hh, -hd)
        glVertex3f( hw, hh,  hd)
        glVertex3f(-hw, hh,  hd)
        glEnd()
        for sx, sz in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            glBegin(GL_LINES)
            glVertex3f(sx*hw, 0,  sz*hd)
            glVertex3f(sx*hw, hh, sz*hd)
            glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    # ── Utilitas ──────────────────────────────────────────
    def distance_to(self, other):
        """Jarak Euclidean ke objek lain."""
        return math.sqrt(
            (self.pos_x - other.pos_x)**2 +
            (self.pos_y - other.pos_y)**2 +
            (self.pos_z - other.pos_z)**2
        )

    def move_to(self, x, y, z):
        self.pos_x = x
        self.pos_y = y
        self.pos_z = z

    def rotate(self, deg_y):
        self.rot_y += deg_y

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"pos=({self.pos_x:.2f},{self.pos_y:.2f},"
                f"{self.pos_z:.2f}), rot_y={self.rot_y:.1f}°)")
