"""
mesh.py
============================================================
  Loader OBJ Mesh Generik
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Mendukung:
    - Vertex (v)
    - Normal (vn)
    - Texture coordinate (vt)
    - Face (f) – triangulated atau quad
    - Multi-material (mtl) – diabaikan, pakai glColor saja

  Cara pakai:
    m = Mesh("objects/launcher/launcher.obj")
    m.draw()
============================================================
"""

import os
from OpenGL.GL import *


class Mesh:
    """Memuat dan merender file OBJ sederhana."""

    def __init__(self, path: str):
        self.path      = path
        self.vertices  = []   # list of (x,y,z)
        self.normals   = []   # list of (nx,ny,nz)
        self.texcoords = []   # list of (u,v)
        self.faces     = []   # list of [(vi,ti,ni), ...]
        self._loaded   = False
        self._load()

    # ── Parser OBJ ────────────────────────────────────────
    def _load(self):
        if not os.path.exists(self.path):
            print(f"[MESH] File tidak ditemukan: {self.path}")
            return

        verts, norms, texcs = [], [], []
        faces = []

        try:
            with open(self.path, "r") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split()
                    token = parts[0]

                    if token == "v":
                        verts.append(tuple(float(p) for p in parts[1:4]))
                    elif token == "vn":
                        norms.append(tuple(float(p) for p in parts[1:4]))
                    elif token == "vt":
                        texcs.append(tuple(float(p) for p in parts[1:3]))
                    elif token == "f":
                        face = []
                        for tok in parts[1:]:
                            indices = tok.split("/")
                            vi = int(indices[0]) - 1
                            ti = int(indices[1]) - 1 if (len(indices) > 1 and indices[1]) else -1
                            ni = int(indices[2]) - 1 if (len(indices) > 2 and indices[2]) else -1
                            face.append((vi, ti, ni))
                        # Triangulate fan jika face > 3 vertex
                        for i in range(1, len(face) - 1):
                            faces.append([face[0], face[i], face[i+1]])

            self.vertices  = verts
            self.normals   = norms
            self.texcoords = texcs
            self.faces     = faces
            self._loaded   = True
            print(f"[MESH] Dimuat: {self.path} "
                  f"({len(verts)} v, {len(faces)} f)")

        except Exception as e:
            print(f"[MESH] Error saat membaca {self.path}: {e}")

    # ── Render ────────────────────────────────────────────
    def draw(self, tex_id=None):
        """
        Render mesh menggunakan GL_TRIANGLES.
        Jika tex_id diberikan, aktifkan tekstur.
        """
        if not self._loaded or not self.faces:
            return

        if tex_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex_id)

        glBegin(GL_TRIANGLES)
        for tri in self.faces:
            for (vi, ti, ni) in tri:
                # Normal
                if ni >= 0 and ni < len(self.normals):
                    glNormal3fv(self.normals[ni])
                # Texcoord
                if ti >= 0 and ti < len(self.texcoords):
                    glTexCoord2fv(self.texcoords[ti])
                # Vertex
                if vi >= 0 and vi < len(self.vertices):
                    glVertex3fv(self.vertices[vi])
        glEnd()

        if tex_id is not None:
            glDisable(GL_TEXTURE_2D)

    # ── Info ──────────────────────────────────────────────
    def __repr__(self):
        return (f"Mesh(path='{self.path}', "
                f"verts={len(self.vertices)}, "
                f"faces={len(self.faces)}, "
                f"loaded={self._loaded})")
