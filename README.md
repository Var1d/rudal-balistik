# OPENGL_RUDAL
## Simulasi Peluncuran Rudal Balistik 3D
### Kelompok 58 – Grafika Komputer – UNSIL 2026

---

## Anggota

| Nama | NIM | Tanggung Jawab |
|------|-----|----------------|
| Jamal Abdul Nasir | 247006111015 | Particle VFX (asap & ledakan) |
| Fiqri Mochamad Fadillah | 247006111051 | Pencahayaan & Material |
| Faisal Hadi Saik | 247006111052 | Kamera & Slow-Motion |
| Irsyad Khoerul Umam | 247006111055 | Terrain, Skybox, Vegetasi |
| Farid Dhiya Fairuz | 247006111058 | Model 3D & Texture Mapping |

---

## Struktur Project

```
OPENGL_RUDAL/
│
├── main.py                  ← Entry point utama
├── camera.py                ← Sistem kamera 4 mode
├── scene_renderer.py        ← Orchestrator render scene
├── shader_program.py        ← Loader & compiler GLSL
├── particle_system.py       ← VFX asap & ledakan
├── textures_manager.py      ← Manajemen tekstur terpusat
├── requirements.txt
│
├── objects/
│   ├── missile/
│   │   └── missile.py       ← Model rudal + api nosel
│   ├── launcher/
│   │   └── launcher.py      ← Kendaraan peluncur (TEL)
│   ├── bunker/
│   │   └── bunker.py        ← Bunker target + marker
│   ├── vehicle/
│   │   └── vehicle.py       ← Kendaraan militer pendukung
│   └── tree/
│       └── tree.py          ← Vegetasi pohon pinus
│
├── shaders/
│   ├── default_color.vert   ← Shader standar (Phong)
│   ├── default_color.frag
│   ├── rough_color.vert     ← Material kasar (beton)
│   ├── rough_color.frag
│   ├── skybox.vert          ← Langit & bintang
│   ├── skybox.frag
│   ├── shadow_map.vert      ← Shadow map pass
│   └── shadow_map.frag
│
└── textures/
    ├── ground.png           ← Tekstur tanah/rumput
    ├── metal.png            ← Logam untuk rudal/launcher
    ├── camo.png             ← Kamuflase militer
    ├── bark.png             ← Kulit kayu pohon
    ├── leaves.png           ← Daun pohon
    ├── concrete.png         ← Beton untuk bunker
    └── missile.png          ← Badan rudal (opsional)
```

---

## Instalasi & Menjalankan

### 1. Install dependensi
```bash
pip install -r requirements.txt
```

### 2. Siapkan tekstur (opsional tapi dianjurkan)
Letakkan file PNG/JPG di folder `textures/` sesuai nama di atas.
Sumber tekstur gratis: https://opengameart.org

### 3. Jalankan
```bash
python main.py
```

---

## Kontrol

| Tombol | Fungsi |
|--------|--------|
| **ENTER** | Mulai / Ulang simulasi |
| **1** | Mode kamera: FREE (manual W/S/A/D) |
| **2** | Mode kamera: CHASE (ikuti rudal) |
| **3** | Mode kamera: TARGET (hadap bunker) |
| **4** | Mode kamera: ORBIT (otomatis) |
| **W / S** | Zoom in / out |
| **A / D** | Putar kamera kiri / kanan |
| **R** | Reset posisi kamera |
| **ESC** | Keluar |

---

## Fitur Grafika

| Fitur | Detail |
|-------|--------|
| **Shader GLSL** | Phong lighting, rough material, skybox shader |
| **Pencahayaan** | GL_LIGHT0 (bulan malam) + GL_LIGHT1 (ledakan dinamis) |
| **Particle VFX** | Asap nosel GL_QUADS transparan + ledakan 700 partikel |
| **Skybox** | 380 bintang berkelip + bulan sabit animasi |
| **Terrain 3D** | Grid 60×30 berbasis sin/cos, warna per ketinggian |
| **Texture Mapping** | 7 tekstur via Pillow + glTexImage2D |
| **Slow-motion** | DT × 0.15 saat rudal < 2 m dari tanah |
| **Chase Camera** | 4 mode kamera dengan transisi lerp halus |
| **Objek 3D** | Rudal, Launcher TEL, Bunker, 3 Kendaraan, 30 Pohon |

---


