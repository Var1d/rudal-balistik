"""
objects/bunker/bunker.py
============================================================
  Model Bunker / Gedung Target
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Komponen:
    - Gedung utama (beton bertingkat)
    - Antena menara
    - Jendela-jendela kecil
    - Target marker (lingkaran merah) di tanah
    - Dinding pelindung (barrier) di sekitar gedung
============================================================
"""

from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *


class Bunker:
    def draw(self, target_x, tex):
        from textures_manager import TextureManager
        q = gluNewQuadric()

        glPushMatrix()
        glTranslatef(target_x, 0.0, 0.0)

        # ── Gedung utama (lantai bawah) ────────────────────
        TextureManager.bind(tex.concrete if tex else None)
        glPushMatrix()
        glTranslatef(0, 0.22, 0)
        glColor3f(0.55, 0.52, 0.48)
        glScalef(0.55, 0.44, 0.45)
        glutSolidCube(1.0)
        glPopMatrix()
        TextureManager.unbind()

        # ── Lantai atas (lebih kecil) ──────────────────────
        glPushMatrix()
        glTranslatef(0, 0.52, 0)
        glColor3f(0.50, 0.47, 0.43)
        glScalef(0.38, 0.20, 0.33)
        glutSolidCube(1.0)
        glPopMatrix()

        # ── Atap datar dengan parapet ──────────────────────
        glPushMatrix()
        glTranslatef(0, 0.64, 0)
        glColor3f(0.42, 0.40, 0.36)
        glScalef(0.42, 0.04, 0.37)
        glutSolidCube(1.0)
        glPopMatrix()

        # Parapet (tembok kecil di pinggir atap)
        for px, pz in [(-0.19,0), (0.19,0), (0,0.17), (0,-0.17)]:
            glPushMatrix()
            glTranslatef(px, 0.68, pz)
            glColor3f(0.45, 0.42, 0.38)
            if px != 0:
                glScalef(0.02, 0.06, 0.35)
            else:
                glScalef(0.36, 0.06, 0.02)
            glutSolidCube(1.0)
            glPopMatrix()

        # ── Antena menara ──────────────────────────────────
        glPushMatrix()
        glTranslatef(0.05, 0.66, 0.05)
        glColor3f(0.60, 0.60, 0.60)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(q, 0.012, 0.010, 0.30, 8, 1)
        # Kepala antena
        glTranslatef(0, 0, 0.28)
        gluCylinder(q, 0.020, 0.000, 0.04, 8, 1)
        glPopMatrix()

        # ── Jendela-jendela ────────────────────────────────
        win_positions = [
            (-0.12, 0.26, 0.228), (0.00, 0.26, 0.228),
            ( 0.12, 0.26, 0.228), (-0.06, 0.26,-0.228),
            ( 0.06, 0.26,-0.228),
        ]
        for wx, wy, wz in win_positions:
            glPushMatrix()
            glTranslatef(wx, wy, wz)
            face = "front" if wz > 0 else "back"
            if face == "front":
                glRotatef(0, 0, 1, 0)
            else:
                glRotatef(180, 0, 1, 0)
            # Bingkai jendela
            glColor3f(0.30, 0.28, 0.25)
            glScalef(0.10, 0.10, 0.01)
            glutSolidCube(1.0)
            glPopMatrix()
            # Kaca (sedikit di depan bingkai)
            glPushMatrix()
            glTranslatef(wx, wy, wz + (0.007 if face=="front" else -0.007))
            glColor3f(0.25, 0.45, 0.55)
            glScalef(0.07, 0.07, 0.005)
            glutSolidCube(1.0)
            glPopMatrix()

        # ── Dinding barrier (4 sisi) ───────────────────────
        barrier_data = [
            (-0.42, 0.06, 0.0,  0.04, 0.12, 0.60),  # kiri
            ( 0.42, 0.06, 0.0,  0.04, 0.12, 0.60),  # kanan
            ( 0.0,  0.06, 0.35, 0.76, 0.12, 0.04),  # depan
            ( 0.0,  0.06,-0.35, 0.76, 0.12, 0.04),  # belakang
        ]
        for bx,by,bz, sw,sh,sd in barrier_data:
            glPushMatrix()
            glTranslatef(bx, by, bz)
            glColor3f(0.45, 0.42, 0.38)
            glScalef(sw, sh, sd)
            glutSolidCube(1.0)
            glPopMatrix()

        # ── Target marker di tanah ─────────────────────────
        glPushMatrix()
        glTranslatef(0, 0.018, 0)
        glRotatef(-90, 1, 0, 0)
        glColor3f(1.0, 0.0, 0.0)
        gluDisk(q, 0.0,  0.20, 36, 1)
        glColor3f(1.0, 1.0, 1.0)
        gluDisk(q, 0.11, 0.16, 36, 1)
        glColor3f(1.0, 0.0, 0.0)
        gluDisk(q, 0.0,  0.06, 36, 1)
        glPopMatrix()

        glPopMatrix()   # akhir translasi target_x
        gluDeleteQuadric(q)
