import glfw
from OpenGL.GL import *
import numpy as np
import time

# Vertex data for a full-screen quad
vertices = np.array([
    -1.0, -1.0,
     1.0, -1.0,
    -1.0,  1.0,
     1.0,  1.0
], dtype=np.float32)

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        error = glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"Shader compilation failed: {error}")
    return shader

def create_program(vertex_shader_source, fragment_shader_source):
    program = glCreateProgram()
    vertex_shader = compile_shader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_shader_source, GL_FRAGMENT_SHADER)
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
        error = glGetProgramInfoLog(program).decode()
        raise RuntimeError(f"Program linking failed: {error}")
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    return program

if not glfw.init():
    raise Exception("glfw can not be initialized!")

window = glfw.create_window(800, 600, "Mandelbrot Set", None, None)
if not window:
    glfw.terminate()
    raise Exception("glfw window can not be created!")

glfw.make_context_current(window)

# Load shaders
vertex_shader_source = """
#version 330 core
layout(location = 0) in vec2 position;
out vec2 fragCoord;

void main()
{
    fragCoord = (position + 1.0) / 2.0 * vec2(800.0, 600.0); // Map to [0, 800] and [0, 600]
    gl_Position = vec4(position, 0.0, 1.0);
}
"""
fragment_shader_source = """
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
"""

try:
    shader_program = create_program(vertex_shader_source, fragment_shader_source)
    print("Shaders compiled and linked successfully.")
except RuntimeError as e:
    print(e)
    glfw.terminate()
    exit()

# Create and bind VAO
vao = glGenVertexArrays(1)
glBindVertexArray(vao)

# Create and bind VBO
vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

# Define the vertex attribute pointer
position = glGetAttribLocation(shader_program, "position")
glVertexAttribPointer(position, 2, GL_FLOAT, GL_FALSE, 0, None)
glEnableVertexAttribArray(position)

# Unbind VBO and VAO
glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)

glUseProgram(shader_program)

# Uniform locations
resolution_loc = glGetUniformLocation(shader_program, "u_resolution")
center_loc = glGetUniformLocation(shader_program, "u_center")
zoom_loc = glGetUniformLocation(shader_program, "u_zoom")
max_iter_loc = glGetUniformLocation(shader_program, "u_maxIter")

# Set initial uniform values
glUniform2f(resolution_loc, 800, 600)
center = np.array([-0.5693038674840807, -0.5724608139558649])
zoom = 1.0
glUniform2f(center_loc, *center)
glUniform1f(zoom_loc, zoom)
glUniform1i(max_iter_loc, 512)

is_dragging = False
last_cursor_pos = None

def cursor_position_callback(window, xpos, ypos):
    global is_dragging, last_cursor_pos, center
    if is_dragging:
        if last_cursor_pos is not None:
            dx = (xpos - last_cursor_pos[0]) / 800.0 * 2.0 / zoom
            dy = (last_cursor_pos[1] - ypos) / 600.0 * 2.0 / zoom
            center[0] -= 16*dx
            center[1] -= 16*dy
        last_cursor_pos = (xpos, ypos)

def mouse_button_callback(window, button, action, mods):
    global is_dragging, last_cursor_pos
    if button == glfw.MOUSE_BUTTON_LEFT:
        if action == glfw.PRESS:
            is_dragging = True
            last_cursor_pos = glfw.get_cursor_pos(window)
        elif action == glfw.RELEASE:
            is_dragging = False
            last_cursor_pos = None

def scroll_callback(window, xoffset, yoffset):
    global zoom, center
    cursor_x, cursor_y = glfw.get_cursor_pos(window)
    
    # Convert cursor position to OpenGL coordinates
    cursor_x = (cursor_x / 800.0) * 2.0 - 1.0
    cursor_y = 1.0 - (cursor_y / 600.0) * 2.0  # Invert Y-axis

    # Calculate the current center in world coordinates
    #center_x_world = center[0] + cursor_x / zoom
    #center_y_world = center[1] + cursor_y / zoom

    # Adjust zoom (inverting the direction)
    zoom_factor = 1.1 if yoffset < 0 else 1.0 / 1.1
    zoom *= zoom_factor

    # Calculate the new center in world coordinates
    scaling_factor = 0.5  # Increase this value to make the center move faster
    #center[0] = center_x_world - cursor_x  / zoom
    #center[1] = center_y_world - cursor_y  / zoom

glfw.set_cursor_pos_callback(window, cursor_position_callback)
glfw.set_mouse_button_callback(window, mouse_button_callback)
glfw.set_scroll_callback(window, scroll_callback)



# Main rendering loop with animation
while not glfw.window_should_close(window):
    glClear(GL_COLOR_BUFFER_BIT)

    # Update uniforms
    glUniform1f(zoom_loc, zoom)
    glUniform2f(center_loc, *center)

    # Bind VAO and draw the quad
    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    glBindVertexArray(0)

    glfw.swap_buffers(window)
    glfw.poll_events()
    time.sleep(0.01)  # Add a small delay to control animation speed

glfw.terminate()
