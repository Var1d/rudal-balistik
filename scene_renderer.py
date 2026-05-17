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
        self.moon_pos        = [-38.0, 32.0, -28.0]
        self.fog_color       = (0.04, 0.06, 0.12)
        self.fog_density     = 0.025
        self.launch_flash_t  = 0.0
        self.scorch_active   = False
        self.scorch_x        = 0.0
        self.scorch_z        = 0.0
        self.terrain_cols    = 140
        self.terrain_rows    = 80
        self.terrain_w       = 260.0
        self.terrain_d       = 140.0
        self.terrain_list_id = None
        # Landing page state
        self._fading         = False
        self._fade_alpha     = 0.0
        # Typewriter effect
        self._type_index     = 0
        self._type_timer     = 0.0
        self._type_speed     = 0.045
        self._type_done      = False
        # Countdown state
        self._countdown      = False
        self._countdown_val  = 3.0
        self._cdown_flash    = 0.0

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

        self.vehicles = []

        # Tempatkan pohon
        random.seed(7)
        self.trees = [
            Tree(x=random.uniform(-40, 60),
                 z=random.uniform(-30, 30),
                 scale=random.uniform(0.8, 1.4))
            for _ in range(40)
        ]

        # Bintang
        random.seed(42)
        self._stars = [
            (random.uniform(-130, 130), random.uniform(5, 60),
             random.uniform(-100, 100), random.uniform(1.2, 3.5),
             random.uniform(0, 6.28), random.uniform(0.4, 2.0))
            for _ in range(250)
        ]

        # Awan
        random.seed(11)
        self._clouds = [
            {
                "x": random.uniform(-140.0, 220.0),
                "y": random.uniform(12.0, 28.0),
                "z": random.uniform(-90.0, 90.0),
                "s": random.uniform(2.0, 5.0),
                "a": random.uniform(0.08, 0.18),
                "spd": random.uniform(0.1, 0.5),
            }
            for _ in range(35)
        ]

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
        if hv < -0.02: return (0.05, 0.18, 0.05)
        if hv < 0.04:  return (0.08, 0.30, 0.08)
        if hv < 0.09:  return (0.15, 0.38, 0.12)
        return (0.35, 0.30, 0.12)

    def _build_terrain_display_list(self):
        if self.terrain_list_id is not None:
            glDeleteLists(self.terrain_list_id, 1)
        self.terrain_list_id = glGenLists(1)
        glNewList(self.terrain_list_id, GL_COMPILE)

        COLS, ROWS = self.terrain_cols, self.terrain_rows
        W, D = self.terrain_w, self.terrain_d
        X0, Z0 = -120.0, -90.0
        dx, dz = W / COLS, D / ROWS

        for row in range(ROWS):
            z0, z1 = Z0 + row * dz, Z0 + (row + 1) * dz
            glBegin(GL_TRIANGLE_STRIP)
            for col_i in range(COLS + 1):
                x = X0 + col_i * dx
                h0, h1 = self._terrain_h(x, z0), self._terrain_h(x, z1)
                n0, n1 = self._terrain_normal(x, z0), self._terrain_normal(x, z1)
                glColor3f(*self._terrain_color(h0)); glNormal3f(*n0); glVertex3f(x, h0, z0)
                glColor3f(*self._terrain_color(h1)); glNormal3f(*n1); glVertex3f(x, h1, z1)
            glEnd()
        glEndList()

    def trigger_impact(self, target_x):
        self.bunker_obj.trigger_destruction(target_x)
        self.scorch_active = True
        self.scorch_x, self.scorch_z = target_x, 0.0

    def reset_effects(self):
        self.bunker_obj.reset()
        self.launch_flash_t, self.scorch_active = 0.0, False

    # ── Pencahayaan ────────────────────────────────────────
    def _setup_lighting(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # LIGHT0 - Cahaya Bulan
        glEnable(GL_LIGHT0)
        ldir = [self.moon_pos[0], self.moon_pos[1], self.moon_pos[2], 0.0]
        glLightfv(GL_LIGHT0, GL_POSITION, ldir)
        glLightfv(GL_LIGHT0, GL_AMBIENT,  [0.12, 0.12, 0.22, 1.0]) # Increased ambient
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  [0.85, 0.88, 1.0, 1.0])  # Increased diffuse
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.60, 0.65, 0.90, 1.0])

        # LIGHT1 - Ledakan
        glDisable(GL_LIGHT1)

    def _update_explosion_light(self, x, y, intensity):
        if intensity <= 0: glDisable(GL_LIGHT1); return
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [x, y+0.1, 0.3, 1.0])
        f = intensity * random.uniform(0.85, 1.0)
        glLightfv(GL_LIGHT1, GL_DIFFUSE,  [f, f*0.4, 0.0, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [f*0.6, f*0.2, 0.0, 1.0])
        glLightfv(GL_LIGHT1, GL_CONSTANT_ATTENUATION,  [0.25]) # Reduced attenuation
        glLightfv(GL_LIGHT1, GL_LINEAR_ATTENUATION,    [0.10])

    def _update_launch_light(self, x, y, intensity):
        if intensity <= 0.0: glDisable(GL_LIGHT2); return
        glEnable(GL_LIGHT2)
        glLightfv(GL_LIGHT2, GL_POSITION, [x - 0.1, y + 0.1, 0.0, 1.0])
        glLightfv(GL_LIGHT2, GL_DIFFUSE,  [1.0*intensity, 0.6*intensity, 0.2*intensity, 1.0])
        glLightfv(GL_LIGHT2, GL_SPECULAR, [0.8*intensity, 0.4*intensity, 0.1*intensity, 1.0])
        glLightfv(GL_LIGHT2, GL_CONSTANT_ATTENUATION, [0.30])
        glLightfv(GL_LIGHT2, GL_LINEAR_ATTENUATION,   [0.20])

    def _apply_common_shader_uniforms(self, shader, point_light_world_pos=(0,0,0), point_light_color=(0,0,0), point_light_intensity=0.0):
        if not shader or not shader.valid: return
        
        # 1. Directional Light (Moon)
        # Transform World Moon Position to View Space Direction
        mv = glGetDoublev(GL_MODELVIEW_MATRIX)
        # Direction to light source in view space
        # directional light W=0.0
        lx = self.moon_pos[0]*mv[0][0] + self.moon_pos[1]*mv[1][0] + self.moon_pos[2]*mv[2][0]
        ly = self.moon_pos[0]*mv[0][1] + self.moon_pos[1]*mv[1][1] + self.moon_pos[2]*mv[2][1]
        lz = self.moon_pos[0]*mv[0][2] + self.moon_pos[1]*mv[1][2] + self.moon_pos[2]*mv[2][2]
        shader.set_uniform_3f("uLightDirVS", lx, ly, lz)
        
        shader.set_uniform_3f("uLightColor", 0.90, 0.92, 1.0)
        shader.set_uniform_3f("uAmbientColor", 0.18, 0.20, 0.30) # Brighter ambient
        shader.set_uniform_3f("uSpecColor", 0.85, 0.90, 1.0)
        shader.set_uniform_f("uShininess", 64.0)
        
        # 2. Point Light (Missile/Explosion)
        # Transform World Point Position to View Space
        px, py, pz = point_light_world_pos
        vx = px*mv[0][0] + py*mv[1][0] + pz*mv[2][0] + mv[3][0]
        vy = px*mv[0][1] + py*mv[1][1] + pz*mv[2][1] + mv[3][1]
        vz = px*mv[0][2] + py*mv[1][2] + pz*mv[2][2] + mv[3][2]
        shader.set_uniform_3f("uPointLightPosVS", vx, vy, vz)
        shader.set_uniform_3f("uPointLightColor", *point_light_color)
        shader.set_uniform_f("uPointLightIntensity", point_light_intensity)

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

        tx = max_range_m * scale
        self.bunker_obj.update(dt)
        
        self._draw_sky()
        self._draw_terrain_base() # Base terrain with rough shader
        
        # Prepare point light data
        pl_pos = (0,0,0)
        pl_col = (0,0,0)
        pl_int = 0.0
        
        if state in (FLYING, LAUNCHING):
            pl_pos = (missile_x, missile_y, 0.0) if state == FLYING else (0.0, 0.05, 0.0)
            boost = 0.8 + 0.2 * math.sin(self._star_time * 45.0)
            pl_int = (0.7 if state == FLYING else 1.2) * boost
            pl_col = (1.0, 0.7, 0.3)
        elif state == EXPLODING:
            pl_pos = (missile_x, 0.1, 0.0)
            pl_int = max(0.0, 2.0 - explode_t * 1.5)
            pl_col = (1.0, 0.4, 0.1)

        # Apply lighting to models
        if self.shader_default and self.shader_default.valid:
            self.shader_default.use()
            self._apply_common_shader_uniforms(self.shader_default, pl_pos, pl_col, pl_int)
            self.shader_default.set_uniform_i("useTexture", 1)

        for tree in self.trees: tree.draw(self.tex)
        self.launcher_obj.draw(angle_deg, self.tex)
        self.bunker_obj.draw(tx, self.tex)

        # Draw missile
        if state in (FLYING, LAUNCHING):
            mx, my = (0.0, 0.05) if state == LAUNCHING else (missile_x, missile_y)
            if self.shader_default and self.shader_default.valid:
                self.shader_default.set_uniform_i("useTexture", 0)
            self.missile_obj.draw(mx, my, sim_t, v0, gravity, angle_rad_fn(), scale, self.tex)
            self._update_launch_light(mx, my, pl_int)
            particles.draw_smoke()
        elif state == EXPLODING:
            self._update_explosion_light(missile_x, 0.1, pl_int)
            self._update_launch_light(missile_x, missile_y, 0.0)
            particles.draw_explosion()
        else:
            self._update_launch_light(missile_x, missile_y, 0.0)

        # Re-apply rough shader to terrain if needed (here we draw scorched mark)
        self._draw_terrain_fx(pl_pos, pl_col, pl_int)

        ShaderProgram.use_fixed()
        glDisable(GL_LIGHTING)
        self._draw_hud(state, sim_t, t_flight, missile_x, missile_y, 
                       max_range_m, angle_deg, v0, gravity, scale, angle_rad_fn,
                       IDLE, FLYING, EXPLODING, LAUNCHING, FINISHED,
                       cam_mode, mouse_locked)
        glEnable(GL_LIGHTING)

    def _draw_terrain_base(self):
        # We need to call this after sky to have the ModelView matrix set up for _apply_common_shader_uniforms
        # but before drawing other things.
        # Actually, in render(), _draw_sky() is called first.
        if self.shader_rough and self.shader_rough.valid:
            self.shader_rough.use()
            # We don't have point light info yet here in the original flow? 
            # Let's call it with default 0 first or move terrain drawing.
            self._apply_common_shader_uniforms(self.shader_rough)
            self.shader_rough.set_uniform_i("useTexture", 0)
        else: glDisable(GL_LIGHTING)
        if self.terrain_list_id is not None: glCallList(self.terrain_list_id)

    def _draw_terrain_fx(self, pl_pos, pl_col, pl_int):
        # Redraw terrain with point light influence for better look
        if self.shader_rough and self.shader_rough.valid:
            self.shader_rough.use()
            self._apply_common_shader_uniforms(self.shader_rough, pl_pos, pl_col, pl_int)
            self.shader_rough.set_uniform_i("useTexture", 0)
            if self.terrain_list_id is not None: glCallList(self.terrain_list_id)

        if self.scorch_active:
            glDisable(GL_LIGHTING); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            for i in range(3):
                r, a = 0.5 + i*0.25, 0.25 - i*0.07
                glBegin(GL_TRIANGLE_FAN); glColor4f(0.04, 0.02, 0.01, a); glVertex3f(self.scorch_x, 0.015, self.scorch_z)
                for k in range(36):
                    t = (k/35.0)*math.tau
                    glColor4f(0.06, 0.04, 0.02, 0.0); glVertex3f(self.scorch_x+math.cos(t)*r, 0.015, self.scorch_z+math.sin(t)*r*0.6)
                glEnd()
            glEnable(GL_LIGHTING)

    def _draw_sky(self):
        glDepthMask(GL_FALSE)
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)

        # Stars
        glBegin(GL_POINTS)
        for (sx,sy,sz,ssz,phase,freq) in self._stars:
            b = 0.6 + 0.4*math.sin(self._star_time*freq+phase)
            glColor4f(b, b, b*0.9, b*0.8)
            glVertex3f(sx, sy, sz)
        glEnd()

        # Clouds
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        for c in self._clouds:
            c["x"] += c["spd"] * 0.016
            if c["x"] > 240.0: c["x"] = -180.0
            s, y = c["s"], c["y"] + 0.5 * math.sin(self._star_time * 0.5 + c["z"])
            glBegin(GL_QUADS)
            glColor4f(0.7, 0.8, 1.0, c["a"]); glVertex3f(c["x"]-s, y-s*0.3, c["z"])
            glVertex3f(c["x"]+s, y-s*0.3, c["z"])
            glColor4f(0.7, 0.8, 1.0, 0.0); glVertex3f(c["x"]+s*0.5, y+s*0.5, c["z"])
            glVertex3f(c["x"]-s*0.5, y+s*0.5, c["z"])
            glEnd()

        # Moon 3D & Halo
        glPushMatrix()
        glTranslatef(*self.moon_pos)
        # Halo
        glDisable(GL_DEPTH_TEST)
        glBegin(GL_TRIANGLE_FAN)
        glColor4f(0.8, 0.9, 1.0, 0.25)
        glVertex3f(0, 0, 0)
        glColor4f(0.1, 0.1, 0.3, 0.0)
        for k in range(33):
            a = (k/32.0)*math.tau
            glVertex3f(math.cos(a)*5.0, math.sin(a)*5.0, 0)
        glEnd()
        glEnable(GL_DEPTH_TEST)
        # Moon Sphere
        glRotatef(self._star_time * 1.5, 0, 1, 0)
        glRotatef(-90, 1, 0, 0)
        self.tex.bind(self.tex.moon)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        q = gluNewQuadric(); gluQuadricTexture(q, GL_TRUE)
        gluSphere(q, 1.8, 32, 32); gluDeleteQuadric(q)
        self.tex.unbind()
        glPopMatrix()

        glDepthMask(GL_TRUE); glEnable(GL_LIGHTING)

    def _draw_terrain(self):
        if self.shader_rough and self.shader_rough.valid:
            self.shader_rough.use()
            self._apply_common_shader_uniforms(self.shader_rough)
            self.shader_rough.set_uniform_i("useTexture", 0)
        else: glDisable(GL_LIGHTING)
        if self.terrain_list_id is not None: glCallList(self.terrain_list_id)

        if self.scorch_active:
            glDisable(GL_LIGHTING); glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            for i in range(3):
                r, a = 0.5 + i*0.25, 0.25 - i*0.07
                glBegin(GL_TRIANGLE_FAN); glColor4f(0.04, 0.02, 0.01, a); glVertex3f(self.scorch_x, 0.015, self.scorch_z)
                for k in range(36):
                    t = (k/35.0)*math.tau
                    glColor4f(0.06, 0.04, 0.02, 0.0); glVertex3f(self.scorch_x+math.cos(t)*r, 0.015, self.scorch_z+math.sin(t)*r*0.6)
                glEnd()
            glEnable(GL_LIGHTING)
        ShaderProgram.use_fixed()

    def _draw_theoretical_path(self, t_flight, scale, angle_rad_fn, v0, gravity,
                                FLYING, EXPLODING, FINISHED, state):
        if state not in (FLYING, EXPLODING, FINISHED): return
        glDisable(GL_LIGHTING); tf = t_flight if t_flight > 0 else 1.0
        glLineStipple(2, 0xAAAA); glEnable(GL_LINE_STIPPLE); glColor3f(0.3, 0.4, 1.0); glBegin(GL_LINE_STRIP)
        for i in range(81):
            tt = tf*i/80; px = v0*math.cos(angle_rad_fn())*tt*scale
            py = max(0.0, (v0*math.sin(angle_rad_fn())*tt - 0.5*gravity*tt*tt))*scale; glVertex3f(px, py, 0.0)
        glEnd(); glDisable(GL_LINE_STIPPLE); glEnable(GL_LIGHTING)

    def _draw_text(self, x, y, text, r=1.0, g=1.0, b=1.0):
        glColor3f(r, g, b); glRasterPos2f(x, y)
        for ch in text: glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))

    def _draw_hud(self, state, sim_t, t_flight, mx, my, max_range_m, angle_deg, v0, gravity, scale, angle_rad_fn,
                  IDLE, FLYING, EXPLODING, LAUNCHING, FINISHED, cam_mode, mouse_locked):
        from camera import CAM_NAMES, CAM_FREE
        w, h = glutGet(GLUT_WINDOW_WIDTH), glutGet(GLUT_WINDOW_HEIGHT)
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity(); gluOrtho2D(0, w, 0, h)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity(); glDisable(GL_DEPTH_TEST)
        self._draw_text(10, h-22, "SIMULASI PELUNCURAN RUDAL BALISTIK  –  Kelompok 58", 0.95, 0.9, 0.2)
        self._draw_text(10, h-40, "Python + PyOpenGL  |  Grafika Komputer  |  UNSIL 2026", 0.6, 0.6, 0.6)
        self._draw_text(10, h-65, f"Sudut : {angle_deg:.0f} deg   V0 : {v0:.0f} m/s   Jangkauan : {max_range_m:.1f} m", 0.75, 1.0, 0.75)
        self._draw_text(10, h-85, f"KAMERA: {CAM_NAMES[cam_mode]}" + (" (Klik untuk kunci mouse)" if cam_mode==CAM_FREE and not mouse_locked else ""), 0.5, 0.8, 1.0)
        status_map = { IDLE: ("[ IDLE ]  Tekan ENTER untuk mulai", 0.7,0.7,0.7), LAUNCHING: ("[ LAUNCHING ]  Rudal bersiap...", 0.2,0.8,1.0),
                       FLYING: ("[ FLYING ]  Rudal meluncur!", 0.2,1.0,0.2), EXPLODING: ("[ EXPLODING ]  TARGET TERKENA!", 1.0,0.3,0.0),
                       FINISHED: ("[ SELESAI ]  Tekan ENTER untuk ulang", 0.95,0.95,0.1) }
        txt, sr, sg, sb = status_map[state]; self._draw_text(10, 42, txt, sr, sg, sb)
        if state in (FLYING, EXPLODING, FINISHED):
            py = max(0.0, v0*math.sin(angle_rad_fn())*sim_t - 0.5*gravity*sim_t*sim_t)
            self._draw_text(10, 24, f"Waktu : {sim_t:.2f} s / {t_flight:.2f} s"); self._draw_text(10, 6, f"Posisi : X={v0*math.cos(angle_rad_fn())*sim_t:.1f} m  Y={py:.1f} m")
        self._draw_text(w-320, h-22, "KONTROL DASAR:", 0.8, 0.8, 0.8); self._draw_text(w-320, h-38, "1/2/3/4 : Ganti Kamera", 0.6, 0.6, 0.6); self._draw_text(w-320, h-54, "ENTER   : Mulai/Ulang", 0.6, 0.6, 0.6)
        if cam_mode == CAM_FREE:
            self._draw_text(w-320, h-95, "FREE CAM:", 0.8, 0.8, 0.8); self._draw_text(w-320, h-111, "W/S : Maju/Mundur", 0.6, 0.6, 0.6)
            self._draw_text(w-320, h-127, "A/D : Geser Kiri/Kanan", 0.6, 0.6, 0.6); self._draw_text(w-320, h-143, "SPACE/SHIFT : Naik/Turun", 0.6, 0.6, 0.6)
        elif cam_mode == 3:  # CAM_ORBIT
            self._draw_text(w-320, h-95, "ORBIT CAM:", 0.8, 0.8, 0.8); self._draw_text(w-320, h-111, "W/S : Zoom In/Out", 0.6, 0.6, 0.6)
            self._draw_text(w-320, h-127, "A/D : Putar Kiri/Kanan", 0.6, 0.6, 0.6); self._draw_text(w-320, h-143, "R   : Reset Kamera", 0.6, 0.6, 0.6)
        glEnable(GL_DEPTH_TEST); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW); glPopMatrix()

    def _draw_axes(self):
        glDisable(GL_LIGHTING); glLineWidth(2.0); glBegin(GL_LINES)
        glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(2,0,0); glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,2,0); glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,2)
        glEnd(); glLineWidth(1.0); glEnable(GL_LIGHTING)

    # ── Landing Page ───────────────────────────────────────
    def render_landing(self):
        w = glutGet(GLUT_WINDOW_WIDTH)
        h = glutGet(GLUT_WINDOW_HEIGHT)

        # Setup proyeksi 3D untuk background
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / max(h, 1), 0.01, 300.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0.0, 7.0, 14.0,  0.0, 0.8, 0.0,  0.0, 1.0, 0.0)

        # Lapis 1 & 2: langit + terrain
        self._draw_sky()
        self._draw_terrain()

        # Lapis 3: launcher + pohon di background
        glEnable(GL_LIGHTING)
        self.launcher_obj.draw(60.0, self.tex)
        if self.shader_default and self.shader_default.valid:
            self.shader_default.use()
            self._apply_common_shader_uniforms(self.shader_default)
            self.shader_default.set_uniform_i("useTexture", 1)
        for tree in self.trees:
            tree.draw(self.tex)
        ShaderProgram.use_fixed()

        # Lapis 4: overlay 2D
        glDisable(GL_LIGHTING)
        glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
        gluOrtho2D(0, w, 0, h)
        glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self._draw_scanline(w, h)

        if self._countdown:
            self._draw_countdown(w, h)
        else:
            self._draw_landing_overlay(w, h)

        # Fade-out overlay hitam
        if self._fading:
            glBegin(GL_QUADS)
            glColor4f(0.0, 0.0, 0.0, min(1.0, self._fade_alpha))
            glVertex2f(0, 0); glVertex2f(w, 0)
            glVertex2f(w, h); glVertex2f(0, h)
            glEnd()

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
        glEnable(GL_LIGHTING)

    def _draw_countdown(self, w, h):
        """Tampilkan angka countdown besar di tengah layar."""
        val  = self._countdown_val
        num  = int(math.ceil(max(val, 0.0)))
        frac = val - int(val) if val > 0 else 1.0
        alpha = min(1.0, frac * 2.0)
        cx, cy = w // 2, h // 2

        # Overlay gelap
        glBegin(GL_QUADS)
        glColor4f(0.0, 0.0, 0.0, 0.60)
        glVertex2f(0, 0); glVertex2f(w, 0)
        glVertex2f(w, h); glVertex2f(0, h)
        glEnd()

        if val > 0.0:
            label = str(num)
            tx = cx - len(label) * 9
            glColor4f(0.30, 0.95, 0.22, alpha)
            glRasterPos2f(tx, cy)
            for ch in label:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
            sub_map = {3: "BERSIAP...", 2: "SIAP!", 1: "API !!!"}
            sub = sub_map.get(num, "")
            glColor4f(0.65, 0.85, 0.55, alpha * 0.85)
            glRasterPos2f(cx - len(sub) * 4, cy - 28)
            for ch in sub:
                glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(ch))
        else:
            launch = ">> LUNCURKAN <<"
            blink  = 0.6 + 0.4 * math.sin(self._star_time * 12.0)
            glColor4f(0.95*blink, 0.30*blink, 0.10*blink, 1.0)
            glRasterPos2f(cx - len(launch) * 5, cy)
            for ch in launch:
                glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    def _draw_scanline(self, w, h):
        """Strip hijau transparan bergerak dari atas ke bawah."""
        t = self._star_time
        sy = h * (1.0 - (t * 0.12) % 1.0)
        glBegin(GL_QUADS)
        glColor4f(0.20, 0.65, 0.15, 0.0)
        glVertex2f(0, sy);      glVertex2f(w, sy)
        glColor4f(0.20, 0.65, 0.15, 0.06)
        glVertex2f(w, sy - 40); glVertex2f(0, sy - 40)
        glEnd()

    def _draw_landing_box(self, x, y, bw, bh, r, g, b, a=0.75, border=True):
        """Kotak semi-transparan dengan border hijau militer opsional."""
        glBegin(GL_QUADS)
        glColor4f(r, g, b, a)
        glVertex2f(x,      y);      glVertex2f(x + bw, y)
        glVertex2f(x + bw, y + bh); glVertex2f(x,      y + bh)
        glEnd()
        if border:
            glLineWidth(1.4)
            glBegin(GL_LINE_LOOP)
            glColor4f(0.35, 0.70, 0.22, 0.88)
            glVertex2f(x,      y);      glVertex2f(x + bw, y)
            glVertex2f(x + bw, y + bh); glVertex2f(x,      y + bh)
            glEnd()
            glLineWidth(1.0)

    def _draw_hline(self, x, y, length, r=0.30, g=0.58, b=0.18, a=0.70):
        glLineWidth(1.2)
        glBegin(GL_LINES)
        glColor4f(r, g, b, a)
        glVertex2f(x, y); glVertex2f(x + length, y)
        glEnd()
        glLineWidth(1.0)

    def _ltext(self, x, y, text, r=1.0, g=1.0, b=1.0, a=1.0,
               font=GLUT_BITMAP_8_BY_13):
        glColor4f(r, g, b, a)
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def _draw_landing_overlay(self, w, h):
        t = self._star_time

        # Dimensi panel utama
        panel_w = min(920, w - 60)
        panel_h = min(540, h - 60)
        px = (w - panel_w) // 2
        py = (h - panel_h) // 2

        # ── Panel utama ────────────────────────────────────
        self._draw_landing_box(px, py, panel_w, panel_h,
                               0.01, 0.05, 0.01, 0.80)

        # ── Corner brackets ────────────────────────────────
        L = 20
        glLineWidth(2.2)
        glColor4f(0.38, 0.82, 0.22, 1.0)
        for (cx, cy, sx, sy) in [
            (px,          py,          1,  1),
            (px+panel_w,  py,         -1,  1),
            (px,          py+panel_h,  1, -1),
            (px+panel_w,  py+panel_h, -1, -1),
        ]:
            glBegin(GL_LINES)
            glVertex2f(cx, cy); glVertex2f(cx + sx*L, cy)
            glVertex2f(cx, cy); glVertex2f(cx, cy + sy*L)
            glEnd()
        glLineWidth(1.0)

        # ── Header bar ─────────────────────────────────────
        hbar_y = py + panel_h - 62
        self._draw_landing_box(px+8, hbar_y, panel_w-16, 54,
                               0.04, 0.16, 0.04, 0.92, border=False)
        self._draw_hline(px+8, hbar_y,      panel_w-16)
        self._draw_hline(px+8, hbar_y + 54, panel_w-16)

        # Judul — typewriter effect
        TITLE_FULL = "SIMULASI PELUNCURAN RUDAL BALISTIK 3D"
        if self._type_done:
            pulse   = 0.85 + 0.15 * math.sin(t * 2.0)
            display = TITLE_FULL
            tr, tg, tb = 0.28*pulse, 0.92*pulse, 0.22*pulse
        else:
            display = TITLE_FULL[:self._type_index]
            tr, tg, tb = 0.28, 0.92, 0.22
        cursor  = "_" if (not self._type_done and int(t * 8) % 2 == 0) else ""
        title_x = px + (panel_w - len(TITLE_FULL) * 10) // 2
        self._ltext(title_x, hbar_y + 32, display + cursor,
                    tr, tg, tb, font=GLUT_BITMAP_HELVETICA_18)

        sub   = "Grafika Komputer  |  UNSIL 2026  |  Kelompok 58"
        sub_x = px + (panel_w - len(sub) * 7) // 2
        self._ltext(sub_x, hbar_y + 12, sub,
                    0.50, 0.72, 0.40, font=GLUT_BITMAP_8_BY_13)

        # ── Divider ────────────────────────────────────────
        div1_y = hbar_y - 16
        self._draw_hline(px+8, div1_y, panel_w-16)

        # ── Tabel Anggota ──────────────────────────────────
        tbl_top = div1_y - 14
        tbl_x   = px + 32
        col_nim = tbl_x + 270

        # Header kolom
        self._draw_landing_box(tbl_x-8, tbl_top-2, panel_w-56, 15,
                               0.06, 0.20, 0.05, 0.88, border=False)
        self._ltext(tbl_x,       tbl_top, "NAMA",             0.42, 0.82, 0.28, font=GLUT_BITMAP_8_BY_13)
        self._ltext(col_nim,     tbl_top, "NIM",              0.42, 0.82, 0.28, font=GLUT_BITMAP_8_BY_13)
        self._ltext(col_nim+115, tbl_top, "PANGKAT & JABATAN",0.42, 0.82, 0.28, font=GLUT_BITMAP_8_BY_13)
        self._draw_hline(tbl_x-8, tbl_top-4, panel_w-56, 0.28, 0.55, 0.16)

        members = [
            ("Fiqri Mochamad Fadillah", "247006111051", "Marsekal Muda", "Komandan Operasi",      (0.95, 0.80, 0.20)),
            ("Farid Dhiya Fairuz",      "247006111058", "Kolonel",       "Kepala Navigasi & Kamera",(0.80, 0.82, 0.85)),
            ("Jamal Abdul Nasir",       "247006111015", "Mayor",         "Komandan Lapangan",      (0.40, 0.90, 0.40)),
            ("Irsyad Khoerul Umam",     "247006111055", "Kapten",        "Komandan Medan & Terrain",(0.35, 0.75, 0.30)),
            ("Faisal Hadi Saik",        "247006111052", "Letnan Satu",   "Operator Sistem Senjata", (0.28, 0.60, 0.25)),
        ]
        col_pangkat = col_nim + 115
        row_h = 19
        for i, (nama, nim, pangkat, jabatan, warna) in enumerate(members):
            ry = tbl_top - 18 - i * row_h
            if i % 2 == 0:
                self._draw_landing_box(tbl_x-8, ry-3, panel_w-56, row_h-1,
                                       0.05, 0.13, 0.03, 0.50, border=False)
            # Bullet kotak kecil
            glBegin(GL_QUADS)
            glColor4f(*warna, 0.90)
            glVertex2f(tbl_x-18, ry+2);  glVertex2f(tbl_x-10, ry+2)
            glVertex2f(tbl_x-10, ry+10); glVertex2f(tbl_x-18, ry+10)
            glEnd()
            self._ltext(tbl_x,       ry, nama,                    0.82, 0.94, 0.72, font=GLUT_BITMAP_8_BY_13)
            self._ltext(col_nim,     ry, nim,                     0.60, 0.78, 0.48, font=GLUT_BITMAP_8_BY_13)
            self._ltext(col_pangkat, ry, f"{pangkat} - {jabatan}", *warna,           font=GLUT_BITMAP_8_BY_13)

        # ── Divider tengah ─────────────────────────────────
        div2_y = tbl_top - 18 - len(members) * row_h - 12
        self._draw_hline(px+8, div2_y, panel_w-16)

        # ── Kontrol keyboard ───────────────────────────────
        # Setiap item: tombol di baris atas, deskripsi di baris bawah
        ctrl_items = [
            ("ENTER",   "Mulai/Ulang Simulasi"),
            ("ESC",     "Unlock Mouse/Keluar"),
            ("1/2/3/4", "Free/Chase/Target/Orbit"),
            ("R",       "Reset Kamera"),
            ("W/S",     "Maju/Mundur (Free)"),
            ("A/D",     "Kiri/Kanan (Free)"),
            ("SPACE/SHIFT", "Naik/Turun (Free)"),
            ("Mouse",   "Lihat Sekitar (Free)"),
            ("W/S",     "Zoom In/Out (Orbit)"),
            ("A/D",     "Putar Kiri/Kanan (Orbit)"),
            ("↑↓←→",    "Menoleh (Free)"),
        ]
        n_cols   = 4
        col_w    = (panel_w - 32) // n_cols
        row_h_ctrl = 34          # tinggi per item (tombol + deskripsi)
        n_rows   = (len(ctrl_items) + n_cols - 1) // n_cols
        box_h    = n_rows * row_h_ctrl + 16
        ctrl_top = div2_y - 14  # Y atas kotak kontrol
        self._draw_landing_box(px+8, ctrl_top - box_h, panel_w-16, box_h,
                               0.03, 0.10, 0.02, 0.78)
        for i, (k, v) in enumerate(ctrl_items):
            col = i % n_cols
            row = i // n_cols
            kx  = px + 16 + col * col_w
            # tombol di baris atas item
            key_y  = ctrl_top - 18 - row * row_h_ctrl
            # deskripsi di baris bawah item
            desc_y = key_y - 16
            self._ltext(kx, key_y,  f"[ {k} ]",
                        0.32, 0.88, 0.22, font=GLUT_BITMAP_8_BY_13)
            self._ltext(kx, desc_y, v,
                        0.60, 0.75, 0.50, font=GLUT_BITMAP_8_BY_13)

        # ── Prompt ENTER berkedip ──────────────────────────
        blink    = 0.5 + 0.5 * math.sin(t * 3.5)
        prompt   = ">>  TEKAN  ENTER  UNTUK  MULAI  <<"
        prompt_x = px + (panel_w - len(prompt) * 7) // 2
        prompt_y = py + 10
        self._ltext(prompt_x, prompt_y, prompt,
                    0.30*blink, 0.90*blink, 0.20*blink,
                    font=GLUT_BITMAP_8_BY_13)
