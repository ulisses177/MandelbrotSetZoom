#version 330 core
in vec2 fragCoord;
out vec4 color;

uniform vec2 u_resolution;
uniform vec2 u_center;
uniform float u_zoom;
uniform int u_maxIter;

// Helper functions for double-double arithmetic
vec2 twoSum(float a, float b) {
    float s = a + b;
    float v = s - a;
    float e = (a - (s - v)) + (b - v);
    return vec2(s, e);
}

vec2 quickTwoSum(float a, float b) {
    float s = a + b;
    float e = b - (s - a);
    return vec2(s, e);
}

vec2 twoProd(float a, float b) {
    float p = a * b;
    float e = (a * b) - p; // Manually handle the error term without fma
    return vec2(p, e);
}

vec2 add_dd(vec2 a, vec2 b) {
    vec2 s = twoSum(a.x, b.x);
    s.y += a.y + b.y;
    return quickTwoSum(s.x, s.y);
}

vec2 sub_dd(vec2 a, vec2 b) {
    vec2 s = twoSum(a.x, -b.x);
    s.y += a.y - b.y;
    return quickTwoSum(s.x, s.y);
}

vec2 mul_dd(vec2 a, vec2 b) {
    vec2 p = twoProd(a.x, b.x);
    p.y += a.x * b.y + a.y * b.x;
    return quickTwoSum(p.x, p.y);
}

vec2 sqr_dd(vec2 a) {
    return mul_dd(a, a);
}

void main()
{
    vec2 cRe = add_dd(vec2(u_center.x, 0.0), vec2((fragCoord.x - u_resolution.x / 2.0) / u_zoom, 0.0));
    vec2 cIm = add_dd(vec2(u_center.y, 0.0), vec2((fragCoord.y - u_resolution.y / 2.0) / u_zoom, 0.0));
    vec2 zRe = vec2(0.0, 0.0);
    vec2 zIm = vec2(0.0, 0.0);

    int i;
    for(i = 0; i < u_maxIter; i++) {
        vec2 zRe2 = sqr_dd(zRe);
        vec2 zIm2 = sqr_dd(zIm);
        if (zRe2.x + zIm2.x > 4.0) break;

        vec2 zRe_zIm = mul_dd(zRe, zIm);
        zIm = add_dd(add_dd(zRe_zIm, zRe_zIm), cIm);
        zRe = add_dd(sub_dd(zRe2, zIm2), cRe);
    }

    float norm = float(i) / float(u_maxIter);
    color = vec4(vec3(norm), 1.0);
}
