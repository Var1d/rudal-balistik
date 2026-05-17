# OPENGL_RUDAL
## Simulasi Peluncuran Rudal Balistik 3D
### Kelompok 58 – Grafika Komputer – UNSIL 2026

---

## Anggota

| Nama | NIM | 
|------|-----|
| Jamal Abdul Nasir | 247006111015 | 
| Fiqri Mochamad Fadillah | 247006111051 |
| Faisal Hadi Saik | 247006111052 |
| Irsyad Khoerul Umam | 247006111055 |
| Farid Dhiya Fairuz | 247006111058 | 

---

## Struktur Project

```
OPENGL_RUDAL/
│
├── main.py                  ← Entry point utama + logika simulasi
├── camera.py                ← Sistem kamera 4 mode (FREE/CHASE/TARGET/ORBIT)
├── scene_renderer.py        ← Orchestrator render scene + landing page
├── shader_program.py        ← Loader & compiler GLSL
├── particle_system.py       ← VFX asap & ledakan
├── textures_manager.py      ← Manajemen tekstur terpusat
├── requirements.txt         ← Dependensi Python
│
├── objects/
│   ├── missile/
│   │   └── missile.py       ← Model rudal + api nosel
│   ├── launcher/
│   │   └── launcher.py      ← Kendaraan peluncur (TEL)
│   ├── bunker/
│   │   └── bunker.py        ← Bunker target + animasi hancur
│   ├── vehicle/
│   │   └── vehicle.py       ← Kendaraan militer pendukung
│   └── tree/
│       └── tree.py          ← Vegetasi pohon pinus
│
├── shaders/
│   ├── default_color.vert   ← Shader standar (Phong lighting)
│   ├── default_color.frag
│   ├── rough_color.vert     ← Material kasar (beton/tanah)
│   ├── rough_color.frag
│   ├── skybox.vert          ← Langit & bintang
│   ├── skybox.frag
│   ├── shadow_map.vert      ← Shadow map pass
│   └── shadow_map.frag
│
├── textures/
│   ├── ground.png           ← Tekstur tanah/rumput
│   ├── metal.png            ← Logam untuk rudal/launcher
│   ├── camo.png             ← Kamuflase militer
│   ├── bark.png             ← Kulit kayu pohon
│   ├── leaves.png           ← Daun pohon
│   ├── concrete.png         ← Beton untuk bunker
│   ├── missile.png          ← Badan rudal
│   └── moon.png             ← Tekstur bulan 3D
│
└── sound/
    ├── Brirfing_theme.wav   ← BGM landing page
    ├── type.wav             ← SFX typewriter
    ├── beep.wav             ← SFX countdown
    ├── alert.wav            ← SFX alert peluncuran
    ├── launch.wav           ← SFX peluncuran rudal
    └── explode.wav          ← SFX ledakan
```

---

## Instalasi & Menjalankan

### 1. Install dependensi
```bash
pip install -r requirements.txt
```

### 2. Siapkan tekstur dan audio
Letakkan file PNG/JPG di folder `textures/` dan file WAV di folder `sound/`.

Sumber gratis:
- Tekstur: https://opengameart.org
- Audio: https://freesound.org

### 3. Jalankan
```bash
python main.py
```

---

## Kontrol

### Kontrol Umum

| Tombol | Fungsi |
|--------|--------|
| **ENTER** | Mulai / Ulang simulasi (kamera tetap di mode yang dipilih) |
| **DELETE** | Stop simulasi (kembali ke IDLE, kamera tidak berubah) |
| **ESC** | Kembali ke landing page (hanya saat IDLE/FINISHED) atau unlock mouse (FREE cam) |
| **R** | Reset parameter kamera (zoom, angle) tanpa ubah mode |

### Mode Kamera

| Tombol | Mode | Deskripsi |
|--------|------|----------|
| **1** | FREE | Kontrol manual penuh (WASD + Mouse) |
| **2** | CHASE | Mengikuti rudal dari belakang |
| **3** | TARGET | Fokus ke bunker target |
| **4** | ORBIT | Berputar otomatis mengelilingi scene |

### Kontrol FREE Camera (Mode 1)

| Tombol | Fungsi |
|--------|--------|
| **W / S** | Maju / Mundur |
| **A / D** | Geser Kiri / Kanan |
| **SPACE** | Naik |
| **SHIFT** | Turun |
| **Mouse** | Lihat sekitar (otomatis lock saat aktif) |
| **↑ / ↓** | Tengadah / Tunduk |
| **← / →** | Menoleh Kiri / Kanan |
| **Klik Mouse** | Lock/Unlock mouse |

### Kontrol ORBIT Camera (Mode 4)

| Tombol | Fungsi |
|--------|--------|
| **W / S** | Zoom In / Out |
| **A / D** | Putar Kiri / Kanan (manual) |

**Catatan:** Mode ORBIT berputar otomatis 36°/detik dan fokus dinamis:
- **IDLE/LAUNCHING**: Fokus ke tengah scene
- **FLYING**: Fokus mengikuti rudal
- **EXPLODING/FINISHED**: Fokus ke titik ledakan

---

## Fitur Grafika

| Fitur | Detail |
|-------|--------|
| **Landing Page** | Typewriter effect + countdown + fade transition + BGM |
| **Shader GLSL** | Phong lighting, rough material, skybox shader |
| **Pencahayaan** | GL_LIGHT0 (bulan 3D) + GL_LIGHT1 (ledakan) + GL_LIGHT2 (nosel rudal) |
| **Particle VFX** | Asap nosel transparan + ledakan 700 partikel + api tanah |
| **Skybox** | 250 bintang berkelip + 35 awan bergerak + bulan 3D bertekstur |
| **Terrain 3D** | Grid 140×80 berbasis sin/cos, warna per ketinggian, Phong shading |
| **Texture Mapping** | 8 tekstur (ground, metal, camo, bark, leaves, concrete, missile, moon) |
| **Slow-motion** | DT × 0.15 saat rudal < 2 m dari tanah |
| **Camera System** | 4 mode dengan transisi lerp halus + camera shake + persistence |
| **Objek 3D** | Rudal, Launcher TEL, Bunker (animasi hancur), 40 Pohon |
| **Audio System** | 6 SFX (type, beep, alert, launch, explode) + BGM via pygame.mixer |
| **HUD Dinamis** | Info simulasi + kontrol kamera + status real-time |
| **Collision Detection** | Tip-based collision untuk akurasi tinggi |
| **Scorch Mark** | Bekas terbakar di tanah dengan alpha blending |

---


