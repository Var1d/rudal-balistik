"""
objects/missile/missile.py
============================================================
  Model Rudal Balistik 3D – Versi Final
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Fitur:
    - Badan ramping + kepala lancip + sirip trapesium
    - 4 canard (sayap kecil di tengah badan)
    - Animasi api nosel (exhaust fire) saat terbang
============================================================
"""

import math, random
from OpenGL.GL   import *
from OpenGL.GLU  import *


class Missile:
    def draw(self, x, y, sim_t, v0, gravity, angle_rad, scale, tex):
        vx  = v0 * math.cos(angle_rad)
        vy  = v0 * math.sin(angle_rad) - gravity * sim_t
        ang = math.degrees(math.atan2(vy, vx))
        q   = gluNewQuadric()

        glPushMatrix()
        glTranslatef(x, y, 0.0)
        glRotatef(ang, 0, 0, 1)
        glRotatef(-90, 1, 0, 0)

        # Badan
        glColor3f(0.75, 0.18, 0.18)
        gluCylinder(q, 0.04, 0.04, 0.45, 20, 1)

        # Kepala lancip
        glPushMatrix()
        glTranslatef(0, 0, 0.45)
        glColor3f(0.92, 0.92, 0.08)
        gluCylinder(q, 0.04, 0.0, 0.20, 20, 1)
        glPopMatrix()

        # Tutup belakang
        glColor3f(0.45, 0.08, 0.08)
        gluDisk(q, 0.0, 0.04, 20, 1)

        # Nosel
        glPushMatrix()
        glTranslatef(0, 0, -0.07)
        glColor3f(0.15, 0.15, 0.15)
        gluCylinder(q, 0.03, 0.055, 0.07, 20, 1)
        glPopMatrix()

        # Canard (4 sayap kecil depan)
        glColor3f(0.50, 0.12, 0.12)
        for i in range(4):
            glPushMatrix()
            glRotatef(i*90.0+45.0, 0, 0, 1)
            glTranslatef(0, 0, 0.30)
            glBegin(GL_TRIANGLES)
            glVertex3f(0.040, 0.0,  0.00)
            glVertex3f(0.110, 0.0, -0.08)
            glVertex3f(0.040, 0.0, -0.08)
            glEnd()
            glPopMatrix()

        # Sirip belakang (trapesium)
        glColor3f(0.55, 0.12, 0.12)
        for i in range(4):
            glPushMatrix()
            glRotatef(i*90.0, 0, 0, 1)
            glBegin(GL_QUADS)
            glVertex3f(0.040, 0.0,  0.00)
            glVertex3f(0.040, 0.0, -0.18)
            glVertex3f(0.210, 0.0, -0.22)
            glVertex3f(0.170, 0.0,  0.00)
            glEnd()
            glPopMatrix()

        glPopMatrix()

        # Api nosel
        self._draw_nozzle_fire(x, y, ang)
        gluDeleteQuadric(q)

    def _draw_nozzle_fire(self, mx, my, ang_deg):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        ang_rad  = math.radians(ang_deg)
        nx = mx - 0.07 * math.cos(ang_rad)
        ny = my - 0.07 * math.sin(ang_rad)
        for _ in range(random.randint(5, 9)):
            length = random.uniform(0.07, 0.26)
            width  = random.uniform(0.02, 0.07)
            offset = random.uniform(-0.02, 0.02)
            ft = random.random()
            if ft < 0.3:   r,g,b,a = 1.0, 1.0, 0.7, 0.90
            elif ft < 0.7: r,g,b,a = 1.0, 0.5, 0.0, random.uniform(0.5,0.8)
            else:          r,g,b,a = 0.9, 0.15,0.0, random.uniform(0.3,0.6)
            glPushMatrix()
            glTranslatef(nx, ny, 0.0)
            glRotatef(ang_deg+180, 0, 0, 1)
            glTranslatef(offset - width*0.5, 0, 0)
            glBegin(GL_QUADS)
            glColor4f(r, g, b, a)
            glVertex3f(0.0,    -width*0.5, 0.0)
            glVertex3f(0.0,     width*0.5, 0.0)
            glColor4f(r, g, b, 0.0)
            glVertex3f(length,  width*0.15, 0.0)
            glVertex3f(length, -width*0.15, 0.0)
            glEnd()
            glPopMatrix()
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
