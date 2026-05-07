"""
shader_program.py
============================================================
  Loader & Compiler GLSL Shader
  Kelompok 58 – OPENGL_RUDAL – UNSIL 2026

  Cara pakai:
    sp = ShaderProgram("shaders/default_color")
    sp.use()
    sp.set_uniform_f("time", 1.5)
    sp.set_uniform_3f("lightPos", 1.0, 5.0, 2.0)
    ShaderProgram.use_fixed()   # kembali ke pipeline lama
============================================================
"""

import os
from OpenGL.GL import *


class ShaderProgram:
    """Membungkus satu pasang vertex + fragment shader GLSL."""

    # Cache agar shader tidak dikompilasi ulang
    _cache = {}

    def __init__(self, base_path: str):
        """
        base_path: path tanpa ekstensi, misal "shaders/default_color"
        Akan mencari:
          shaders/default_color.vert
          shaders/default_color.frag
        """
        self.program_id = None
        self._base      = base_path

        vert_path = base_path + ".vert"
        frag_path = base_path + ".frag"

        if base_path in ShaderProgram._cache:
            self.program_id = ShaderProgram._cache[base_path]
            return

        if not os.path.exists(vert_path):
            print(f"[SHADER] File tidak ditemukan: {vert_path}")
            return
        if not os.path.exists(frag_path):
            print(f"[SHADER] File tidak ditemukan: {frag_path}")
            return

        try:
            with open(vert_path, "r") as f:
                vert_src = f.read()
            with open(frag_path, "r") as f:
                frag_src = f.read()

            self.program_id = self._compile(vert_src, frag_src)
            ShaderProgram._cache[base_path] = self.program_id
            print(f"[SHADER] Berhasil dikompilasi: {base_path}")

        except Exception as e:
            print(f"[SHADER] Error saat kompilasi {base_path}: {e}")

    # ── Kompilasi internal ─────────────────────────────────
    def _compile(self, vert_src: str, frag_src: str) -> int:
        vert_id = self._compile_shader(GL_VERTEX_SHADER,   vert_src)
        frag_id = self._compile_shader(GL_FRAGMENT_SHADER, frag_src)

        prog = glCreateProgram()
        glAttachShader(prog, vert_id)
        glAttachShader(prog, frag_id)
        glLinkProgram(prog)

        if not glGetProgramiv(prog, GL_LINK_STATUS):
            log = glGetProgramInfoLog(prog).decode()
            raise RuntimeError(f"Program link error:\n{log}")

        glDeleteShader(vert_id)
        glDeleteShader(frag_id)
        return prog

    def _compile_shader(self, shader_type: int, source: str) -> int:
        sid = glCreateShader(shader_type)
        glShaderSource(sid, source)
        glCompileShader(sid)
        if not glGetShaderiv(sid, GL_COMPILE_STATUS):
            log = glGetShaderInfoLog(sid).decode()
            type_name = "VERTEX" if shader_type == GL_VERTEX_SHADER else "FRAGMENT"
            raise RuntimeError(f"{type_name} shader error:\n{log}")
        return sid

    # ── Penggunaan ─────────────────────────────────────────
    def use(self):
        """Aktifkan shader program ini."""
        if self.program_id:
            glUseProgram(self.program_id)

    @staticmethod
    def use_fixed():
        """Kembalikan ke OpenGL fixed-function pipeline."""
        glUseProgram(0)

    # ── Set uniform helpers ────────────────────────────────
    def _loc(self, name: str) -> int:
        return glGetUniformLocation(self.program_id, name)

    def set_uniform_i(self, name: str, val: int):
        if self.program_id:
            glUniform1i(self._loc(name), val)

    def set_uniform_f(self, name: str, val: float):
        if self.program_id:
            glUniform1f(self._loc(name), val)

    def set_uniform_3f(self, name: str, x: float, y: float, z: float):
        if self.program_id:
            glUniform3f(self._loc(name), x, y, z)

    def set_uniform_4f(self, name: str, x, y, z, w):
        if self.program_id:
            glUniform4f(self._loc(name), x, y, z, w)

    @property
    def valid(self) -> bool:
        return self.program_id is not None
