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
    W/A/S/D     – Pergerakan kamera (Maju, Kiri, Mundur, Kanan)
    Panah       – Kontrol menoleh (Atas, Bawah, Kiri, Kanan)
    Mouse       – Lihat sekitar saat free-cam
    R           – Reset kamera
    ESC         – Keluar
============================================================
  Instalasi:
    pip install PyOpenGL PyOpenGL_accelerate Pillow numpy
============================================================
"""

import sys
import os
import math
import time
import ctypes
from OpenGL.GL   import *
from OpenGL.GLU  import *
from OpenGL.GLUT import *

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _project_path(path):
    return path if os.path.isabs(path) else os.path.join(_BASE_DIR, path)

# ── Audio (pygame.mixer) ─────────────────────────────────
try:
    import pygame.mixer as _mixer
    _mixer.pre_init(44100, -16, 2, 512)
    _mixer.init()
    _AUDIO_OK = True
except Exception:
    _AUDIO_OK = False

def _load_sound(path):
    path = _project_path(path)
    if not _AUDIO_OK or not os.path.exists(path):
        return None
    try:
        return _mixer.Sound(path)
    except Exception:
        return None

def _play_bgm(path):
    path = _project_path(path)
    if not _AUDIO_OK or not os.path.exists(path):
        return
    try:
        _mixer.music.load(path)
        _mixer.music.set_volume(0.45)
        _mixer.music.play(-1)
    except Exception:
        pass

def _play(sfx):
    if sfx is not None:
        try:
            sfx.play()
        except Exception:
            pass

def _stop_music():
    if not _AUDIO_OK:
        return
    try:
        _mixer.music.fadeout(800)
    except Exception:
        pass

# Preload SFX
_sfx_type    = None
_sfx_beep    = None
_sfx_alert   = None
_sfx_launch  = None
_sfx_explode = None

# State input untuk free cam
mouse_locked = [True]
ignore_mouse_warp = [False]
last_idle_time = [time.perf_counter()]

def lock_mouse():
    mouse_locked[0] = True
    glutSetCursor(GLUT_CURSOR_NONE)
    # Pusatkan mouse di awal lock
    cx = glutGet(GLUT_WINDOW_WIDTH) // 2
    cy = glutGet(GLUT_WINDOW_HEIGHT) // 2
    glutWarpPointer(cx, cy)

def unlock_mouse():
    mouse_locked[0] = False
    glutSetCursor(GLUT_CURSOR_LEFT_ARROW)

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
TIMER_MS   = 8
DT         = 0.008

# ────────────────────────────────────────────────────────
#  State simulasi
# ────────────────────────────────────────────────────────
LANDING = -1
IDLE, LAUNCHING, FLYING, EXPLODING, FINISHED = 0, 1, 2, 3, 4

state      = LANDING
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

def missile_tip_position(mx, my, sim_time):
    # Panjang visual rudal kira-kira: body+cone = 0.74 unit OpenGL.
    tip_len = 0.74
    vx = V0 * math.cos(angle_rad())
    vy = V0 * math.sin(angle_rad()) - GRAVITY * sim_time
    sp = math.hypot(vx, vy)
    if sp < 1e-6:
        fx, fy = 1.0, 0.0
    else:
        fx, fy = vx / sp, vy / sp
    return mx + fx * tip_len, my + fy * tip_len

def tip_hits_bunker(tip_x, tip_y, target_x):
    # AABB bunker (disesuaikan model bunker.py)
    bunker_min_x = target_x - 0.32
    bunker_max_x = target_x + 0.32
    bunker_min_y = 0.08
    bunker_max_y = 0.72
    return bunker_min_x <= tip_x <= bunker_max_x and bunker_min_y <= tip_y <= bunker_max_y

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
    # Simpan posisi FREE cam sebelum reset
    was_free_cam = camera.mode == CAM_FREE
    state      = LAUNCHING
    sim_t      = 0.0
    launch_t   = 0.0
    explode_t  = 0.0
    t_flight   = flight_time()
    missile_x  = 0.0
    missile_y  = 0.05
    frame_cnt  = 0
    particles.reset()
    # Jangan reset kamera jika sedang di FREE mode
    if not was_free_cam:
        camera.reset()
    camera.trigger_shake(0.10)
    if renderer is not None:
        renderer.reset_effects()
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
        # Tambahkan asap di tanah saat persiapan meluncur
        particles.emit_launch_smoke(missile_x, 0.05, dt_eff)
        
        if camera.mode == CAM_FREE:
            camera.update(
                dt_eff, state, missile_x, missile_y,
                0.0, 0.0, max_range() * SCALE,
                IDLE, FLYING, EXPLODING, FINISHED
            )
        if launch_t >= 0.3:
            state = FLYING
            sim_t = 0.0
            _play(_sfx_launch)
        glutTimerFunc(TIMER_MS, on_timer, 0)

    elif state == FLYING:
        sim_t     += dt_eff
        frame_cnt += 1
        x = pos_x(sim_t) * SCALE
        y = pos_y(sim_t) * SCALE
        missile_x = x
        missile_y = max(0.0, y)

        # Tabrakan berdasarkan ujung moncong rudal (nose tip).
        target_x = max_range() * SCALE
        tip_x, tip_y = missile_tip_position(missile_x, missile_y, sim_t)
        hit_bunker = tip_hits_bunker(tip_x, tip_y, target_x)

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

        if hit_bunker:
            missile_x = tip_x
            missile_y = max(0.0, tip_y)
            particles.trigger_explosion(missile_x, missile_y)
            camera.trigger_shake(0.42)
            if renderer is not None:
                renderer.trigger_impact(target_x)
            _play(_sfx_explode)
            state     = EXPLODING
            explode_t = 0.0
        elif sim_t >= t_flight or pos_y(sim_t) <= 0.0:
            missile_x = pos_x(t_flight) * SCALE
            missile_y = 0.0
            particles.trigger_explosion(missile_x, missile_y)
            camera.trigger_shake(0.42)
            if renderer is not None:
                renderer.trigger_impact(missile_x)
            _play(_sfx_explode)
            state     = EXPLODING
            explode_t = 0.0
        glutTimerFunc(TIMER_MS, on_timer, 0)

    elif state == EXPLODING:
        explode_t += dt_eff
        particles.emit_ground_fire(missile_x, missile_y, dt_eff)
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

    if state == LANDING or renderer._fading or renderer._countdown:
        renderer.render_landing()
        glutSwapBuffers()
        return

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
        cam_mode     = camera.mode,
        mouse_locked = mouse_locked[0]
    )

    glutSwapBuffers()


def idle_update():
    global state
    now = time.perf_counter()
    dt = min(0.05, now - last_idle_time[0])
    last_idle_time[0] = now

    # Check Shift for free cam (standalone shift detection on Windows)
    if camera.mode == CAM_FREE:
        try:
            # 0x10 is the Virtual Key Code for SHIFT
            is_shift = bool(ctypes.windll.user32.GetAsyncKeyState(0x10) & 0x8000)
            camera._free_move['shift'] = is_shift
        except:
            pass

    if state == LANDING or renderer._fading or renderer._countdown:
        renderer._star_time += dt

        # Typewriter: maju satu huruf tiap _type_speed detik
        if not renderer._type_done:
            renderer._type_timer += dt
            if renderer._type_timer >= renderer._type_speed:
                renderer._type_timer  = 0.0
                renderer._type_index += 1
                _play(_sfx_type)
                TITLE_LEN = len("SIMULASI PELUNCURAN RUDAL BALISTIK 3D")
                if renderer._type_index >= TITLE_LEN:
                    renderer._type_index = TITLE_LEN
                    renderer._type_done  = True

        # Countdown
        if renderer._countdown:
            prev = int(math.ceil(max(renderer._countdown_val, 0.0)))
            renderer._countdown_val -= dt
            curr = int(math.ceil(max(renderer._countdown_val, 0.0)))
            # Beep tiap angka berganti
            if curr < prev and curr > 0:
                _play(_sfx_beep)
            # Alert saat LUNCURKAN muncul
            if renderer._countdown_val <= 0.0 and prev > 0:
                _play(_sfx_alert)
            if renderer._countdown_val <= -0.6:
                renderer._countdown  = False
                renderer._fading     = True
                renderer._fade_alpha = 0.0
                _stop_music()

        # Fade
        if renderer._fading:
            renderer._fade_alpha += dt / 0.6
            if renderer._fade_alpha >= 1.0:
                renderer._fade_alpha = 0.0
                renderer._fading     = False
                state = IDLE
                unlock_mouse()

        glutPostRedisplay()
        return

    # Saat simulasi belum berjalan / sudah selesai, timer fisika tidak aktif.
    # Free-cam tetap perlu update supaya mouse dan WASD terasa langsung.
    if camera.mode == CAM_FREE and state in (IDLE, FINISHED):
        camera.update(
            dt, state, missile_x, missile_y,
            0.0, 0.0, max_range() * SCALE,
            IDLE, FLYING, EXPLODING, FINISHED
        )
        glutPostRedisplay()

# ────────────────────────────────────────────────────────
#  Reshape
# ────────────────────────────────────────────────────────
def reshape(w, h):
    glViewport(0, 0, w, max(h, 1))

# ────────────────────────────────────────────────────────
#  Keyboard
# ────────────────────────────────────────────────────────
def keyboard(key, x, y):
    global state
    # Tangani input di landing page
    if state == LANDING:
        if key in (b'\r', b'\n'):
            if not renderer._countdown:
                # Skip typewriter jika belum selesai, lalu mulai countdown
                renderer._type_done  = True
                renderer._type_index = len("SIMULASI PELUNCURAN RUDAL BALISTIK 3D")
                renderer._countdown     = True
                renderer._countdown_val = 3.0
        elif key == b'\x1b':
            sys.exit(0)
        glutPostRedisplay()
        return

    # WASD untuk free cam
    if camera.mode == CAM_FREE:
        camera.free_cam_key(key, True)

    if key in (b'\r', b'\n'):
        if state in (IDLE, FINISHED):
            reset_sim()
    elif key == b'\x1b':
        if mouse_locked[0]:
            unlock_mouse()
        else:
            sys.exit(0)
    elif key in (b'r', b'R'): camera.reset()
    elif key == b'1':
        camera.set_mode(CAM_FREE)
        lock_mouse()
    elif key == b'2': 
        camera.set_mode(CAM_CHASE)
        unlock_mouse()
    elif key == b'3': 
        camera.set_mode(CAM_TARGET)
        unlock_mouse()
    elif key == b'4': 
        camera.set_mode(CAM_ORBIT)
        unlock_mouse()
    # Zoom/rotate hanya jika bukan free cam
    elif camera.mode != CAM_FREE:
        if key in (b'w', b'W'): camera.zoom_in()
        if key in (b's', b'S'): camera.zoom_out()
        if key in (b'a', b'A'): camera.rotate_left()
        if key in (b'd', b'D'): camera.rotate_right()

    glutPostRedisplay()

def keyboard_up(key, x, y):
    if camera.mode == CAM_FREE:
        camera.free_cam_key(key, False)

def special_key(key, x, y):
    if camera.mode == CAM_FREE:
        if key == GLUT_KEY_UP:    camera.free_cam_key('up', True)
        if key == GLUT_KEY_DOWN:  camera.free_cam_key('down', True)
        if key == GLUT_KEY_LEFT:  camera.free_cam_key('left', True)
        if key == GLUT_KEY_RIGHT: camera.free_cam_key('right', True)
    glutPostRedisplay()

def special_key_up(key, x, y):
    if camera.mode == CAM_FREE:
        if key == GLUT_KEY_UP:    camera.free_cam_key('up', False)
        if key == GLUT_KEY_DOWN:  camera.free_cam_key('down', False)
        if key == GLUT_KEY_LEFT:  camera.free_cam_key('left', False)
        if key == GLUT_KEY_RIGHT: camera.free_cam_key('right', False)

def mouse_motion(x, y):
    # Mouse movement untuk free cam
    if camera.mode == CAM_FREE and mouse_locked[0]:
        if ignore_mouse_warp[0]:
            ignore_mouse_warp[0] = False
            return

        cx = glutGet(GLUT_WINDOW_WIDTH) // 2
        cy = glutGet(GLUT_WINDOW_HEIGHT) // 2
        
        dx = x - cx
        dy = y - cy
        
        if dx != 0 or dy != 0:
            camera.free_cam_mouse(dx, dy)
            ignore_mouse_warp[0] = True
            glutWarpPointer(cx, cy)
            glutPostRedisplay()

def mouse_passive(x, y):
    mouse_motion(x, y)

def mouse_click(button, state_btn, x, y):
    if button == GLUT_LEFT_BUTTON and state_btn == GLUT_DOWN:
        if camera.mode == CAM_FREE and not mouse_locked[0]:
            lock_mouse()

# ────────────────────────────────────────────────────────
#  Main
# ────────────────────────────────────────────────────────
def main():
    global renderer, _sfx_type, _sfx_beep, _sfx_alert, _sfx_launch, _sfx_explode

    print("=" * 56)
    print("  OPENGL_RUDAL – Kelompok 58 – UNSIL 2026")
    print("=" * 56)
    print(f"  Sudut     : {ANGLE_DEG:.0f} derajat")
    print(f"  V0        : {V0:.0f} m/s")
    print(f"  Jangkauan : {max_range():.1f} m")
    print(f"  Waktu     : {flight_time():.2f} detik")
    print("-" * 56)
    print("  ENTER=Mulai  ESC=Keluar  1/2/3/4=Kamera")
    print("  FREE: W/S=Maju/Mundur  A/D=Geser Kiri/Kanan")
    print("        SPACE/SHIFT=Naik/Turun")
    print("  PANAH: Atas/Bawah=Tengadah/Tunduk  Kiri/Kanan=Menoleh")
    print("  Mode lain: W/S=Zoom  A/D=Putar  R=Reset kamera")
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

    # Load audio
    _play_bgm("sound/Brirfing_theme.wav")
    _sfx_type    = _load_sound("sound/type.wav")
    _sfx_beep    = _load_sound("sound/beep.wav")
    _sfx_alert   = _load_sound("sound/alert.wav")
    _sfx_launch  = _load_sound("sound/launch.wav")
    _sfx_explode = _load_sound("sound/explode.wav")

    # Cursor visible di landing page
    unlock_mouse()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_key)
    glutSpecialUpFunc(special_key_up)
    glutMotionFunc(mouse_motion)
    glutPassiveMotionFunc(mouse_passive)
    glutMouseFunc(mouse_click)
    glutIdleFunc(idle_update)
    glutMainLoop()

if __name__ == "__main__":
    main()
