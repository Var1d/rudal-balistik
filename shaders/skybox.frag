/* ============================================================
   skybox.frag
   Fragment shader langit malam: warna langsung tanpa lighting
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

varying vec4 fragColor;

void main() {
    gl_FragColor = fragColor;
}
