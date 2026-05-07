/* ============================================================
   rough_color.vert
   Shader untuk material kasar (beton, tanah) – diffuse only
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

varying vec3 fragNormal;
varying vec4 fragColor;
varying vec3 fragPos;

void main() {
    fragNormal = normalize(gl_NormalMatrix * gl_Normal);
    fragColor  = gl_Color;
    fragPos    = vec3(gl_ModelViewMatrix * gl_Vertex);
    gl_Position    = gl_ModelViewProjectionMatrix * gl_Vertex;
    gl_TexCoord[0] = gl_MultiTexCoord0;
}
