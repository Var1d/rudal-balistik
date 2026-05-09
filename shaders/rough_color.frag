/* ============================================================
   rough_color.frag
   Fragment shader material kasar: diffuse kuat, no specular + point light
   Kelompok 58 – OPENGL_RUDAL – UNSIL 2026
   ============================================================ */

varying vec3 fragNormal;
varying vec4 fragColor;
varying vec3 fragPos;

uniform int       useTexture;
uniform sampler2D tex0;

// Directional Light (Moon)
uniform vec3 uLightDirVS;
uniform vec3 uLightColor;
uniform vec3 uAmbientColor;

// Point Light (Missile/Explosion)
uniform vec3  uPointLightPosVS;
uniform vec3  uPointLightColor;
uniform float uPointLightIntensity;

// Fog
uniform vec3 uFogColor;
uniform float uFogDensity;

void main() {
    vec3 normal   = normalize(fragNormal);
    vec3 baseColor = fragColor.rgb;
    
    if (useTexture == 1) {
        vec4 tc = texture2D(tex0, gl_TexCoord[0].st);
        baseColor *= tc.rgb;
    }

    // 1. Directional Light (Moon)
    vec3 lightDir = normalize(uLightDirVS);
    float diff   = max(dot(normal, lightDir), 0.0);
    vec3  dLit   = (uAmbientColor + diff * uLightColor) * baseColor;

    // 2. Point Light (Missile/Explosion)
    vec3  pointLightDir = uPointLightPosVS - fragPos;
    float dist = length(pointLightDir);
    pointLightDir = normalize(pointLightDir);
    
    float atten = uPointLightIntensity / (1.0 + 0.4*dist + 0.1*dist*dist);
    float pDiff = max(dot(normal, pointLightDir), 0.0);
    vec3 pDiffuse = pDiff * uPointLightColor * baseColor * atten;

    vec3 result = dLit + pDiffuse;

    // Fog
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
