#version 330

in vec3 in_position;
uniform mat4 u_mvp;
out vec3 v_world_pos;

void main() {
    v_world_pos = in_position;
    gl_Position = u_mvp * vec4(in_position, 1.0);
}
