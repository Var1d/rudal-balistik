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
uniform vec3 uLightDirVS;
uniform vec3 uLightColor;
uniform vec3 uAmbientColor;
uniform vec3 uSpecColor;
uniform float uShininess;
uniform vec3 uFogColor;
uniform float uFogDensity;

void main() {
    vec3 lightDir = normalize(uLightDirVS);
    vec3 normal   = normalize(fragNormal);

    float diff    = max(dot(normal, lightDir), 0.0);
    vec3  ambient = uAmbientColor * fragColor.rgb;
    vec3  diffuse = diff * uLightColor * fragColor.rgb;
    vec3 viewDir  = normalize(-fragPos);
    vec3 halfDir  = normalize(lightDir + viewDir);
    float spec    = pow(max(dot(normal, halfDir), 0.0), uShininess);
    vec3 specular = spec * uSpecColor;

    vec3 result = ambient + diffuse + specular;
    float alpha_out = fragColor.a;

    if (useTexture == 1) {
        vec4 texColor = texture2D(tex0, gl_TexCoord[0].st);
        result *= texColor.rgb;
        alpha_out = fragColor.a * texColor.a;
    }

    // Fog eksponensial berbasis jarak view-space.
    float dist = length(fragPos);
    float fogFactor = exp(-uFogDensity * uFogDensity * dist * dist);
    fogFactor = clamp(fogFactor, 0.0, 1.0);
    vec3 fogged = mix(uFogColor, result, fogFactor);

    gl_FragColor = vec4(fogged, alpha_out);
}
