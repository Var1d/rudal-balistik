/* ============================================================
   skybox.vert
   Shader untuk elemen langit (bintang, bulan) – no lighting
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

varying vec4 fragColor;

void main() {
    fragColor   = gl_Color;
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
