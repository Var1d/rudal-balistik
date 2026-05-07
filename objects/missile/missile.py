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
from OpenGL.GLUT import *


class Missile:
    @staticmethod
    def _normalize3(v):
        x, y, z = v
        l = math.sqrt(x * x + y * y + z * z)
        if l < 1e-8:
            return (0.0, 1.0, 0.0)
        return (x / l, y / l, z / l)

    @staticmethod
    def _cross(a, b):
        return (
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        )

    def _apply_velocity_alignment(self, vx, vy, vz=0.0):
        # Forward axis model rudal diasumsikan +Z (arah ke hulu ledak).
        forward = self._normalize3((vx, vy, vz))
        world_up = (0.0, 1.0, 0.0)
        right = self._cross(world_up, forward)
        if math.sqrt(right[0] * right[0] + right[1] * right[1] + right[2] * right[2]) < 1e-6:
            world_up = (0.0, 0.0, 1.0)
            right = self._cross(world_up, forward)
        right = self._normalize3(right)
        up = self._normalize3(self._cross(forward, right))

        # glMultMatrixf memakai column-major.
        rot = [
            right[0], right[1], right[2], 0.0,
            up[0],    up[1],    up[2],    0.0,
            forward[0], forward[1], forward[2], 0.0,
            0.0,      0.0,      0.0,      1.0,
        ]
        glMultMatrixf(rot)

    def draw(self, x, y, sim_t, v0, gravity, angle_rad, scale, tex):
        vx  = v0 * math.cos(angle_rad)
        vy  = v0 * math.sin(angle_rad) - gravity * sim_t
        q   = gluNewQuadric()

        glPushMatrix()
        glTranslatef(x, y, 0.0)
        self._apply_velocity_alignment(vx, vy, 0.0)

        # Body utama (silver)
        glColor3f(0.80, 0.82, 0.84)
        gluCylinder(q, 0.050, 0.050, 0.56, 26, 1)

        # Ring kuning depan
        glPushMatrix()
        glTranslatef(0, 0, 0.47)
        glColor3f(0.96, 0.74, 0.08)
        gluCylinder(q, 0.051, 0.051, 0.028, 24, 1)
        glPopMatrix()

        # Kepala hitam
        glPushMatrix()
        glTranslatef(0, 0, 0.56)
        glColor3f(0.08, 0.09, 0.10)
        gluCylinder(q, 0.050, 0.0, 0.18, 26, 1)
        glPopMatrix()

        # Tutup belakang + nozzle ring
        glColor3f(0.22, 0.22, 0.23)
        gluDisk(q, 0.0, 0.050, 24, 1)
        glPushMatrix()
        glColor3f(0.16, 0.13, 0.10)
        gluCylinder(q, 0.048, 0.058, 0.030, 22, 1)
        glPopMatrix()

        # Nozzle dalam
        glPushMatrix()
        glTranslatef(0, 0, -0.085)
        glColor3f(0.10, 0.10, 0.11)
        gluCylinder(q, 0.028, 0.050, 0.085, 24, 1)
        glPopMatrix()

        # Panel line tipis body
        glColor3f(0.62, 0.64, 0.66)
        for z in (0.16, 0.30, 0.44):
            glPushMatrix()
            glTranslatef(0, 0, z)
            gluCylinder(q, 0.0505, 0.0505, 0.003, 24, 1)
            glPopMatrix()

        # Sirip delta besar (mid body)
        glColor3f(0.63, 0.67, 0.70)
        for i in range(4):
            glPushMatrix()
            glRotatef(i * 90.0 + 45.0, 0, 0, 1)
            glTranslatef(0, 0, 0.28)
            glBegin(GL_TRIANGLES)
            glVertex3f(0.050, 0.0, -0.005)
            glVertex3f(0.230, 0.0, -0.13)
            glVertex3f(0.050, 0.0, -0.13)
            glEnd()
            glPopMatrix()

        # Sirip belakang kecil
        glColor3f(0.58, 0.62, 0.65)
        for i in range(4):
            glPushMatrix()
            glRotatef(i * 90.0, 0, 0, 1)
            glBegin(GL_TRIANGLES)
            glVertex3f(0.050, 0.0, -0.02)
            glVertex3f(0.145, 0.0, -0.13)
            glVertex3f(0.050, 0.0, -0.13)
            glEnd()
            glPopMatrix()

        self._draw_markings()

        glPopMatrix()

        # Api nosel
        self._draw_nozzle_fire(x, y, vx, vy)
        self._draw_nozzle_glow(x, y, vx, vy, sim_t)
        gluDeleteQuadric(q)

    def _draw_nozzle_fire(self, mx, my, vx, vy):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        ang_rad  = math.atan2(vy, vx)
        ang_deg  = math.degrees(ang_rad)
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

    def _draw_nozzle_glow(self, mx, my, vx, vy, sim_t):
        ang = math.atan2(vy, vx)
        nx = mx - 0.06 * math.cos(ang)
        ny = my - 0.06 * math.sin(ang)
        pulse = 0.78 + 0.22 * math.sin(sim_t * 55.0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        for i in range(3):
            r = 0.09 + i * 0.03
            a = (0.32 - i * 0.08) * pulse
            glBegin(GL_TRIANGLE_FAN)
            glColor4f(1.0, 0.65, 0.24, a)
            glVertex3f(nx, ny, 0.03)
            for k in range(20):
                t = (k / 19.0) * math.tau
                glColor4f(1.0, 0.35, 0.05, 0.0)
                glVertex3f(nx + math.cos(t) * r, ny + math.sin(t) * r, 0.03)
            glEnd()
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def _draw_markings(self):
        # Emblem + teks di sisi kanan & kiri rudal.
        self._draw_marking_side(+1.0, mirror=False)
        self._draw_marking_side(-1.0, mirror=True)

    def _draw_marking_side(self, side_sign, mirror=False):
        glLineWidth(2.0)
        glColor3f(0.90, 0.08, 0.10)

        # Emblem
        glPushMatrix()
        glTranslatef(0.053 * side_sign, 0.0, 0.36)
        glRotatef(90 if side_sign > 0 else -90, 0, 1, 0)
        if mirror:
            glScalef(-0.20, 0.20, 0.20)
        else:
            glScalef(0.20, 0.20, 0.20)
        glBegin(GL_LINE_STRIP)
        for i in range(16):
            t = i / 15.0
            x = -0.18 + t * 0.14
            y = -0.12 + (t * (1.0 - t)) * 0.38
            glVertex3f(x, y, 0.0)
        glEnd()
        glBegin(GL_LINE_STRIP)
        for i in range(16):
            t = i / 15.0
            x = 0.18 - t * 0.14
            y = -0.12 + (t * (1.0 - t)) * 0.38
            glVertex3f(x, y, 0.0)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(0.0, -0.14, 0.0)
        glVertex3f(0.0, 0.18, 0.0)
        glEnd()
        glPopMatrix()

        # Teks
        glPushMatrix()
        glTranslatef(0.052 * side_sign, 0.0, 0.24)
        glRotatef(90 if side_sign > 0 else -90, 0, 1, 0)
        txt_scale = 0.00042
        if mirror:
            glScalef(-txt_scale, txt_scale, txt_scale)
        else:
            glScalef(txt_scale, txt_scale, txt_scale)
        glColor3f(0.10, 0.10, 0.10)
        for ch in "irsyadku-055":
            glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
        glPopMatrix()
