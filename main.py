"""
============================================================
  OPENGL_RUDAL – Simulasi Peluncuran Rudal Balistik 3D
  Kelompok 58 – Program Studi Informatika – UNSIL 2026
============================================================
  Struktur Project:
    main.py              – Entry point, GLUT init & loop
    camera.py            – Sistem kamera multi-mode
    scene_renderer.py    – Render scene utama
    shader_program.py    – Loader & compiler GLSL shader
    particle_system.py   – Sistem partikel VFX
    mesh.py              – Loader OBJ mesh generik

    objects/
      missile/           – Model & logika rudal
      launcher/          – Model launcher kendaraan
      bunker/            – Model bunker/gedung target
      vehicle/           – Kendaraan militer pendukung
      tree/              – Vegetasi pohon

    shaders/             – File GLSL (.vert / .frag)
    textures/            – File gambar (.png / .jpg)

  Kontrol:
    ENTER       – Mulai / Ulang simulasi
    1/2/3/4     – Ganti mode kamera
    W/S         – Zoom in/out
    A/D         – Putar kamera
    R           – Reset kamera
    ESC         – Keluar
============================================================
  Instalasi:
    pip install PyOpenGL PyOpenGL_accelerate Pillow numpy
============================================================
"""

import sys
import math
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *

# ── Import modul internal ────────────────────────────────
from camera          import Camera, CAM_FREE, CAM_CHASE, CAM_TARGET, CAM_ORBIT
from particle_system import ParticleSystem
from scene_renderer  import SceneRenderer
from shader_program  import ShaderProgram

# ────────────────────────────────────────────────────────
#  Konstanta fisika & simulasi
# ────────────────────────────────────────────────────────
GRAVITY    = 9.8
V0         = 80.0
ANGLE_DEG  = 60.0
SCALE      = 0.05
TIMER_MS   = 16
DT         = 0.016

# ────────────────────────────────────────────────────────
#  State simulasi
# ────────────────────────────────────────────────────────
IDLE, LAUNCHING, FLYING, EXPLODING, FINISHED = 0, 1, 2, 3, 4

state      = IDLE
sim_t      = 0.0
launch_t   = 0.0
explode_t  = 0.0
t_flight   = 0.0
missile_x  = 0.0
missile_y  = 0.0
frame_cnt  = 0

# ────────────────────────────────────────────────────────
#  Inisialisasi subsistem global
# ────────────────────────────────────────────────────────
camera   = Camera()
particles = ParticleSystem()
renderer  = None   # diisi setelah OpenGL context siap

# ────────────────────────────────────────────────────────
#  Fisika balistik
# ────────────────────────────────────────────────────────
def angle_rad():
    return math.radians(ANGLE_DEG)

def pos_x(t):
    return V0 * math.cos(angle_rad()) * t

def pos_y(t):
    return V0 * math.sin(angle_rad()) * t - 0.5 * GRAVITY * t * t

def flight_time():
    return 2.0 * V0 * math.sin(angle_rad()) / GRAVITY

def max_range():
    return V0 * V0 * math.sin(2.0 * angle_rad()) / GRAVITY

# ────────────────────────────────────────────────────────
#  Slow-motion: aktif saat rudal hampir mendarat
# ────────────────────────────────────────────────────────
def get_dt():
    if state == FLYING:
        y_world = pos_y(sim_t)
        if y_world < 2.0:
            return DT * 0.15   # 15% kecepatan → slow-motion
    return DT

# ────────────────────────────────────────────────────────
#  Reset simulasi
# ────────────────────────────────────────────────────────
def reset_sim():
    global state, sim_t, launch_t, explode_t, t_flight
    global missile_x, missile_y, frame_cnt
    state      = LAUNCHING
    sim_t      = 0.0
    launch_t   = 0.0
    explode_t  = 0.0
    t_flight   = flight_time()
    missile_x  = 0.0
    missile_y  = 0.05
    frame_cnt  = 0
    particles.reset()
    camera.reset()
    glutTimerFunc(TIMER_MS, on_timer, 0)

# ────────────────────────────────────────────────────────
#  Timer callback
# ────────────────────────────────────────────────────────
def on_timer(value):
    global state, sim_t, launch_t, explode_t
    global missile_x, missile_y, frame_cnt

    dt_eff = get_dt()

    if state == LAUNCHING:
        launch_t += dt_eff
        if launch_t >= 0.3:
            state = FLYING
            sim_t = 0.0
        glutTimerFunc(TIMER_MS, on_timer, 0)

    elif state == FLYING:
        sim_t     += dt_eff
        frame_cnt += 1
        x = pos_x(sim_t) * SCALE
        y = pos_y(sim_t) * SCALE
        missile_x = x
        missile_y = max(0.0, y)

        # Emisi asap dari nosel
        vx_w = V0 * math.cos(angle_rad())
        vy_w = V0 * math.sin(angle_rad()) - GRAVITY * sim_t
        particles.emit_smoke(missile_x, missile_y, dt_eff)

        # Update kamera chase
        camera.update(
            dt_eff, state, missile_x, missile_y,
            vx_w * SCALE, vy_w * SCALE,
            max_range() * SCALE,
            IDLE, FLYING, EXPLODING, FINISHED
        )

        if sim_t >= t_flight or pos_y(sim_t) <= 0.0:
            missile_x = pos_x(t_flight) * SCALE
            missile_y = 0.0
            particles.trigger_explosion(missile_x, missile_y)
            state     = EXPLODING
            explode_t = 0.0
        glutTimerFunc(TIMER_MS, on_timer, 0)

    elif state == EXPLODING:
        explode_t += dt_eff
        particles.update(dt_eff)
        camera.update(
            dt_eff, state, missile_x, missile_y,
            0.0, 0.0, max_range() * SCALE,
            IDLE, FLYING, EXPLODING, FINISHED
        )
        if explode_t >= 2.5:
            state = FINISHED
        glutTimerFunc(TIMER_MS, on_timer, 0)

    particles.update(dt_eff)
    glutPostRedisplay()

# ────────────────────────────────────────────────────────
#  Display callback
# ────────────────────────────────────────────────────────
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    w = glutGet(GLUT_WINDOW_WIDTH)
    h = glutGet(GLUT_WINDOW_HEIGHT)

    # Proyeksi perspektif
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, w / max(h, 1), 0.01, 300.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Terapkan kamera
    camera.apply()

    # Render seluruh scene
    renderer.render(
        state        = state,
        missile_x    = missile_x,
        missile_y    = missile_y,
        sim_t        = sim_t,
        explode_t    = explode_t,
        t_flight     = t_flight,
        particles    = particles,
        angle_deg    = ANGLE_DEG,
        v0           = V0,
        gravity      = GRAVITY,
        scale        = SCALE,
        max_range_m  = max_range(),
        angle_rad_fn = angle_rad,
        FLYING       = FLYING,
        EXPLODING    = EXPLODING,
        LAUNCHING    = LAUNCHING,
        IDLE         = IDLE,
        FINISHED     = FINISHED,
    )

    glutSwapBuffers()

# ────────────────────────────────────────────────────────
#  Reshape
# ────────────────────────────────────────────────────────
def reshape(w, h):
    glViewport(0, 0, w, max(h, 1))

# ────────────────────────────────────────────────────────
#  Keyboard
# ────────────────────────────────────────────────────────
def keyboard(key, x, y):
    global cam_dist, cam_angle

    if key in (b'\r', b'\n'):
        if state in (IDLE, FINISHED):
            reset_sim()
    elif key == b'\x1b':
        sys.exit(0)
    elif key in (b'w', b'W'): camera.zoom_in()
    elif key in (b's', b'S'): camera.zoom_out()
    elif key in (b'a', b'A'): camera.rotate_left()
    elif key in (b'd', b'D'): camera.rotate_right()
    elif key in (b'r', b'R'): camera.reset()
    elif key == b'1': camera.set_mode(CAM_FREE)
    elif key == b'2': camera.set_mode(CAM_CHASE)
    elif key == b'3': camera.set_mode(CAM_TARGET)
    elif key == b'4': camera.set_mode(CAM_ORBIT)

    glutPostRedisplay()

# ────────────────────────────────────────────────────────
#  Main
# ────────────────────────────────────────────────────────
def main():
    global renderer

    print("=" * 56)
    print("  OPENGL_RUDAL – Kelompok 58 – UNSIL 2026")
    print("=" * 56)
    print(f"  Sudut     : {ANGLE_DEG:.0f} derajat")
    print(f"  V0        : {V0:.0f} m/s")
    print(f"  Jangkauan : {max_range():.1f} m")
    print(f"  Waktu     : {flight_time():.2f} detik")
    print("-" * 56)
    print("  ENTER=Mulai  ESC=Keluar  1/2/3/4=Kamera")
    print("  W/S=Zoom     A/D=Putar   R=Reset kamera")
    print("=" * 56)

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 700)
    glutInitWindowPosition(60, 40)
    glutCreateWindow(b"OPENGL_RUDAL - Simulasi Balistik 3D - Kelompok 58 UNSIL 2026")

    # Setup OpenGL
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_NORMALIZE)
    glClearColor(0.04, 0.04, 0.13, 1.0)

    # Inisialisasi renderer (load tekstur, shader, objek)
    renderer = SceneRenderer()
    renderer.init()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

if __name__ == "__main__":
    main()
