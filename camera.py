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
import random
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


def _smooth_factor(speed, dt):
    return 1.0 - math.exp(-speed * max(0.0, dt))


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
        self.shake_amp = 0.0
        self.shake_decay = 2.8
        self.shake_x = 0.0
        self.shake_y = 0.0
        self.shake_z = 0.0

        # Free cam (WASD + mouse)
        self.free_pos = [0.0, 7.0, 14.0]
        self.free_yaw = 0.0
        self.free_pitch = 0.0
        self._free_target_yaw = 0.0
        self._free_target_pitch = 0.0
        self.free_vel = [0.0, 0.0, 0.0]
        
        # Kecepatan ditingkatkan sesuai permintaan
        self.free_speed = 35.0
        self.free_rot_speed = 180.0
        self.free_accel = 20.0
        self.free_damping = 12.0
        
        self.free_mouse_sens = 0.14
        self.free_mouse_smooth = 18.0
        self._free_last_mouse = None
        self._free_move = {
            'w': False, 's': False, 'a': False, 'd': False,
            'q': False, 'e': False,
            'up': False, 'down': False, 'left': False, 'right': False
        }

    def free_cam_key(self, key, down):
        if isinstance(key, bytes):
            k = key.decode('utf-8').lower()
        elif isinstance(key, str):
            k = key.lower()
        else:
            k = key
            
        if k in self._free_move:
            self._free_move[k] = down

    def free_cam_mouse(self, dx, dy):
        self._free_target_yaw += dx * self.free_mouse_sens
        self._free_target_pitch -= dy * self.free_mouse_sens
        self._free_target_pitch = max(-89.0, min(89.0, self._free_target_pitch))

    def update_free_cam(self, dt):
        dir_x = dir_y = dir_z = 0.0
        
        # Pergerakan WASD + QE
        if self._free_move['w']: dir_z += 1.0  # Maju
        if self._free_move['s']: dir_z -= 1.0  # Mundur
        if self._free_move['a']: dir_x -= 1.0  # Kiri
        if self._free_move['d']: dir_x += 1.0  # Kanan
        if self._free_move['q']: dir_y += 1.0  # Atas
        if self._free_move['e']: dir_y -= 1.0  # Bawah
        
        # Rotasi Panah (Menoleh)
        if self._free_move['left']:  self._free_target_yaw -= self.free_rot_speed * dt
        if self._free_move['right']: self._free_target_yaw += self.free_rot_speed * dt
        if self._free_move['up']:    self._free_target_pitch += self.free_rot_speed * dt
        if self._free_move['down']:  self._free_target_pitch -= self.free_rot_speed * dt
        
        # Batasi pitch agar tidak jungkir balik
        self._free_target_pitch = max(-89.0, min(89.0, self._free_target_pitch))

        move_len = math.sqrt(dir_x * dir_x + dir_y * dir_y + dir_z * dir_z)
        if move_len > 0.01:
            dir_x /= move_len
            dir_y /= move_len
            dir_z /= move_len

        mouse_t = _smooth_factor(self.free_mouse_smooth, dt)
        self.free_yaw = _lerp(self.free_yaw, self._free_target_yaw, mouse_t)
        self.free_pitch = _lerp(self.free_pitch, self._free_target_pitch, mouse_t)

        yaw_rad = math.radians(self.free_yaw)
        pitch_rad = math.radians(self.free_pitch)

        forward = [
            math.cos(pitch_rad) * math.sin(yaw_rad),
            math.sin(pitch_rad),
            -math.cos(pitch_rad) * math.cos(yaw_rad)
        ]
        right = [
            math.cos(yaw_rad),
            0.0,
            math.sin(yaw_rad)
        ]

        target_vel = [
            (forward[0] * dir_z + right[0] * dir_x) * self.free_speed,
            dir_y * self.free_speed,
            (forward[2] * dir_z + right[2] * dir_x) * self.free_speed,
        ]

        response = self.free_accel if move_len > 0.01 else self.free_damping
        vel_t = _smooth_factor(response, dt)
        for i in range(3):
            self.free_vel[i] = _lerp(self.free_vel[i], target_vel[i], vel_t)
            self.free_pos[i] += self.free_vel[i] * dt

        target_eye = list(self.free_pos)
        target_look = [
            self.free_pos[0] + forward[0],
            self.free_pos[1] + forward[1],
            self.free_pos[2] + forward[2],
        ]

        cam_t = _smooth_factor(self._lerp_speed, dt)
        for i in range(3):
            self.eye[i] = _lerp(self.eye[i], target_eye[i], cam_t)
            self.look[i] = _lerp(self.look[i], target_look[i], cam_t)

    # ── Mode ──────────────────────────────────────────────
    def set_mode(self, mode):
        self.mode = mode
        print(f"[KAMERA] {CAM_NAMES[mode]}")

    def reset(self):
        self.mode       = CAM_FREE
        self.dist       = 14.0
        self.angle      = 30.0
        self._orbit_ang = 30.0
        self.shake_amp  = 0.0
        self.shake_x = self.shake_y = self.shake_z = 0.0
        self.eye  = [0.0, 7.0, 14.0]
        self.look = [0.0, 0.8,  0.0]
        self._t_eye  = [0.0, 7.0, 14.0]
        self._t_look = [0.0, 0.8,  0.0]
        self.free_pos = [0.0, 7.0, 14.0]
        self.free_yaw = 0.0
        self.free_pitch = 0.0
        self._free_target_yaw = 0.0
        self._free_target_pitch = 0.0
        self.free_vel = [0.0, 0.0, 0.0]
        for key in self._free_move:
            self._free_move[key] = False

    def trigger_shake(self, amplitude):
        self.shake_amp = max(self.shake_amp, amplitude)

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
            self.update_free_cam(dt)
            # Smooth shake tetap berlaku
            self._t_eye = list(self.eye)
            self._t_look = list(self.look)

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

        if self.shake_amp > 0.0005:
            self.shake_amp *= math.exp(-self.shake_decay * dt)
            self.shake_x = random.uniform(-1.0, 1.0) * self.shake_amp
            self.shake_y = random.uniform(-1.0, 1.0) * self.shake_amp * 0.75
            self.shake_z = random.uniform(-1.0, 1.0) * self.shake_amp
        else:
            self.shake_amp = 0.0
            self.shake_x = self.shake_y = self.shake_z = 0.0

    # ── Apply ke OpenGL ────────────────────────────────────
    def apply(self):
        gluLookAt(
            self.eye[0] + self.shake_x,  self.eye[1] + self.shake_y,  self.eye[2] + self.shake_z,
            self.look[0] + self.shake_x * 0.5, self.look[1] + self.shake_y * 0.5, self.look[2] + self.shake_z * 0.5,
            0.0, 1.0, 0.0
        )
