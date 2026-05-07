"""
point_light.py
============================================================
  Point Light Dinamis – Cahaya Ledakan & Efek Muzzle Flash
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Mengelola GL_LIGHT1 dan GL_LIGHT2 sebagai cahaya dinamis:
    - GL_LIGHT1: cahaya ledakan (oranye, positional)
    - GL_LIGHT2: muzzle flash saat launching (putih kilat)
============================================================
"""

import random
from OpenGL.GL import *


class PointLight:
    """Satu sumber cahaya titik (positional) OpenGL."""

    def __init__(self, gl_light_id, color=(1.0, 0.5, 0.0)):
        self.gl_id   = gl_light_id    # misal GL_LIGHT1
        self.color   = color
        self.active  = False
        self.x = 0.0; self.y = 0.0; self.z = 0.0
        self.intensity = 0.0

        # Setup atenuasi
        glLightf(self.gl_id, GL_CONSTANT_ATTENUATION,  0.4)
        glLightf(self.gl_id, GL_LINEAR_ATTENUATION,    0.18)
        glLightf(self.gl_id, GL_QUADRATIC_ATTENUATION, 0.04)
        glDisable(self.gl_id)

    def enable(self, x, y, z, intensity=1.0):
        self.active    = True
        self.x = x; self.y = y; self.z = z
        self.intensity = intensity

    def disable(self):
        self.active    = False
        self.intensity = 0.0
        glDisable(self.gl_id)

    def update(self, dt, decay=1.2):
        """Kurangi intensitas setiap frame (efek padam)."""
        if not self.active:
            return
        self.intensity -= decay * dt
        if self.intensity <= 0.0:
            self.disable()

    def apply(self):
        """Terapkan cahaya ke OpenGL. Panggil sebelum render objek."""
        if not self.active or self.intensity <= 0.0:
            glDisable(self.gl_id)
            return

        glEnable(self.gl_id)
        glLightfv(self.gl_id, GL_POSITION,
                  [self.x, self.y + 0.1, self.z, 1.0])

        # Flicker acak untuk efek api berkedip
        flicker = self.intensity * random.uniform(0.82, 1.0)
        r, g, b = self.color
        glLightfv(self.gl_id, GL_DIFFUSE,
                  [r*flicker, g*flicker, b*flicker, 1.0])
        glLightfv(self.gl_id, GL_SPECULAR,
                  [r*flicker*0.5, g*flicker*0.5, b*flicker*0.5, 1.0])
        glLightfv(self.gl_id, GL_AMBIENT, [0.0, 0.0, 0.0, 1.0])


class LightManager:
    """
    Mengelola semua cahaya dinamis dalam scene.
    Penggunaan:
        lm = LightManager()
        lm.trigger_explosion(mx, 0.0)
        lm.trigger_muzzle(0.0, 0.2)
        # per frame:
        lm.update(dt)
        lm.apply()
    """

    def __init__(self):
        # Cahaya ledakan: oranye merah
        self.explosion = PointLight(GL_LIGHT1, color=(1.0, 0.40, 0.0))
        # Muzzle flash: putih kekuningan
        self.muzzle    = PointLight(GL_LIGHT2, color=(1.0, 0.95, 0.6))

    def trigger_explosion(self, x, y, z=0.0):
        self.explosion.enable(x, y, z, intensity=1.5)

    def trigger_muzzle(self, x, y, z=0.0):
        self.muzzle.enable(x, y, z, intensity=1.0)

    def update(self, dt):
        self.explosion.update(dt, decay=0.9)
        self.muzzle.update(dt, decay=5.0)   # muzzle flash singkat

    def apply(self):
        self.explosion.apply()
        self.muzzle.apply()

    def reset(self):
        self.explosion.disable()
        self.muzzle.disable()
