/* ============================================================
   shadow_map.vert
   First pass: render scene dari sudut pandang cahaya
   untuk menghasilkan depth map (shadow mapping)
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

void main() {
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
