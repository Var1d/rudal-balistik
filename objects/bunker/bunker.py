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

import math
import random
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *


class Bunker:
    def __init__(self):
        self.destroyed = False
        self.fragments = []
        self._fire_spots = []

    def reset(self):
        self.destroyed = False
        self.fragments = []
        self._fire_spots = []

    def trigger_destruction(self, target_x):
        if self.destroyed:
            return
        self.destroyed = True
        self.fragments = []
        random.seed(99)

        size = 0.055
        for _ in range(140):
            ox = random.uniform(-0.35, 0.35)
            oy = random.uniform(0.08, 0.70)
            oz = random.uniform(-0.30, 0.30)
            ang = random.uniform(0.0, math.tau)
            spd = random.uniform(0.6, 3.2)
            vx = math.cos(ang) * spd
            vy = random.uniform(1.2, 4.5)
            vz = math.sin(ang) * spd * 0.9
            self.fragments.append({
                "x": target_x + ox, "y": oy, "z": oz,
                "vx": vx, "vy": vy, "vz": vz,
                "rot": random.uniform(0.0, 360.0),
                "rotv": random.uniform(-260.0, 260.0),
                "size": size * random.uniform(0.75, 1.35),
                "alive": True,
            })

        self._fire_spots = [
            (target_x + random.uniform(-0.35, 0.35),
             random.uniform(0.0, 0.03),
             random.uniform(-0.30, 0.30),
             random.uniform(0.12, 0.22))
            for _ in range(16)
        ]
        self._spawn_support_fragments(target_x)

    def _spawn_support_fragments(self, target_x):
        # Fragmen tambahan dari bendera, mobil militer, dan tank.
        for _ in range(90):
            ox = random.uniform(-0.75, 0.80)
            oy = random.uniform(0.02, 0.72)
            oz = random.uniform(-0.55, 0.55)
            ang = random.uniform(0.0, math.tau)
            spd = random.uniform(0.5, 2.6)
            self.fragments.append({
                "x": target_x + ox, "y": oy, "z": oz,
                "vx": math.cos(ang) * spd, "vy": random.uniform(0.8, 3.6), "vz": math.sin(ang) * spd,
                "rot": random.uniform(0.0, 360.0), "rotv": random.uniform(-320.0, 320.0),
                "size": 0.035 * random.uniform(0.8, 1.45), "alive": True,
            })

    def update(self, dt):
        if not self.destroyed:
            return
        for f in self.fragments:
            if not f["alive"]:
                continue
            f["x"] += f["vx"] * dt
            f["y"] += f["vy"] * dt
            f["z"] += f["vz"] * dt
            f["vy"] -= 9.8 * dt
            f["rot"] += f["rotv"] * dt
            if f["y"] <= 0.0:
                f["y"] = 0.0
                f["vy"] *= -0.22
                f["vx"] *= 0.76
                f["vz"] *= 0.76
                if abs(f["vy"]) < 0.32:
                    f["vy"] = 0.0
                if abs(f["vx"]) + abs(f["vz"]) < 0.10:
                    f["vx"] = 0.0
                    f["vz"] = 0.0

    def _draw_israel_flag(self):
        q = gluNewQuadric()
        glPushMatrix()
        glTranslatef(-0.32, 0.02, 0.28)
        glColor3f(0.70, 0.70, 0.72)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(q, 0.009, 0.009, 0.85, 8, 1)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(-0.31, 0.72, 0.28)
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(0.0,  0.00, 0.0); glVertex3f(0.34, 0.00, 0.0)
        glVertex3f(0.34, 0.18, 0.0); glVertex3f(0.0,  0.18, 0.0)
        glEnd()

        glColor3f(0.08, 0.28, 0.82)
        glBegin(GL_QUADS)
        glVertex3f(0.0,  0.01, 0.001); glVertex3f(0.34, 0.01, 0.001)
        glVertex3f(0.34, 0.04, 0.001); glVertex3f(0.0,  0.04, 0.001)
        glVertex3f(0.0,  0.14, 0.001); glVertex3f(0.34, 0.14, 0.001)
        glVertex3f(0.34, 0.17, 0.001); glVertex3f(0.0,  0.17, 0.001)
        glEnd()

        glTranslatef(0.18, 0.09, 0.002)
        s = 0.048
        glBegin(GL_LINE_LOOP)
        glVertex3f(0.0, s, 0.0)
        glVertex3f(-s * 0.866, -s * 0.5, 0.0)
        glVertex3f(s * 0.866, -s * 0.5, 0.0)
        glEnd()
        glBegin(GL_LINE_LOOP)
        glVertex3f(0.0, -s, 0.0)
        glVertex3f(-s * 0.866, s * 0.5, 0.0)
        glVertex3f(s * 0.866, s * 0.5, 0.0)
        glEnd()
        glPopMatrix()
        gluDeleteQuadric(q)

    def _draw_bunker_vehicles_and_tank(self):
        q = gluNewQuadric()
        for bx, bz in [(-0.58, 0.42), (0.56, -0.45)]:
            glPushMatrix()
            glTranslatef(bx, 0.0, bz)
            glColor3f(0.22, 0.30, 0.14)
            glPushMatrix()
            glTranslatef(0.0, 0.07, 0.0)
            glScalef(0.24, 0.12, 0.12)
            glutSolidCube(1.0)
            glPopMatrix()
            for wx, wz in [(-0.08, 0.07), (-0.08, -0.07), (0.08, 0.07), (0.08, -0.07)]:
                glPushMatrix()
                glTranslatef(wx, 0.04, wz)
                glRotatef(90, 1, 0, 0)
                glColor3f(0.10, 0.10, 0.10)
                gluCylinder(q, 0.03, 0.03, 0.03, 10, 1)
                glPopMatrix()
            glPopMatrix()

        glPushMatrix()
        glTranslatef(0.62, 0.0, 0.36)
        glColor3f(0.20, 0.27, 0.13)
        glPushMatrix()
        glTranslatef(0.0, 0.08, 0.0)
        glScalef(0.36, 0.12, 0.20)
        glutSolidCube(1.0)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.0, 0.16, 0.0)
        glutSolidSphere(0.065, 10, 10)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0.19, 0.16, 0.0)
        glRotatef(90, 0, 1, 0)
        gluCylinder(q, 0.012, 0.012, 0.22, 10, 1)
        glPopMatrix()
        glPopMatrix()
        gluDeleteQuadric(q)

    def draw(self, target_x, tex):
        if self.destroyed:
            self._draw_destroyed(tex)
            return

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

        self._draw_israel_flag()
        self._draw_bunker_vehicles_and_tank()

        glPopMatrix()   # akhir translasi target_x
        gluDeleteQuadric(q)

    def _draw_destroyed(self, tex):
        from textures_manager import TextureManager
        TextureManager.bind(tex.concrete if tex else None)
        for f in self.fragments:
            glPushMatrix()
            glTranslatef(f["x"], f["y"] + f["size"] * 0.5, f["z"])
            glRotatef(f["rot"], 0.3, 0.9, 0.2)
            glColor3f(0.42, 0.40, 0.38)
            s = f["size"]
            glScalef(s, s, s)
            glutSolidCube(1.0)
            glPopMatrix()
        TextureManager.unbind()

        # Mark/bekas ledakan permanen di area bunker (crater + arang)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        mark_x = self._fire_spots[0][0] if self._fire_spots else 0.0
        mark_z = self._fire_spots[0][2] if self._fire_spots else 0.0
        for i in range(4):
            r = 0.55 + i * 0.18
            a = 0.30 - i * 0.06
            glBegin(GL_TRIANGLE_FAN)
            glColor4f(0.04, 0.03, 0.025, a)
            glVertex3f(mark_x, 0.014 + i * 0.0008, mark_z)
            for k in range(42):
                t = (k / 41.0) * math.tau
                glColor4f(0.08, 0.06, 0.04, 0.0)
                cx = mark_x + math.cos(t) * r
                cz = mark_z + math.sin(t) * r * 0.72
                glVertex3f(cx, 0.014 + i * 0.0008, cz)
            glEnd()

        # Cekungan kawah sederhana
        glColor4f(0.02, 0.02, 0.02, 0.65)
        glBegin(GL_TRIANGLE_FAN)
        center_x = mark_x
        center_z = mark_z
        glVertex3f(center_x, 0.012, center_z)
        for k in range(42):
            t = (k / 41.0) * math.tau
            glVertex3f(center_x + math.cos(t) * 0.48, 0.010, center_z + math.sin(t) * 0.30)
        glEnd()
        glEnable(GL_LIGHTING)

        # Kebakaran kecil di sekitar reruntuhan
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        t = glutGet(GLUT_ELAPSED_TIME) * 0.001
        for idx, (x, y, z, base_s) in enumerate(self._fire_spots):
            flicker = 0.75 + 0.25 * math.sin(t * (8.0 + (idx % 5)) + x * 5.0)
            h = base_s * (0.8 + 0.6 * flicker)
            w = base_s * 0.45
            glBegin(GL_QUADS)
            glColor4f(1.0, 0.85, 0.35, 0.9)
            glVertex3f(x - w, y, z)
            glVertex3f(x + w, y, z)
            glColor4f(1.0, 0.25, 0.02, 0.0)
            glVertex3f(x + w * 0.2, y + h, z)
            glVertex3f(x - w * 0.2, y + h, z)
            glEnd()
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
