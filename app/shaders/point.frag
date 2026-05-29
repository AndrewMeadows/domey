#version 330

uniform vec3 u_color;
out vec4 frag_color;

void main() {
    // Round point sprites: discard fragments outside the unit disc.
    vec2 d = gl_PointCoord - vec2(0.5);
    if (dot(d, d) > 0.25) discard;
    frag_color = vec4(u_color, 1.0);
}
