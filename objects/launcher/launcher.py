"""
objects/launcher/launcher.py
============================================================
  Model Kendaraan Peluncur (TEL – Transporter Erector Launcher)
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Komponen:
    - Badan truk militer (chassis panjang)
    - 6 roda (3 pasang sumbu)
    - Kabin pengemudi
    - Dudukan putar laras
    - Laras panjang dengan pelindung
============================================================
"""

import math
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *


class Launcher:
    def draw(self, angle_deg, tex):
        from textures_manager import TextureManager
        q = gluNewQuadric()

        # ── Chassis (badan truk) ───────────────────────────
        TextureManager.bind(tex.camo if tex else None)
        glPushMatrix()
        glColor3f(0.20, 0.30, 0.14)
        glScalef(0.75, 0.18, 0.42)
        glutSolidCube(1.0)
        glPopMatrix()
        TextureManager.unbind()

        # ── Kabin pengemudi ────────────────────────────────
        glPushMatrix()
        glTranslatef(-0.28, 0.14, 0.0)
        glColor3f(0.17, 0.25, 0.11)
        glScalef(0.20, 0.20, 0.36)
        glutSolidCube(1.0)
        glPopMatrix()

        # Kaca kabin
        glPushMatrix()
        glTranslatef(-0.19, 0.19, 0.0)
        glColor3f(0.30, 0.55, 0.65)
        glScalef(0.01, 0.10, 0.28)
        glutSolidCube(1.0)
        glPopMatrix()

        # ── 6 Roda (3 sumbu) ───────────────────────────────
        axle_x = [-0.24, 0.05, 0.28]
        for ax in axle_x:
            for side in [-0.23, 0.23]:
                glPushMatrix()
                glTranslatef(ax, -0.11, side)
                glRotatef(90, 1, 0, 0)
                # Ban
                glColor3f(0.12, 0.12, 0.12)
                gluCylinder(q, 0.08, 0.08, 0.05, 18, 1)
                # Pelek
                glColor3f(0.50, 0.50, 0.50)
                gluDisk(q, 0.0, 0.08, 18, 1)
                glTranslatef(0, 0, 0.05)
                gluDisk(q, 0.0, 0.08, 18, 1)
                glPopMatrix()

        # ── Dudukan putar laras ────────────────────────────
        glPushMatrix()
        glTranslatef(0.15, 0.14, 0.0)
        glColor3f(0.28, 0.28, 0.28)
        glScalef(0.14, 0.14, 0.16)
        glutSolidCube(1.0)
        glPopMatrix()

        # ── Laras panjang ──────────────────────────────────
        glPushMatrix()
        glTranslatef(0.15, 0.21, 0.0)
        glRotatef(angle_deg, 0, 0, 1)
        glTranslatef(0.0, 0.30, 0.0)
        glColor3f(0.20, 0.20, 0.20)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(q, 0.033, 0.033, 0.70, 18, 1)
        # Ujung laras (sedikit lebih lebar)
        glTranslatef(0, 0, 0.70)
        gluCylinder(q, 0.033, 0.040, 0.05, 18, 1)
        glPopMatrix()

        # ── Pelindung laras (kotak tipis) ──────────────────
        glPushMatrix()
        glTranslatef(0.15, 0.25, 0.0)
        glRotatef(angle_deg - 90, 0, 0, 1)
        glTranslatef(0.34, 0.0, 0.0)
        glColor3f(0.18, 0.27, 0.12)
        glScalef(0.65, 0.055, 0.055)
        glutSolidCube(1.0)
        glPopMatrix()

        # ── Antena kecil ───────────────────────────────────
        glPushMatrix()
        glTranslatef(0.30, 0.10, 0.18)
        glColor3f(0.20, 0.20, 0.20)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(q, 0.005, 0.005, 0.18, 6, 1)
        glPopMatrix()

        gluDeleteQuadric(q)
