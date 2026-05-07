"""
vibo.py  (VBO Helper)
============================================================
  Vertex Buffer Object – Upload Data ke GPU
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Mengoptimalkan render terrain & objek dengan mengunggah
  vertex data ke VRAM (GPU memory) sekali saja,
  kemudian menggambar langsung dari sana.

  Lebih cepat dari glBegin/glEnd karena data tidak
  dikirim ulang ke GPU setiap frame.

  Cara pakai:
    # Buat buffer dari numpy array
    vbo = VBO(vertex_array, GL_STATIC_DRAW)
    # Saat render:
    vbo.bind()
    vbo.draw(GL_TRIANGLES, vertex_count)
    vbo.unbind()
============================================================
"""

import numpy as np
from OpenGL.GL import *
from OpenGL.arrays import vbo as gl_vbo


class VBO:
    """Wrapper sederhana untuk OpenGL Vertex Buffer Object."""

    def __init__(self, data: np.ndarray, usage=GL_STATIC_DRAW):
        """
        data  : numpy array float32, shape (N, stride)
        usage : GL_STATIC_DRAW / GL_DYNAMIC_DRAW / GL_STREAM_DRAW
        """
        self._vbo_id  = None
        self._count   = 0
        self._stride  = 0
        self._usage   = usage
        self.upload(data)

    def upload(self, data: np.ndarray):
        """Upload atau perbarui data buffer."""
        data_f32 = data.astype(np.float32)
        self._count  = data_f32.shape[0]
        self._stride = data_f32.shape[1] if data_f32.ndim > 1 else 1

        if self._vbo_id is None:
            self._vbo_id = glGenBuffers(1)

        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_id)
        glBufferData(GL_ARRAY_BUFFER,
                     data_f32.nbytes,
                     data_f32,
                     self._usage)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_id)

    def unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, mode, count=None):
        """
        Gambar vertices yang sudah diupload.
        Asumsi: setiap vertex terdiri dari (x, y, z) = 3 float.
        """
        if self._vbo_id is None:
            return
        n = count if count is not None else self._count
        self.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glDrawArrays(mode, 0, n)
        glDisableClientState(GL_VERTEX_ARRAY)
        self.unbind()

    def draw_with_normals(self, mode, count=None):
        """
        Gambar vertices + normals.
        Asumsi layout: (x,y,z, nx,ny,nz) = 6 float per vertex.
        """
        if self._vbo_id is None:
            return
        n = count if count is not None else self._count
        stride = 6 * 4   # 6 float × 4 byte

        self.bind()
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)

        glVertexPointer(3, GL_FLOAT, stride, ctypes.c_void_p(0))
        glNormalPointer(GL_FLOAT, stride, ctypes.c_void_p(12))

        glDrawArrays(mode, 0, n)

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        self.unbind()

    def delete(self):
        if self._vbo_id is not None:
            glDeleteBuffers(1, [self._vbo_id])
            self._vbo_id = None

    def __del__(self):
        self.delete()

    def __repr__(self):
        return (f"VBO(id={self._vbo_id}, "
                f"count={self._count}, "
                f"stride={self._stride})")


# ──────────────────────────────────────────────────────────
#  Helper: buat VBO terrain sekali dari grid sin/cos
# ──────────────────────────────────────────────────────────
def build_terrain_vbo(cols=60, rows=30, w=22.0, d=12.0,
                       x0=-11.0, z0=-6.0):
    """
    Bangun array vertex terrain untuk diupload ke VBO.
    Format tiap vertex: (x, y, z, r, g, b)  → 6 float
    """
    import math as _math

    def h(x, z):
        v  = 0.08 * _math.sin(x*0.9+0.5) * _math.cos(z*1.1)
        v += 0.05 * _math.sin(x*1.8-1.0) * _math.sin(z*0.7+2.0)
        v += 0.03 * _math.cos(x*3.0)     * _math.sin(z*2.5)
        flat = _math.exp(-x*x*0.5)
        return v * (1.0 - flat*0.8)

    def col(hv):
        if   hv < -0.02: return (0.06,0.22,0.06)
        elif hv <  0.04: return (0.10,0.35,0.10)
        elif hv <  0.09: return (0.18,0.42,0.14)
        else:            return (0.38,0.32,0.14)

    dx = w / cols
    dz = d / rows
    verts = []

    for row in range(rows):
        for col_i in range(cols):
            x  = x0 + col_i * dx
            z0_ = z0 + row * dz
            z1  = z0 + (row+1) * dz

            # Dua segitiga per cell
            corners = [
                (x,    z0_), (x+dx, z0_), (x+dx, z1),
                (x,    z0_), (x+dx, z1),  (x,    z1),
            ]
            for (cx, cz) in corners:
                hy = h(cx, cz)
                cr, cg, cb = col(hy)
                verts.extend([cx, hy, cz, cr, cg, cb])

    return np.array(verts, dtype=np.float32).reshape(-1, 6)
