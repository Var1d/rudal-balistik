"""
particle_system.py
============================================================
  Sistem Partikel VFX – Asap Trail & Ledakan Epik
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
============================================================
"""

import math, random
from OpenGL.GL import *


class Particle:
    __slots__ = ("x","y","vx","vy","life","max_life",
                 "size","r","g","b","gravity","is_smoke")

    def __init__(self, x, y, vx, vy, life, size,
                 r, g, b, gravity=0.0, is_smoke=False):
        self.x = x;  self.y = y
        self.vx = vx; self.vy = vy
        self.life = life; self.max_life = life
        self.size = size
        self.r = r; self.g = g; self.b = b
        self.gravity = gravity
        self.is_smoke = is_smoke

    def update(self, dt):
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        self.vy -= self.gravity * dt
        self.life -= dt
        if self.is_smoke:
            self.size += dt * 0.07

    @property
    def alive(self):
        return self.life > 0 and self.y >= -0.5

    @property
    def alpha(self):
        return max(0.0, self.life / self.max_life)


class ParticleSystem:
    MAX_SMOKE = 500
    MAX_EXPL  = 700

    def __init__(self):
        self.smoke = []
        self.expl  = []
        self.fire  = []
        self._stimer = 0.0
        self._ftimer = 0.0

    def reset(self):
        self.smoke.clear()
        self.expl.clear()
        self.fire.clear()
        self._stimer = 0.0
        self._ftimer = 0.0

    def update(self, dt):
        for p in self.smoke: p.update(dt)
        for p in self.expl:  p.update(dt)
        for p in self.fire:  p.update(dt)
        self.smoke = [p for p in self.smoke if p.alive]
        self.expl  = [p for p in self.expl  if p.alive]
        self.fire  = [p for p in self.fire  if p.alive]

    # ── Emisi asap nosel ───────────────────────────────────
    def emit_smoke(self, x, y, dt):
        self._stimer += dt
        if self._stimer < 0.025: return
        self._stimer = 0.0
        if len(self.smoke) >= self.MAX_SMOKE: return

        for _ in range(4):
            vx   = random.uniform(-0.25, 0.0)
            vy   = random.uniform(-0.05, 0.15)
            life = random.uniform(0.35, 0.8)
            sz   = random.uniform(0.03, 0.08)
            if random.random() < 0.4:
                r,g,b = random.uniform(0.9,1.0), random.uniform(0.3,0.6), 0.0
            else:
                s = random.uniform(0.45, 0.75); r=g=b=s
            self.smoke.append(
                Particle(x, y, vx, vy, life, sz, r,g,b,
                         gravity=0.4, is_smoke=True))

    def emit_launch_smoke(self, x, y, dt):
        """Asap tebal di tanah saat rudal bersiap meluncur."""
        self._stimer += dt
        if self._stimer < 0.015: return
        self._stimer = 0.0
        if len(self.smoke) >= self.MAX_SMOKE + 200: return

        for _ in range(12):
            # Menyebar horizontal di tanah
            vx   = random.uniform(-1.8, 1.2)
            vz   = random.uniform(-1.0, 1.0) # Meskipun Particle hanya x,y, kita bisa simulasikan
            vy   = random.uniform(0.05, 0.5)
            life = random.uniform(0.8, 1.8)
            sz   = random.uniform(0.08, 0.18)
            
            # Warna abu-abu kecoklatan (asap tanah)
            c = random.uniform(0.3, 0.6)
            r, g, b = c, c*0.95, c*0.85
            
            # Kita gunakan Particle yang ada, tapi karena ini ground smoke, 
            # gravitasi negatif sedikit supaya asapnya naik perlahan.
            p = Particle(x + random.uniform(-0.1, 0.1), y, vx, vy, life, sz, r, g, b, 
                         gravity=-0.15, is_smoke=True)
            self.smoke.append(p)

    # ── Ledakan besar ──────────────────────────────────────
    def trigger_explosion(self, x, y):
        self.expl.clear()
        # Kilatan inti
        for _ in range(100):
            a = random.uniform(0, 2*math.pi)
            s = random.uniform(1.0, 5.0)
            self.expl.append(Particle(
                x, y, s*math.cos(a), s*math.sin(a),
                random.uniform(0.2,0.6), random.uniform(0.04,0.12),
                1.0, random.uniform(0.5,1.0), 0.0, gravity=0.0))
        # Puing jatuh
        for _ in range(250):
            a = random.uniform(0, 2*math.pi)
            s = random.uniform(0.4, 4.0)
            self.expl.append(Particle(
                x, y, s*math.cos(a)*0.8, s*abs(math.sin(a)),
                random.uniform(0.7, 2.0), random.uniform(0.02,0.09),
                random.uniform(0.6,1.0), random.uniform(0.1,0.5), 0.0,
                gravity=9.8))
        # Asap pasca ledakan
        for _ in range(150):
            self.expl.append(Particle(
                x, y, random.uniform(-0.3,0.3), random.uniform(0.5,2.2),
                random.uniform(0.9, 2.2), random.uniform(0.1,0.22),
                *([random.uniform(0.15,0.4)]*3),
                gravity=-0.25, is_smoke=True))
        # Api kebakaran yang bertahan lebih lama
        for _ in range(110):
            self.fire.append(Particle(
                x + random.uniform(-0.45, 0.45), y + random.uniform(0.0, 0.09),
                random.uniform(-0.25, 0.25), random.uniform(0.8, 2.5),
                random.uniform(1.6, 3.6), random.uniform(0.06, 0.16),
                1.0, random.uniform(0.30, 0.85), 0.04,
                gravity=1.3, is_smoke=False))

    def emit_ground_fire(self, x, y, dt):
        self._ftimer += dt
        if self._ftimer < 0.03:
            return
        self._ftimer = 0.0
        if len(self.fire) > 500:
            return
        for _ in range(8):
            self.fire.append(Particle(
                x + random.uniform(-0.50, 0.50), y + random.uniform(0.0, 0.03),
                random.uniform(-0.22, 0.22), random.uniform(0.7, 2.0),
                random.uniform(0.7, 1.5), random.uniform(0.05, 0.12),
                1.0, random.uniform(0.2, 0.7), 0.0,
                gravity=1.2, is_smoke=False))

    # ── Render asap ────────────────────────────────────────
    def draw_smoke(self):
        if not self.smoke: return
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glBegin(GL_QUADS)
        for p in self.smoke:
            a = p.alpha * 0.7
            s = p.size * 0.5
            glColor4f(p.r, p.g, p.b, a)
            glVertex3f(p.x-s, p.y-s, 0.0)
            glVertex3f(p.x+s, p.y-s, 0.0)
            glVertex3f(p.x+s, p.y+s, 0.0)
            glVertex3f(p.x-s, p.y+s, 0.0)
        glEnd()

    # ── Render ledakan ─────────────────────────────────────
    def draw_explosion(self):
        if not self.expl and not self.fire: return
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glBegin(GL_QUADS)
        for p in self.expl:
            s = p.size * 0.5
            glColor4f(p.r, p.g, p.b, p.alpha)
            glVertex3f(p.x-s, p.y-s, 0.05)
            glVertex3f(p.x+s, p.y-s, 0.05)
            glVertex3f(p.x+s, p.y+s, 0.05)
            glVertex3f(p.x-s, p.y+s, 0.05)
        for p in self.fire:
            s = p.size * 0.45
            glColor4f(p.r, p.g, p.b, min(1.0, p.alpha))
            glVertex3f(p.x-s, p.y-s, 0.04)
            glVertex3f(p.x+s, p.y-s, 0.04)
            glColor4f(1.0, 0.1, 0.02, 0.0)
            glVertex3f(p.x+s*0.25, p.y+s*1.9, 0.04)
            glVertex3f(p.x-s*0.25, p.y+s*1.9, 0.04)
        glEnd()
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
