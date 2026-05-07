"""
============================================================
  SIMULASI PELUNCURAN RUDAL BALISTIK – Grafika Komputer
  Kelompok 58 – Program Studi Informatika, UNSIL 2026
  Menggunakan Python + PyOpenGL + GLUT
============================================================

Instalasi:
    pip install PyOpenGL PyOpenGL_accelerate

Menjalankan:
    python rudal_balistik.py

Kontrol:
    ENTER       – Mulai / Ulang simulasi
    W / S       – Zoom in / out
    A / D       – Putar kamera kiri / kanan
    R           – Reset kamera
    ESC         – Keluar
============================================================
"""

import sys
import math
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *

# ────────────────────────────────────────────────────────────
#  Konstanta fisika & tampilan
# ────────────────────────────────────────────────────────────
GRAVITY   = 9.8        # m/s²
V0        = 80.0       # kecepatan awal (m/s)
ANGLE_DEG = 60.0       # sudut peluncuran (derajat)
SCALE     = 0.05       # konversi meter → unit OpenGL
TIMER_MS  = 16         # ~60 fps
DT        = 0.016      # delta waktu per frame

# ────────────────────────────────────────────────────────────
#  Fungsi fisika balistik
# ────────────────────────────────────────────────────────────
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

# ────────────────────────────────────────────────────────────
#  State global
# ────────────────────────────────────────────────────────────
IDLE, LAUNCHING, FLYING, EXPLODING, FINISHED = 0, 1, 2, 3, 4

state      = IDLE
sim_t      = 0.0       # waktu simulasi berjalan
launch_t   = 0.0       # fase animasi peluncuran
explode_t  = 0.0       # fase ledakan
t_flight   = 0.0       # total waktu terbang
missile_x  = 0.0
missile_y  = 0.0
trail      = []        # list titik jejak [(x,y), ...]
frame_cnt  = 0

# Kamera
cam_dist   = 12.0
cam_angle  = 30.0      # derajat (putar sumbu Y)

# ────────────────────────────────────────────────────────────
#  Reset simulasi
# ────────────────────────────────────────────────────────────
def reset_sim():
    global state, sim_t, launch_t, explode_t, t_flight
    global missile_x, missile_y, trail, frame_cnt
    state      = LAUNCHING
    sim_t      = 0.0
    launch_t   = 0.0
    explode_t  = 0.0
    t_flight   = flight_time()
    missile_x  = 0.0
    missile_y  = 0.05
    trail      = []
    frame_cnt  = 0
    glutTimerFunc(TIMER_MS, on_timer, 0)

# ────────────────────────────────────────────────────────────
#  Timer callback
# ────────────────────────────────────────────────────────────
def on_timer(value):
    global state, sim_t, launch_t, explode_t
    global missile_x, missile_y, trail, frame_cnt

    if state == LAUNCHING:
        launch_t += DT
        if launch_t >= 0.3:
            state  = FLYING
            sim_t  = 0.0
        glutTimerFunc(TIMER_MS, on_timer, 0)

    elif state == FLYING:
        sim_t    += DT
        frame_cnt += 1
        x = pos_x(sim_t) * SCALE
        y = pos_y(sim_t) * SCALE

        missile_x = x
        missile_y = max(0.0, y)

        if frame_cnt % 2 == 0:
            trail.append((missile_x, missile_y))

        if sim_t >= t_flight or y <= 0.0:
            missile_x = pos_x(t_flight) * SCALE
            missile_y = 0.0
            state     = EXPLODING
            explode_t = 0.0
        glutTimerFunc(TIMER_MS, on_timer, 0)

    elif state == EXPLODING:
        explode_t += DT
        if explode_t >= 1.5:
            state = FINISHED
        glutTimerFunc(TIMER_MS, on_timer, 0)

    glutPostRedisplay()

# ────────────────────────────────────────────────────────────
#  Gambar tanah / grid
# ────────────────────────────────────────────────────────────
def draw_ground():
    glLineWidth(1.0)
    glColor3f(0.15, 0.45, 0.15)
    glBegin(GL_LINES)
    for i in range(-20, 21):
        glVertex3f(i * 0.5,  0.0, -5.0)
        glVertex3f(i * 0.5,  0.0,  5.0)
        glVertex3f(-10.0, 0.0, i * 0.5)
        glVertex3f( 10.0, 0.0, i * 0.5)
    glEnd()

    glColor4f(0.1, 0.35, 0.1, 0.5)
    glBegin(GL_QUADS)
    glVertex3f(-10.0, -0.01, -5.0)
    glVertex3f( 10.0, -0.01, -5.0)
    glVertex3f( 10.0, -0.01,  5.0)
    glVertex3f(-10.0, -0.01,  5.0)
    glEnd()

# ────────────────────────────────────────────────────────────
#  Gambar sumbu koordinat
# ────────────────────────────────────────────────────────────
def draw_axes():
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glColor3f(1,0,0); glVertex3f(0,0,0); glVertex3f(2,0,0)   # X merah
    glColor3f(0,1,0); glVertex3f(0,0,0); glVertex3f(0,2,0)   # Y hijau
    glColor3f(0,0,1); glVertex3f(0,0,0); glVertex3f(0,0,2)   # Z biru
    glEnd()
    glLineWidth(1.0)

# ────────────────────────────────────────────────────────────
#  Gambar launcher
# ────────────────────────────────────────────────────────────
def draw_launcher():
    q = gluNewQuadric()

    # platform
    glPushMatrix()
    glColor3f(0.4, 0.4, 0.4)
    glScalef(0.4, 0.1, 0.4)
    glutSolidCube(1.0)
    glPopMatrix()

    # laras miring
    glPushMatrix()
    glTranslatef(0.0, 0.1, 0.0)
    glRotatef(ANGLE_DEG, 0.0, 0.0, 1.0)
    glTranslatef(0.0, 0.25, 0.0)
    glColor3f(0.3, 0.3, 0.3)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(q, 0.04, 0.04, 0.5, 12, 1)
    glPopMatrix()

    gluDeleteQuadric(q)

# ────────────────────────────────────────────────────────────
#  Gambar rudal
# ────────────────────────────────────────────────────────────
def draw_missile(x, y):
    vx  = V0 * math.cos(angle_rad())
    vy  = V0 * math.sin(angle_rad()) - GRAVITY * sim_t

    def normalize3(vx_, vy_, vz_):
        l = math.sqrt(vx_ * vx_ + vy_ * vy_ + vz_ * vz_)
        if l < 1e-8:
            return (0.0, 1.0, 0.0)
        return (vx_ / l, vy_ / l, vz_ / l)

    def cross(a, b):
        return (
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        )

    q = gluNewQuadric()

    glPushMatrix()
    glTranslatef(x, y, 0.0)
    forward = normalize3(vx, vy, 0.0)
    world_up = (0.0, 1.0, 0.0)
    right = cross(world_up, forward)
    if math.sqrt(right[0] * right[0] + right[1] * right[1] + right[2] * right[2]) < 1e-6:
        world_up = (0.0, 0.0, 1.0)
        right = cross(world_up, forward)
    right = normalize3(*right)
    up = normalize3(*cross(forward, right))

    rot = [
        right[0], right[1], right[2], 0.0,
        up[0], up[1], up[2], 0.0,
        forward[0], forward[1], forward[2], 0.0,
        0.0, 0.0, 0.0, 1.0,
    ]
    glMultMatrixf(rot)

    # badan
    glColor3f(0.85, 0.2, 0.2)
    gluCylinder(q, 0.055, 0.055, 0.35, 16, 1)

    # kepala kerucut (hulu ledak)
    glPushMatrix()
    glTranslatef(0, 0, 0.35)
    glColor3f(0.95, 0.95, 0.1)
    gluCylinder(q, 0.055, 0.0, 0.15, 16, 1)
    glPopMatrix()

    # tutup belakang
    glPushMatrix()
    glColor3f(0.5, 0.1, 0.1)
    gluDisk(q, 0.0, 0.055, 16, 1)
    glPopMatrix()

    # nosel
    glPushMatrix()
    glTranslatef(0, 0, -0.06)
    glColor3f(0.2, 0.2, 0.2)
    gluCylinder(q, 0.04, 0.065, 0.06, 16, 1)
    glPopMatrix()

    # sirip (4 buah)
    glColor3f(0.6, 0.15, 0.15)
    for i in range(4):
        glPushMatrix()
        glRotatef(i * 90.0, 0, 0, 1)
        glBegin(GL_TRIANGLES)
        glVertex3f(0.055,  0.0,  0.0)
        glVertex3f(0.18,   0.0, -0.12)
        glVertex3f(0.055,  0.0, -0.12)
        glEnd()
        glPopMatrix()

    glPopMatrix()
    gluDeleteQuadric(q)

# ────────────────────────────────────────────────────────────
#  Gambar jejak lintasan
# ────────────────────────────────────────────────────────────
def draw_trail():
    if len(trail) < 2:
        return
    glLineWidth(2.0)
    glBegin(GL_LINE_STRIP)
    n = len(trail)
    for i, (tx, ty) in enumerate(trail):
        alpha = i / n
        glColor3f(1.0, 0.4 + 0.6 * alpha, 0.0)
        glVertex3f(tx, ty, 0.0)
    glEnd()
    glLineWidth(1.0)

# ────────────────────────────────────────────────────────────
#  Efek ledakan
# ────────────────────────────────────────────────────────────
def draw_explosion(x, y):
    r         = explode_t * 1.5
    intensity = max(0.0, 1.0 - explode_t / 1.2)

    glPushMatrix()
    glTranslatef(x, y, 0.0)

    # bola cahaya
    glColor3f(1.0, 0.6 * intensity, 0.0)
    glutSolidSphere(r * 0.3, 16, 16)

    # cincin partikel
    n_part = 32
    glPointSize(5.0)
    glBegin(GL_POINTS)
    for i in range(n_part):
        a  = i * 2 * math.pi / n_part
        pr = r * (0.5 + 0.5 * math.sin(a * 3))
        px = pr * math.cos(a)
        py = pr * math.sin(a)
        glColor3f(intensity, intensity * 0.3, 0.0)
        glVertex3f(px, py, 0.0)
    glEnd()
    glPointSize(1.0)

    glPopMatrix()

# ────────────────────────────────────────────────────────────
#  Lintasan teoretis (putus-putus)
# ────────────────────────────────────────────────────────────
def draw_theoretical_path():
    tf    = t_flight if t_flight > 0 else flight_time()
    steps = 80
    glLineWidth(1.0)
    glLineStipple(2, 0xAAAA)
    glEnable(GL_LINE_STIPPLE)
    glColor3f(0.35, 0.35, 1.0)
    glBegin(GL_LINE_STRIP)
    for i in range(steps + 1):
        tt = tf * i / steps
        glVertex3f(pos_x(tt) * SCALE, max(0.0, pos_y(tt)) * SCALE, 0.0)
    glEnd()
    glDisable(GL_LINE_STIPPLE)

# ────────────────────────────────────────────────────────────
#  Target (lingkaran merah)
# ────────────────────────────────────────────────────────────
def draw_target():
    tx = max_range() * SCALE
    q  = gluNewQuadric()
    glPushMatrix()
    glTranslatef(tx, 0.02, 0.0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(1.0, 0.0, 0.0)
    gluDisk(q, 0.0,  0.15, 32, 1)
    glColor3f(1.0, 1.0, 1.0)
    gluDisk(q, 0.08, 0.11, 32, 1)
    glColor3f(1.0, 0.0, 0.0)
    gluDisk(q, 0.0,  0.04, 32, 1)
    glPopMatrix()
    gluDeleteQuadric(q)

# ────────────────────────────────────────────────────────────
#  HUD teks
# ────────────────────────────────────────────────────────────
def draw_text(x, y, text, r=1.0, g=1.0, b=1.0):
    glColor3f(r, g, b)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))

def draw_hud():
    w = glutGet(GLUT_WINDOW_WIDTH)
    h = glutGet(GLUT_WINDOW_HEIGHT)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

    # judul
    draw_text(10, h-20, "SIMULASI PELUNCURAN RUDAL BALISTIK  –  Kelompok 58", 0.95, 0.9, 0.2)
    draw_text(10, h-38, "Python + PyOpenGL  |  Grafika Komputer  |  UNSIL 2026", 0.65, 0.65, 0.65)

    # info fisika
    draw_text(10, h-62, f"Sudut Peluncuran : {ANGLE_DEG:.0f} derajat", 0.8, 1.0, 0.8)
    draw_text(10, h-78, f"Kecepatan Awal   : {V0:.0f} m/s",            0.8, 1.0, 0.8)
    draw_text(10, h-94, f"Jangkauan Maks   : {max_range():.1f} m",     0.8, 1.0, 0.8)
    draw_text(10, h-110,f"Waktu Terbang    : {flight_time():.2f} s",   0.8, 1.0, 0.8)

    # status
    status_map = {
        IDLE:      ("[ IDLE ]  Tekan ENTER untuk mulai",    0.7,  0.7,  0.7),
        LAUNCHING: ("[ LAUNCHING ]  Rudal bersiap...",      0.2,  0.8,  1.0),
        FLYING:    ("[ FLYING ]  Rudal meluncur!",          0.2,  1.0,  0.2),
        EXPLODING: ("[ EXPLODING ]  TARGET TERKENA!",       1.0,  0.3,  0.0),
        FINISHED:  ("[ SELESAI ]  Tekan ENTER untuk ulang", 0.95, 0.95, 0.1),
    }
    txt, sr, sg, sb = status_map[state]
    draw_text(10, 40, txt, sr, sg, sb)

    if state in (FLYING, EXPLODING, FINISHED):
        cur_y = max(0.0, pos_y(sim_t))
        draw_text(10, 22, f"Waktu : {sim_t:.2f} s / {t_flight:.2f} s")
        draw_text(10,  6, f"Posisi Rudal : X = {pos_x(sim_t):.1f} m   Y = {cur_y:.1f} m")

    # kontrol
    draw_text(w-230, h-20, "W/S: Zoom  A/D: Putar  R: Reset kamera", 0.55, 0.55, 0.55)
    draw_text(w-230, h-36, "ENTER: Mulai/Ulang        ESC: Keluar",   0.55, 0.55, 0.55)

    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

# ────────────────────────────────────────────────────────────
#  Display callback
# ────────────────────────────────────────────────────────────
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    w = glutGet(GLUT_WINDOW_WIDTH)
    h = glutGet(GLUT_WINDOW_HEIGHT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, w / max(h, 1), 0.01, 200.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # posisi kamera mengitari tengah lintasan
    rad    = math.radians(cam_angle)
    center = max_range() * SCALE * 0.5
    ex     = center + cam_dist * math.sin(rad)
    ey     = cam_dist * 0.5
    ez     = cam_dist * math.cos(rad)
    gluLookAt(ex, ey, ez,
              center, 0.8, 0.0,
              0.0,    1.0, 0.0)

    # ── Dunia ──
    draw_ground()
    draw_axes()
    draw_launcher()
    draw_theoretical_path()
    draw_trail()
    draw_target()

    if state == FLYING:
        draw_missile(missile_x, missile_y)
    elif state == EXPLODING:
        draw_explosion(missile_x, missile_y)
    elif state == LAUNCHING:
        draw_missile(0.0, 0.05)

    draw_hud()
    glutSwapBuffers()

# ────────────────────────────────────────────────────────────
#  Reshape
# ────────────────────────────────────────────────────────────
def reshape(w, h):
    glViewport(0, 0, w, max(h, 1))

# ────────────────────────────────────────────────────────────
#  Keyboard
# ────────────────────────────────────────────────────────────
def keyboard(key, x, y):
    global cam_dist, cam_angle

    if key == b'\r' or key == b'\n':          # ENTER
        if state in (IDLE, FINISHED):
            reset_sim()
    elif key == b'\x1b':                      # ESC
        sys.exit(0)
    elif key in (b'w', b'W'):
        cam_dist = max(3.0, cam_dist - 0.5)
    elif key in (b's', b'S'):
        cam_dist = min(30.0, cam_dist + 0.5)
    elif key in (b'a', b'A'):
        cam_angle -= 5.0
    elif key in (b'd', b'D'):
        cam_angle += 5.0
    elif key in (b'r', b'R'):
        cam_dist  = 12.0
        cam_angle = 30.0

    glutPostRedisplay()

# ────────────────────────────────────────────────────────────
#  Main
# ────────────────────────────────────────────────────────────
def main():
    print("=" * 50)
    print("  SIMULASI PELUNCURAN RUDAL BALISTIK")
    print("  Kelompok 58 – UNSIL 2026")
    print("=" * 50)
    print(f"  Sudut      : {ANGLE_DEG:.0f} derajat")
    print(f"  V0         : {V0:.0f} m/s")
    print(f"  Jangkauan  : {max_range():.1f} m")
    print(f"  Waktu      : {flight_time():.2f} detik")
    print("-" * 50)
    print("  ENTER = Mulai   ESC = Keluar")
    print("  W/S = Zoom      A/D = Putar kamera")
    print("=" * 50)

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1100, 660)
    glutInitWindowPosition(80, 60)
    glutCreateWindow(b"Simulasi Rudal Balistik - Kelompok 58 - UNSIL 2026")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.05, 0.05, 0.15, 1.0)   # langit malam

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)

    glutMainLoop()

if __name__ == "__main__":
    main()
