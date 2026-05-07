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

        # Tempatkan 3 kendaraan militer di scene
        self.vehicles = [
            Vehicle(x=-1.5, z= 0.4),
            Vehicle(x=-2.2, z=-0.3),
            Vehicle(x=-3.0, z= 0.1),
        ]

        # Tempatkan pohon di sekitar area
        random.seed(7)
        self.trees = [
            Tree(x=random.uniform(-8, -1),
                 z=random.uniform(-4, 4),
                 scale=random.uniform(0.8, 1.4))
            for _ in range(20)
        ]
        # Tambah pohon di sisi kanan (dekat target)
        self.trees += [
            Tree(x=random.uniform(5, 9),
                 z=random.uniform(-4, 4),
                 scale=random.uniform(0.7, 1.2))
            for _ in range(10)
        ]

        # Generate bintang
        random.seed(42)
        self._stars = [
            (random.uniform(-30,30), random.uniform(3,25),
             random.uniform(-20,20), random.uniform(1.5,4.0),
             random.uniform(0, 6.28), random.uniform(0.5,2.5))
            for _ in range(380)
        ]

        # Setup pencahayaan
        self._setup_lighting()

        print("[SCENE] Inisialisasi selesai.")

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

    # ── Render utama ───────────────────────────────────────
    def render(self, state, missile_x, missile_y, sim_t,
               explode_t, t_flight, particles,
               angle_deg, v0, gravity, scale,
               max_range_m, angle_rad_fn,
               FLYING, EXPLODING, LAUNCHING, IDLE, FINISHED):

        self._star_time += 0.016

        tx = max_range_m * scale   # posisi X target dalam unit OpenGL

        # 1. Langit & bintang (depth write off)
        self._draw_sky()

        # 2. Terrain berbukit
        self._draw_terrain()

        # 3. Sumbu koordinat (debug visual)
        self._draw_axes()

        # 4. Pohon
        for tree in self.trees:
            tree.draw(self.tex)

        # 5. Launcher
        self.launcher_obj.draw(angle_deg, self.tex)

        # 6. Kendaraan militer
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
            self.missile_obj.draw(mx, my, sim_t, v0, gravity,
                                  angle_rad_fn(), scale, self.tex)
            particles.draw_smoke()

        elif state == EXPLODING:
            intensity = max(0.0, 1.0 - explode_t / 1.5)
            self._update_explosion_light(missile_x, 0.0, intensity)
            particles.draw_explosion()

        # 10. HUD (2D overlay, lighting mati)
        glDisable(GL_LIGHTING)
        self._draw_hud(state, sim_t, t_flight, missile_x,
                       missile_y, max_range_m, angle_deg, v0,
                       gravity, scale, angle_rad_fn,
                       IDLE, FLYING, EXPLODING, LAUNCHING, FINISHED)
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
        glDisable(GL_LIGHTING)
        COLS, ROWS = 60, 30
        W, D = 22.0, 12.0
        X0, Z0 = -11.0, -6.0
        dx = W / COLS
        dz = D / ROWS

        def h(x, z):
            v  = 0.08 * math.sin(x*0.9+0.5) * math.cos(z*1.1)
            v += 0.05 * math.sin(x*1.8-1.0) * math.sin(z*0.7+2.0)
            v += 0.03 * math.cos(x*3.0)     * math.sin(z*2.5)
            flat = math.exp(-x*x*0.5)
            return v * (1.0 - flat*0.8)

        def col(hv):
            if hv < -0.02: return (0.06,0.22,0.06)
            elif hv < 0.04: return (0.10,0.35,0.10)
            elif hv < 0.09: return (0.18,0.42,0.14)
            else:           return (0.38,0.32,0.14)

        for row in range(ROWS):
            glBegin(GL_TRIANGLE_STRIP)
            for col_i in range(COLS+1):
                x  = X0 + col_i*dx
                z0 = Z0 + row*dz
                z1 = Z0 + (row+1)*dz
                h0 = h(x, z0); h1 = h(x, z1)
                c0 = col(h0);  c1 = col(h1)
                glColor3f(*c0); glVertex3f(x, h0, z0)
                glColor3f(*c1); glVertex3f(x, h1, z1)
            glEnd()

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
                  LAUNCHING, FINISHED):
        from camera import CAM_NAMES
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

        self._draw_text(w-270, h-22,
            "1/2/3/4=Kamera  W/S=Zoom  A/D=Putar  R=Reset",
            0.50, 0.50, 0.50)
        self._draw_text(w-270, h-38,
            "ENTER=Mulai/Ulang           ESC=Keluar",
            0.50, 0.50, 0.50)

        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW);  glPopMatrix()
