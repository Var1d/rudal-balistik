/* ============================================================
   rough_color.frag
   Fragment shader material kasar: diffuse kuat, no specular
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

varying vec3 fragNormal;
varying vec4 fragColor;

uniform int       useTexture;
uniform sampler2D tex0;

void main() {
    vec3 lightDir = normalize(vec3(1.0, 2.5, 1.5));
    vec3 normal   = normalize(fragNormal);

    float diff   = max(dot(normal, lightDir), 0.0);
    vec3  result = (0.12 + diff * 0.85) * fragColor.rgb;

    if (useTexture == 1) {
        vec4 tc = texture2D(tex0, gl_TexCoord[0].st);
        result *= tc.rgb;
        gl_FragColor = vec4(result, fragColor.a * tc.a);
    } else {
        gl_FragColor = vec4(result, fragColor.a);
    }
}
