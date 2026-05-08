"""
scene_renderer.py
============================================================
  Render Orchestrator – Mengatur urutan render semua objek
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
============================================================
"""

import math, random
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *

from shader_program          import ShaderProgram
from objects.missile.missile  import Missile
from objects.launcher.launcher import Launcher
from objects.bunker.bunker    import Bunker
from objects.vehicle.vehicle  import Vehicle
from objects.tree.tree        import Tree
from textures_manager         import TextureManager


class SceneRenderer:
    def __init__(self):
        self.shader_default  = None
        self.shader_skybox   = None
        self.shader_rough    = None
        self.tex             = None
        self.missile_obj     = None
        self.launcher_obj    = None
        self.bunker_obj      = None
        self.vehicles        = []
        self.trees           = []
        self._star_time      = 0.0
        self._stars          = []
        self._clouds         = []
        self.fog_color       = (0.06, 0.08, 0.14)
        self.fog_density     = 0.028
        self.launch_flash_t  = 0.0
        self.scorch_active   = False
        self.scorch_x        = 0.0
        self.scorch_z        = 0.0
        self.terrain_cols    = 140
        self.terrain_rows    = 80
        self.terrain_w       = 260.0
        self.terrain_d       = 140.0
        self.terrain_list_id = None

    # ── Inisialisasi setelah OpenGL context siap ──────────
    def init(self):
        # Load shader
        self.shader_default = ShaderProgram("shaders/default_color")
        self.shader_skybox  = ShaderProgram("shaders/skybox")
        self.shader_rough   = ShaderProgram("shaders/rough_color")

        # Load tekstur
        self.tex = TextureManager()
        self.tex.load_all()

        # Inisialisasi objek
        self.missile_obj  = Missile()
        self.launcher_obj = Launcher()
        self.bunker_obj   = Bunker()

        # Kendaraan sisi launcher dikosongkan agar unit militer fokus di area bunker.
        self.vehicles = []

        # Tempatkan pohon di sekitar area
        random.seed(7)
        self.trees = [
            Tree(x=random.uniform(-40, 60),
                 z=random.uniform(-30, 30),
                 scale=random.uniform(0.8, 1.4))
            for _ in range(40)
        ]

        # Generate bintang
        random.seed(42)
        self._stars = [
            (random.uniform(-30,30), random.uniform(3,25),
             random.uniform(-20,20), random.uniform(1.5,4.0),
             random.uniform(0, 6.28), random.uniform(0.5,2.5))
            for _ in range(220)
        ]

        # Awan procedural
        random.seed(11)
        self._clouds = [
            {
                "x": random.uniform(-140.0, 220.0),
                "y": random.uniform(7.0, 22.0),
                "z": random.uniform(-90.0, 90.0),
                "s": random.uniform(1.2, 3.6),
                "a": random.uniform(0.10, 0.22),
                "spd": random.uniform(0.2, 0.9),
            }
            for _ in range(42)
        ]

        # Setup pencahayaan
        self._setup_lighting()
        self._build_terrain_display_list()

        print("[SCENE] Inisialisasi selesai.")

    @staticmethod
    def _terrain_h(x, z):
        v  = 0.55 * math.sin(x * 0.055) * math.cos(z * 0.047)
        v += 0.33 * math.sin((x + z) * 0.082)
        v += 0.24 * math.cos((x - z) * 0.067)
        v += 0.14 * math.sin(x * 0.21 + 0.8) * math.sin(z * 0.19 - 1.1)
        corridor = math.exp(-(z * z) / 1200.0)
        lane = math.exp(-((x - 8.0) * (x - 8.0)) / 2400.0)
        flatten = corridor * lane
        return v * (1.0 - 0.55 * flatten)

    def _terrain_normal(self, x, z):
        e = 0.16
        h_l = self._terrain_h(x - e, z)
        h_r = self._terrain_h(x + e, z)
        h_d = self._terrain_h(x, z - e)
        h_u = self._terrain_h(x, z + e)
        nx = h_l - h_r
        ny = 2.0 * e
        nz = h_d - h_u
        inv = 1.0 / max(math.sqrt(nx * nx + ny * ny + nz * nz), 1e-6)
        return (nx * inv, ny * inv, nz * inv)

    def _terrain_color(self, hv):
        if hv < -0.02:
            return (0.06, 0.22, 0.06)
        if hv < 0.04:
            return (0.10, 0.35, 0.10)
        if hv < 0.09:
            return (0.18, 0.42, 0.14)
        return (0.38, 0.32, 0.14)

    def _build_terrain_display_list(self):
        if self.terrain_list_id is not None:
            glDeleteLists(self.terrain_list_id, 1)
        self.terrain_list_id = glGenLists(1)
        glNewList(self.terrain_list_id, GL_COMPILE)

        COLS, ROWS = self.terrain_cols, self.terrain_rows
        W, D = self.terrain_w, self.terrain_d
        X0, Z0 = -120.0, -90.0
        dx = W / COLS
        dz = D / ROWS

        for row in range(ROWS):
            z0 = Z0 + row * dz
            z1 = Z0 + (row + 1) * dz
            glBegin(GL_TRIANGLE_STRIP)
            for col_i in range(COLS + 1):
                x = X0 + col_i * dx
                h0 = self._terrain_h(x, z0)
                h1 = self._terrain_h(x, z1)
                n0 = self._terrain_normal(x, z0)
                n1 = self._terrain_normal(x, z1)
                c0 = self._terrain_color(h0)
                c1 = self._terrain_color(h1)
                glColor3f(*c0); glNormal3f(*n0); glVertex3f(x, h0, z0)
                glColor3f(*c1); glNormal3f(*n1); glVertex3f(x, h1, z1)
            glEnd()

        glEndList()

    def trigger_impact(self, target_x):
        self.bunker_obj.trigger_destruction(target_x)
        self.scorch_active = True
        self.scorch_x = target_x
        self.scorch_z = 0.0

    def reset_effects(self):
        self.bunker_obj.reset()
        self.launch_flash_t = 0.0
        self.scorch_active = False

    # ── Pencahayaan ────────────────────────────────────────
    def _setup_lighting(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # GL_LIGHT0 – bulan malam (directional)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 2.5, 1.5, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.04, 0.04, 0.10, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.50, 0.50, 0.60, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.25, 0.25, 0.45, 1.0])

        # GL_LIGHT1 – cahaya ledakan (awalnya mati)
        glDisable(GL_LIGHT1)

    def _update_explosion_light(self, x, y, intensity):
        if intensity <= 0:
            glDisable(GL_LIGHT1); return
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [x, y+0.1, 0.3, 1.0])
        f = intensity * random.uniform(0.85, 1.0)
        glLightfv(GL_LIGHT1, GL_DIFFUSE,  [f, f*0.5, 0.0, 1.0])
        glLightfv(GL_LIGHT1, GL_CONSTANT_ATTENUATION,  [0.4])
        glLightfv(GL_LIGHT1, GL_LINEAR_ATTENUATION,    [0.2])

    def _update_launch_light(self, x, y, intensity):
        if intensity <= 0.0:
            glDisable(GL_LIGHT2)
            return
        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, [x - 0.08, y, 0.0, 1.0])
        glLightfv(GL_LIGHT2, GL_DIFFUSE,  [1.0 * intensity, 0.55 * intensity, 0.20 * intensity, 1.0])
        glLightfv(GL_LIGHT2, GL_SPECULAR, [0.9 * intensity, 0.5 * intensity, 0.25 * intensity, 1.0])
        glLightfv(GL_LIGHT2, GL_CONSTANT_ATTENUATION, [0.45])
        glLightfv(GL_LIGHT2, GL_LINEAR_ATTENUATION,   [0.35])

    def _apply_common_shader_uniforms(self, shader):
        if not shader or not shader.valid:
            return
        shader.set_uniform_3f("uLightDirVS", 1.0, 2.5, 1.5)
        shader.set_uniform_3f("uLightColor", 0.78, 0.80, 0.92)
        shader.set_uniform_3f("uAmbientColor", 0.12, 0.13, 0.18)
        shader.set_uniform_3f("uSpecColor", 1.0, 0.98, 0.95)
        shader.set_uniform_f("uShininess", 40.0)
        shader.set_uniform_3f("uFogColor", *self.fog_color)
        shader.set_uniform_f("uFogDensity", self.fog_density)

    # ── Render utama ───────────────────────────────────────
    def render(self, state, missile_x, missile_y, sim_t,
               explode_t, t_flight, particles,
               angle_deg, v0, gravity, scale,
               max_range_m, angle_rad_fn,
               FLYING, EXPLODING, LAUNCHING, IDLE, FINISHED,
               cam_mode=0, mouse_locked=False):

        dt = 0.016
        self._star_time += dt

        tx = max_range_m * scale   # posisi X target dalam unit OpenGL
        self.bunker_obj.update(dt)
        if state == LAUNCHING:
            self.launch_flash_t = min(1.0, self.launch_flash_t + dt * 3.5)
        else:
            self.launch_flash_t = max(0.0, self.launch_flash_t - dt * 1.8)

        # 1. Langit & bintang (depth write off)
        self._draw_sky()

        # 2. Terrain berbukit
        self._draw_terrain()

        # 3. Sumbu koordinat (debug visual)
        self._draw_axes()

        # 4. Pohon
        if self.shader_default and self.shader_default.valid:
            self.shader_default.use()
            self._apply_common_shader_uniforms(self.shader_default)
            self.shader_default.set_uniform_i("useTexture", 1)
        for tree in self.trees:
            tree.draw(self.tex)

        # 5. Launcher
        self.launcher_obj.draw(angle_deg, self.tex)

        # 6. Kendaraan militer (launcher-side opsional; saat ini kosong)
        for veh in self.vehicles:
            veh.draw(self.tex)

        # 7. Bunker target
        self.bunker_obj.draw(tx, self.tex)

        # 8. Lintasan teoretis (garis putus-putus)
        self._draw_theoretical_path(t_flight, scale,
                                     angle_rad_fn, v0, gravity,
                                     FLYING, EXPLODING, FINISHED, state)

        # 9. Rudal / Ledakan
        if state in (FLYING, LAUNCHING):
            mx = 0.0 if state == LAUNCHING else missile_x
            my = 0.05 if state == LAUNCHING else missile_y
            if self.shader_default and self.shader_default.valid:
                self.shader_default.set_uniform_i("useTexture", 0)
            self.missile_obj.draw(mx, my, sim_t, v0, gravity,
                                  angle_rad_fn(), scale, self.tex)
            boost = 0.75 + 0.25 * math.sin(self._star_time * 40.0)
            self._update_launch_light(mx, my, (0.6 if state == FLYING else 1.0) * boost)
            particles.draw_smoke()

        elif state == EXPLODING:
            intensity = max(0.0, 1.0 - explode_t / 1.5)
            self._update_explosion_light(missile_x, 0.0, intensity)
            self._update_launch_light(missile_x, missile_y, 0.0)
            particles.draw_explosion()
        else:
            self._update_launch_light(missile_x, missile_y, 0.0)

        ShaderProgram.use_fixed()

        # 10. HUD (2D overlay, lighting mati)
        glDisable(GL_LIGHTING)
        self._draw_hud(state, sim_t, t_flight, missile_x,
                       missile_y, max_range_m, angle_deg, v0,
                       gravity, scale, angle_rad_fn,
                       IDLE, FLYING, EXPLODING, LAUNCHING, FINISHED,
                       cam_mode, mouse_locked)
        glEnable(GL_LIGHTING)

    # ── Sky & Bintang ──────────────────────────────────────
    def _draw_sky(self):
        glDepthMask(GL_FALSE)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)

        # Bintang kecil (satu pass)
        glBegin(GL_POINTS)
        for (sx,sy,sz,ssz,phase,freq) in self._stars:
            b = 0.55 + 0.45*math.sin(self._star_time*freq+phase)
            glColor4f(b, b, b*0.9, b*0.9)
            glVertex3f(sx, sy, sz)
        glEnd()

        # Bintang besar (titik lebih besar)
        for (sx,sy,sz,ssz,phase,freq) in self._stars:
            if ssz > 3.0:
                b = 0.7 + 0.3*math.sin(self._star_time*freq+phase)
                glPointSize(ssz)
                glBegin(GL_POINTS)
                glColor4f(b, b, 0.85, b)
                glVertex3f(sx, sy, sz)
                glEnd()
        glPointSize(1.0)

        # Awan lembut
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for c in self._clouds:
            c["x"] += c["spd"] * 0.016
            if c["x"] > 240.0:
                c["x"] = -170.0
            s = c["s"]
            y = c["y"] + 0.3 * math.sin(self._star_time * 0.8 + c["z"])
            glBegin(GL_QUADS)
            glColor4f(0.78, 0.85, 0.95, c["a"])
            glVertex3f(c["x"] - s, y - s * 0.30, c["z"])
            glVertex3f(c["x"] + s, y - s * 0.30, c["z"])
            glColor4f(0.78, 0.85, 0.95, 0.0)
            glVertex3f(c["x"] + s * 0.5, y + s * 0.45, c["z"])
            glVertex3f(c["x"] - s * 0.5, y + s * 0.45, c["z"])
            glEnd()

        # Bulan sabit
        q = gluNewQuadric()
        glPushMatrix()
        glTranslatef(-22.0, 16.0, -14.0)
        glRotatef(-90, 1, 0, 0)
        glColor4f(0.98, 0.96, 0.80, 0.95)
        gluDisk(q, 0.0, 1.1, 32, 1)
        glTranslatef(0.35, 0.0, -0.01)
        glColor4f(0.03, 0.03, 0.10, 1.0)
        gluDisk(q, 0.0, 0.92, 32, 1)
        glPopMatrix()
        gluDeleteQuadric(q)

        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)

    # ── Terrain berbukit ───────────────────────────────────
    def _draw_terrain(self):
        if self.shader_rough and self.shader_rough.valid:
            self.shader_rough.use()
            self._apply_common_shader_uniforms(self.shader_rough)
            self.shader_rough.set_uniform_i("useTexture", 0)
        else:
            glDisable(GL_LIGHTING)
        if self.terrain_list_id is not None:
            glCallList(self.terrain_list_id)

        if self.scorch_active:
            # Bekas terbakar di titik impact.
            glDisable(GL_LIGHTING)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            for i in range(3):
                r = 0.50 + i * 0.22
                a = 0.20 - i * 0.05
                glBegin(GL_TRIANGLE_FAN)
                glColor4f(0.05, 0.03, 0.02, a)
                glVertex3f(self.scorch_x, 0.012 + i * 0.0005, self.scorch_z)
                for k in range(36):
                    t = (k / 35.0) * math.tau
                    glColor4f(0.08, 0.05, 0.03, 0.0)
                    glVertex3f(
                        self.scorch_x + math.cos(t) * r,
                        0.012 + i * 0.0005,
                        self.scorch_z + math.sin(t) * r * 0.65
                    )
                glEnd()
            glEnable(GL_LIGHTING)

        ShaderProgram.use_fixed()
        glEnable(GL_LIGHTING)

    # ── Sumbu koordinat ────────────────────────────────────
    def _draw_axes(self):
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(2,0,0)
        glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,2,0)
        glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,2)
        glEnd()
        glLineWidth(1.0)
        glEnable(GL_LIGHTING)

    # ── Lintasan teoritis ──────────────────────────────────
    def _draw_theoretical_path(self, t_flight, scale,
                                angle_rad_fn, v0, gravity,
                                FLYING, EXPLODING, FINISHED, state):
        if state not in (FLYING, EXPLODING, FINISHED):
            return
        glDisable(GL_LIGHTING)
        tf = t_flight if t_flight > 0 else 1.0
        glLineWidth(1.0)
        glLineStipple(2, 0xAAAA)
        glEnable(GL_LINE_STIPPLE)
        glColor3f(0.3, 0.3, 1.0)
        glBegin(GL_LINE_STRIP)
        for i in range(81):
            tt = tf * i / 80
            px = v0 * math.cos(angle_rad_fn()) * tt * scale
            py = max(0.0, (v0*math.sin(angle_rad_fn())*tt
                     - 0.5*gravity*tt*tt)) * scale
            glVertex3f(px, py, 0.0)
        glEnd()
        glDisable(GL_LINE_STIPPLE)
        glEnable(GL_LIGHTING)

    # ── HUD ────────────────────────────────────────────────
    def _draw_text(self, x, y, text, r=1.0, g=1.0, b=1.0):
        glColor3f(r, g, b)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))

    def _draw_hud(self, state, sim_t, t_flight, mx, my,
                  max_range_m, angle_deg, v0, gravity, scale,
                  angle_rad_fn, IDLE, FLYING, EXPLODING,
                  LAUNCHING, FINISHED, cam_mode, mouse_locked):
        from camera import CAM_NAMES, CAM_FREE
        w = glutGet(GLUT_WINDOW_WIDTH)
        h = glutGet(GLUT_WINDOW_HEIGHT)

        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        gluOrtho2D(0, w, 0, h)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
        glDisable(GL_DEPTH_TEST)

        self._draw_text(10, h-22,
            "SIMULASI PELUNCURAN RUDAL BALISTIK  –  Kelompok 58",
            0.95, 0.90, 0.20)
        self._draw_text(10, h-40,
            "Python + PyOpenGL  |  Grafika Komputer  |  UNSIL 2026",
            0.60, 0.60, 0.60)
        self._draw_text(10, h-65,
            f"Sudut : {angle_deg:.0f} deg   V0 : {v0:.0f} m/s   "
            f"Jangkauan : {max_range_m:.1f} m   Waktu : "
            f"{2*v0*math.sin(angle_rad_fn())/gravity:.2f} s",
            0.75, 1.0, 0.75)

        # Info Kamera
        cam_info = f"KAMERA: {CAM_NAMES[cam_mode]}"
        if cam_mode == CAM_FREE and not mouse_locked:
            cam_info += " (Klik untuk kunci mouse)"
        self._draw_text(10, h-85, cam_info, 0.5, 0.8, 1.0)

        status_map = {
            IDLE:      ("[ IDLE ]  Tekan ENTER untuk mulai",   0.7,0.7,0.7),
            LAUNCHING: ("[ LAUNCHING ]  Rudal bersiap...",     0.2,0.8,1.0),
            FLYING:    ("[ FLYING ]  Rudal meluncur!",         0.2,1.0,0.2),
            EXPLODING: ("[ EXPLODING ]  TARGET TERKENA!",      1.0,0.3,0.0),
            FINISHED:  ("[ SELESAI ]  Tekan ENTER untuk ulang",0.95,0.95,0.1),
        }
        txt, sr, sg, sb = status_map[state]
        self._draw_text(10, 42, txt, sr, sg, sb)

        if state in (FLYING, EXPLODING, FINISHED):
            py = max(0.0, v0*math.sin(angle_rad_fn())*sim_t
                     - 0.5*gravity*sim_t*sim_t)
            self._draw_text(10, 24,
                f"Waktu : {sim_t:.2f} s / {t_flight:.2f} s")
            self._draw_text(10, 6,
                f"Posisi : X={v0*math.cos(angle_rad_fn())*sim_t:.1f} m  "
                f"Y={py:.1f} m")

        # Bantuan Kontrol
        self._draw_text(w-320, h-22, "KONTROL DASAR:", 0.8, 0.8, 0.8)
        self._draw_text(w-320, h-38, "1/2/3/4 : Ganti Kamera", 0.6, 0.6, 0.6)
        self._draw_text(w-320, h-54, "ENTER   : Mulai/Ulang", 0.6, 0.6, 0.6)
        self._draw_text(w-320, h-70, "ESC     : Keluar", 0.6, 0.6, 0.6)

        if cam_mode == CAM_FREE:
            self._draw_text(w-320, h-95, "FREE CAM:", 0.8, 0.8, 0.8)
            self._draw_text(w-320, h-111, "W/S : Maju/Mundur", 0.6, 0.6, 0.6)
            self._draw_text(w-320, h-127, "A/D : Geser Kiri/Kanan", 0.6, 0.6, 0.6)
            self._draw_text(w-320, h-143, "Q/E : Naik/Turun", 0.6, 0.6, 0.6)
            self._draw_text(w-320, h-159, "Mouse: Menoleh", 0.6, 0.6, 0.6)
        else:
            self._draw_text(w-320, h-95, "ORBIT CAM:", 0.8, 0.8, 0.8)
            self._draw_text(w-320, h-111, "W/S : Zoom In/Out", 0.6, 0.6, 0.6)
            self._draw_text(w-320, h-127, "A/D : Putar Kiri/Kanan", 0.6, 0.6, 0.6)
            self._draw_text(w-320, h-143, "R   : Reset Kamera", 0.6, 0.6, 0.6)

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
