/* ============================================================
   default_color.frag
   Fragment shader standar: warna objek + cahaya ambient/diffuse
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

varying vec3 fragNormal;
varying vec3 fragPos;
varying vec4 fragColor;

uniform int   useTexture;    // 1 = gunakan tekstur, 0 = warna saja
uniform sampler2D tex0;

void main() {
    // Arah cahaya GL_LIGHT0 (bulan malam)
    vec3 lightDir = normalize(vec3(1.0, 2.5, 1.5));
    vec3 normal   = normalize(fragNormal);

    // Ambient
    vec3 ambient  = 0.10 * fragColor.rgb;

    // Diffuse (Lambert)
    float diff    = max(dot(normal, lightDir), 0.0);
    vec3  diffuse = diff * 0.80 * fragColor.rgb;

    // Specular (Blinn-Phong ringan)
    vec3 viewDir  = normalize(-fragPos);
    vec3 halfDir  = normalize(lightDir + viewDir);
    float spec    = pow(max(dot(normal, halfDir), 0.0), 32.0);
    vec3 specular = spec * 0.25 * vec3(1.0);

    vec3 result = ambient + diffuse + specular;

    if (useTexture == 1) {
        vec4 texColor = texture2D(tex0, gl_TexCoord[0].st);
        result *= texColor.rgb;
        gl_FragColor = vec4(result, fragColor.a * texColor.a);
    } else {
        gl_FragColor = vec4(result, fragColor.a);
    }
}
