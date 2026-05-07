"""
objects/vehicle/vehicle.py
============================================================
  Model Kendaraan Militer Pendukung (Jeep / APC kecil)
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Komponen:
    - Badan kendaraan kotak
    - 4 roda
    - Kabin + kaca depan
    - Antena kecil
============================================================
"""

from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *


class Vehicle:
    """Kendaraan militer kecil yang ditempatkan di sekitar launcher."""

    def __init__(self, x=0.0, z=0.0):
        self.x = x
        self.z = z

    def draw(self, tex):
        from textures_manager import TextureManager
        q = gluNewQuadric()

        glPushMatrix()
        glTranslatef(self.x, 0.0, self.z)

        # ── Badan ──────────────────────────────────────────
        TextureManager.bind(tex.camo if tex else None)
        glPushMatrix()
        glTranslatef(0, 0.09, 0)
        glColor3f(0.22, 0.30, 0.14)
        glScalef(0.38, 0.18, 0.22)
        glutSolidCube(1.0)
        glPopMatrix()
        TextureManager.unbind()

        # ── Kabin ──────────────────────────────────────────
        glPushMatrix()
        glTranslatef(-0.06, 0.22, 0)
        glColor3f(0.20, 0.27, 0.12)
        glScalef(0.18, 0.14, 0.18)
        glutSolidCube(1.0)
        glPopMatrix()

        # Kaca depan
        glPushMatrix()
        glTranslatef(0.04, 0.24, 0)
        glColor3f(0.28, 0.50, 0.58)
        glScalef(0.008, 0.08, 0.14)
        glutSolidCube(1.0)
        glPopMatrix()

        # ── 4 Roda ─────────────────────────────────────────
        for wx, wz in [(-0.12, 0.12),(-0.12,-0.12),
                        ( 0.12, 0.12),( 0.12,-0.12)]:
            glPushMatrix()
            glTranslatef(wx, 0.06, wz)
            glRotatef(90, 1, 0, 0)
            glColor3f(0.12, 0.12, 0.12)
            gluCylinder(q, 0.05, 0.05, 0.035, 14, 1)
            glColor3f(0.45, 0.45, 0.45)
            gluDisk(q, 0.0, 0.05, 14, 1)
            glTranslatef(0, 0, 0.035)
            gluDisk(q, 0.0, 0.05, 14, 1)
            glPopMatrix()

        # ── Antena ─────────────────────────────────────────
        glPushMatrix()
        glTranslatef(-0.10, 0.30, 0.08)
        glColor3f(0.22, 0.22, 0.22)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(q, 0.004, 0.004, 0.14, 6, 1)
        glPopMatrix()

        glPopMatrix()
        gluDeleteQuadric(q)
