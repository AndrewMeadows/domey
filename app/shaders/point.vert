#version 330

in vec3 in_position;
uniform mat4 u_mvp;
uniform float u_point_size;

void main() {
    gl_Position = u_mvp * vec4(in_position, 1.0);
    gl_PointSize = u_point_size;
}
