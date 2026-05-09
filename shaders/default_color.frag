/* ============================================================
   default_color.frag
   Fragment shader standar: warna objek + cahaya ambient/diffuse + point light
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

varying vec3 fragNormal;
varying vec3 fragPos;
varying vec4 fragColor;

uniform int   useTexture;    // 1 = gunakan tekstur, 0 = warna saja
uniform sampler2D tex0;

// Directional Light (Moon)
uniform vec3 uLightDirVS;
uniform vec3 uLightColor;
uniform vec3 uAmbientColor;
uniform vec3 uSpecColor;
uniform float uShininess;

// Point Light (Missile/Explosion)
uniform vec3  uPointLightPosVS;
uniform vec3  uPointLightColor;
uniform float uPointLightIntensity;

// Fog
uniform vec3 uFogColor;
uniform float uFogDensity;

void main() {
    vec3 normal   = normalize(fragNormal);
    vec3 viewDir  = normalize(-fragPos);
    vec3 baseColor = fragColor.rgb;
    
    if (useTexture == 1) {
        vec4 texColor = texture2D(tex0, gl_TexCoord[0].st);
        baseColor *= texColor.rgb;
    }

    // 1. Directional Light (Moon)
    vec3 lightDir = normalize(uLightDirVS);
    float diff    = max(dot(normal, lightDir), 0.0);
    vec3  ambient = uAmbientColor * baseColor;
    vec3  diffuse = diff * uLightColor * baseColor;
    
    vec3 halfDir  = normalize(lightDir + viewDir);
    float spec    = pow(max(dot(normal, halfDir), 0.0), uShininess);
    vec3 specular = spec * uSpecColor;

    // 2. Point Light (Missile/Explosion)
    vec3  pointLightDir = uPointLightPosVS - fragPos;
    float dist = length(pointLightDir);
    pointLightDir = normalize(pointLightDir);
    
    float atten = uPointLightIntensity / (1.0 + 0.5*dist + 0.2*dist*dist);
    float pDiff = max(dot(normal, pointLightDir), 0.0);
    vec3 pDiffuse = pDiff * uPointLightColor * baseColor * atten;

    vec3 result = ambient + diffuse + specular + pDiffuse;

    // Fog eksponensial berbasis jarak view-space.
    float d = length(fragPos);
    float fogFactor = exp(-uFogDensity * uFogDensity * d * d);
    fogFactor = clamp(fogFactor, 0.0, 1.0);
    vec3 fogged = mix(uFogColor, result, fogFactor);

    float alpha_out = fragColor.a;
    if (useTexture == 1) {
        alpha_out *= texture2D(tex0, gl_TexCoord[0].st).a;
    }

    gl_FragColor = vec4(fogged, alpha_out);
}
