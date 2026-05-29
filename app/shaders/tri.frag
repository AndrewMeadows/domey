#version 330

uniform vec4 u_color;
in vec3 v_world_pos;
out vec4 frag_color;

void main() {
    // Subtle Lambert-ish shading using the unit-sphere outward normal
    // (positions are already on the unit sphere, so position == normal).
    vec3 n = normalize(v_world_pos);
    vec3 light = normalize(vec3(0.5, 0.8, 0.6));
    float diff = max(dot(n, light), 0.0);
    float ambient = 0.35;
    vec3 lit = u_color.rgb * (ambient + (1.0 - ambient) * diff);
    frag_color = vec4(lit, u_color.a);
}
