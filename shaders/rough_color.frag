/* ============================================================
   rough_color.frag
   Fragment shader material kasar: diffuse kuat, no specular
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

varying vec3 fragNormal;
varying vec4 fragColor;
varying vec3 fragPos;

uniform int       useTexture;
uniform sampler2D tex0;
uniform vec3 uLightDirVS;
uniform vec3 uLightColor;
uniform vec3 uAmbientColor;
uniform vec3 uFogColor;
uniform float uFogDensity;

void main() {
    vec3 lightDir = normalize(uLightDirVS);
    vec3 normal   = normalize(fragNormal);

    float diff   = max(dot(normal, lightDir), 0.0);
    vec3  result = (uAmbientColor + diff * uLightColor) * fragColor.rgb;
    float alpha_out = fragColor.a;

    if (useTexture == 1) {
        vec4 tc = texture2D(tex0, gl_TexCoord[0].st);
        result *= tc.rgb;
        alpha_out = fragColor.a * tc.a;
    }

    float dist = length(fragPos);
    float fogFactor = exp(-uFogDensity * uFogDensity * dist * dist);
    fogFactor = clamp(fogFactor, 0.0, 1.0);
    vec3 fogged = mix(uFogColor, result, fogFactor);
    gl_FragColor = vec4(fogged, alpha_out);
}
