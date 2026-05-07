/* ============================================================
   default_color.vert
   Shader vertex standar dengan pencahayaan Phong sederhana
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

varying vec3 fragNormal;
varying vec3 fragPos;
varying vec4 fragColor;

void main() {
    fragPos    = vec3(gl_ModelViewMatrix * gl_Vertex);
    fragNormal = normalize(gl_NormalMatrix * gl_Normal);
    fragColor  = gl_Color;

    gl_Position    = gl_ModelViewProjectionMatrix * gl_Vertex;
    gl_TexCoord[0] = gl_MultiTexCoord0;
}
