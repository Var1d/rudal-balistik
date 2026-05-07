/* ============================================================
   shadow_map.frag
   First pass fragment: hanya tulis kedalaman (depth)
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

void main() {
    /* Depth ditulis otomatis ke gl_FragDepth oleh OpenGL.
       Fragment shader ini tidak perlu melakukan apa-apa. */
    gl_FragColor = vec4(1.0);
}
