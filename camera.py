"""
camera.py
============================================================
  Sistem Kamera Multi-Mode
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Mode kamera:
    CAM_FREE   (1) – kontrol manual W/S/A/D
    CAM_CHASE  (2) – mengikuti rudal dari belakang
    CAM_TARGET (3) – menghadap titik target
    CAM_ORBIT  (4) – mengorbit otomatis
============================================================
"""

import math
from OpenGL.GLU import gluLookAt

# ── Konstanta mode ───────────────────────────────────────
CAM_FREE   = 0
CAM_CHASE  = 1
CAM_TARGET = 2
CAM_ORBIT  = 3

CAM_NAMES = {
    CAM_FREE:   "FREE  (W/S/A/D)",
    CAM_CHASE:  "CHASE (ikuti rudal)",
    CAM_TARGET: "TARGET (hadap target)",
    CAM_ORBIT:  "ORBIT (otomatis)",
}


def _lerp(a, b, t):
    return a + (b - a) * t


class Camera:
    """Kamera OpenGL dengan 4 mode dan transisi halus (lerp)."""

    def __init__(self):
        self.mode        = CAM_FREE
        self.dist        = 14.0
        self.angle       = 30.0
        self._orbit_ang  = 30.0
        self._lerp_speed = 5.0

        # Posisi aktif (diupdate tiap frame)
        self.eye  = [0.0, 7.0, 14.0]
        self.look = [0.0, 0.8,  0.0]

        # Target posisi (tujuan lerp)
        self._t_eye  = [0.0, 7.0, 14.0]
        self._t_look = [0.0, 0.8,  0.0]

    # ── Mode ──────────────────────────────────────────────
    def set_mode(self, mode):
        self.mode = mode
        print(f"[KAMERA] {CAM_NAMES[mode]}")

    def reset(self):
        self.mode       = CAM_FREE
        self.dist       = 14.0
        self.angle      = 30.0
        self._orbit_ang = 30.0

    # ── Kontrol manual ─────────────────────────────────────
    def zoom_in(self):    self.dist = max(3.0,  self.dist - 0.6)
    def zoom_out(self):   self.dist = min(35.0, self.dist + 0.6)
    def rotate_left(self):  self.angle -= 5.0
    def rotate_right(self): self.angle += 5.0

    # ── Update per frame ───────────────────────────────────
    def update(self, dt, state_sim, mx, my, mvx, mvy,
               target_x, IDLE, FLYING, EXPLODING, FINISHED):
        """Hitung posisi target kamera, lalu lerp ke sana."""

        if self.mode == CAM_FREE:
            rad    = math.radians(self.angle)
            cx     = target_x * 0.5
            self._t_eye  = [cx + self.dist * math.sin(rad),
                             self.dist * 0.5,
                             self.dist * math.cos(rad)]
            self._t_look = [cx, 0.8, 0.0]

        elif self.mode == CAM_CHASE and state_sim == FLYING:
            spd = math.hypot(mvx, mvy)
            dx, dy = (mvx / spd, mvy / spd) if spd > 0.01 else (1.0, 0.0)
            off = 0.9
            self._t_eye  = [mx - dx * off, my - dy * off + 0.4, 0.7]
            self._t_look = [mx + dx * 0.6, my + dy * 0.6, 0.0]

        elif self.mode == CAM_TARGET:
            self._t_eye  = [target_x + 2.5, 1.8, 2.5]
            self._t_look = [target_x, 0.0, 0.0]

        elif self.mode == CAM_ORBIT:
            self._orbit_ang += 18.0 * dt
            rad = math.radians(self._orbit_ang)
            cx  = target_x * 0.5
            self._t_eye  = [cx + self.dist * math.sin(rad),
                             self.dist * 0.45,
                             self.dist * math.cos(rad)]
            self._t_look = [cx, 0.8, 0.0]

        # Auto-switch saat meledak
        if state_sim == EXPLODING and self.mode == CAM_CHASE:
            self.set_mode(CAM_TARGET)

        # Lerp halus
        t = min(1.0, self._lerp_speed * dt)
        for i in range(3):
            self.eye[i]  = _lerp(self.eye[i],  self._t_eye[i],  t)
            self.look[i] = _lerp(self.look[i], self._t_look[i], t)

    # ── Apply ke OpenGL ────────────────────────────────────
    def apply(self):
        gluLookAt(
            self.eye[0],  self.eye[1],  self.eye[2],
            self.look[0], self.look[1], self.look[2],
            0.0, 1.0, 0.0
        )
