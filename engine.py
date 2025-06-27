# engine.py
# A simple, real-time 3D engine to navigate Triangle Splatting assets.
# Copyright 2025, Created by alby13

import pygame
from pygame.locals import *
import numpy as np
import glm  # PyGLM for math
from OpenGL.GL import *
import os

# --- 1. SHADER CODE (GLSL) ---
VERTEX_SHADER = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
out vec3 vertexColor;
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
void main()
{
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    vertexColor = aColor;
}
"""

FRAGMENT_SHADER = """
#version 330 core
out vec4 FragColor;
in vec3 vertexColor;
void main()
{
    FragColor = vec4(vertexColor, 1.0);
}
"""

# --- 2. HELPER FUNCTIONS ---
def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"Shader compilation failed: {error}")
    return shader

def create_shader_program(vertex_source, fragment_source):
    vertex_shader = compile_shader(vertex_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_source, GL_FRAGMENT_SHADER)
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        error = glGetProgramInfoLog(program).decode()
        raise RuntimeError(f"Shader linking failed: {error}")
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    return program

def load_custom_off(filepath, progress_callback=None):
    """
    Custom parser for the .off file format. Calls a callback function
    to update a loading screen.
    """
    print(f"Loading custom .off mesh: {filepath}")
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()

        header = lines[0].strip()
        if 'COFF' not in header and 'OFF' not in header:
            raise ValueError("Invalid OFF file header.")
        
        counts = list(map(int, lines[1].strip().split()))
        num_vertices, num_faces = counts[0], counts[1]

        vertex_positions = []
        for i in range(num_vertices):
            vertex_positions.append(list(map(float, lines[2 + i].strip().split())))

        final_vertices = []
        final_colors = []

        for i in range(num_faces):
            if progress_callback and (i % 15000 == 0 or i == num_faces - 1):
                progress_percentage = (i + 1) / num_faces
                progress_callback(progress_percentage, f"Parsing faces: {i+1}/{num_faces}")

            parts = lines[2 + num_vertices + i].strip().split()
            if int(parts[0]) != 3: continue

            idx1, idx2, idx3 = int(parts[1]), int(parts[2]), int(parts[3])
            color = [float(parts[4]) / 255.0, float(parts[5]) / 255.0, float(parts[6]) / 255.0]

            final_vertices.extend([vertex_positions[idx1], vertex_positions[idx2], vertex_positions[idx3]])
            final_colors.extend([color, color, color])
        
        vertices_np = np.array(final_vertices, dtype=np.float32)
        colors_np = np.array(final_colors, dtype=np.float32)

        print(f"Mesh loaded successfully: {len(vertices_np)} vertices.")
        return vertices_np, colors_np

    except Exception as e:
        print(f"Error loading custom .off mesh: {e}")
        return None, None

# --- 3. CAMERA CLASS ---
class Camera:
    def __init__(self, position=glm.vec3(0, 2, 20), speed=5.0):
        self.position = position
        self.yaw = -90.0
        self.pitch = 0.0
        self.speed = speed
        self.mouse_sensitivity = 0.1
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def get_view_matrix(self):
        forward = self.get_forward_vector()
        world_up = glm.vec3(0, 1, 0)
        return glm.lookAt(self.position, self.position + forward, world_up)

    def get_forward_vector(self):
        direction = glm.vec3()
        direction.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        direction.y = glm.sin(glm.radians(self.pitch))
        direction.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        return glm.normalize(direction)

    def process_input(self, keys, mouse_rel, delta_time):
        x_offset, y_offset = mouse_rel
        self.yaw += x_offset * self.mouse_sensitivity
        self.pitch -= y_offset * self.mouse_sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))

        velocity = self.speed * delta_time
        forward = self.get_forward_vector()
        world_up = glm.vec3(0, 1, 0)
        right = glm.normalize(glm.cross(forward, world_up))
        up = world_up

        if keys[K_w]: self.position += forward * velocity
        if keys[K_s]: self.position -= forward * velocity
        if keys[K_a]: self.position -= right * velocity
        if keys[K_d]: self.position += right * velocity
        if keys[K_SPACE]: self.position += up * velocity
        if keys[K_LCTRL] or keys[K_LSHIFT]: self.position -= up * velocity

# --- 4. MAIN ENGINE FUNCTION ---
def main():
    # --- Part 1: Initialization and 2D Loading Screen ---
    pygame.init()
    display_width, display_height = 1280, 720
    screen = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption("Loading...")

    def draw_loading_screen(progress, text):
        screen.fill((25, 25, 25))
        bar_width = 400
        bar_height = 30
        bar_x = (display_width - bar_width) / 2
        bar_y = (display_height - bar_height) / 2
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        fill_width = bar_width * progress
        pygame.draw.rect(screen, (100, 200, 255), (bar_x, bar_y, fill_width, bar_height))
        font = pygame.font.Font(None, 24)
        text_surface = font.render(text, True, (200, 200, 200))
        text_rect = text_surface.get_rect(center=(display_width / 2, bar_y + bar_height + 20))
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.event.pump()

    draw_loading_screen(0, "Starting Loading...")
    vertices, colors = load_custom_off("room.off", draw_loading_screen)
    if vertices is None:
        pygame.quit()
        return

    # --- Part 2: Re-initialize in 3D and Setup the Engine ---
    pygame.display.set_mode((display_width, display_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Triangle Splatting Real-Time Engine")

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    
    shader_program = create_shader_program(VERTEX_SHADER, FRAGMENT_SHADER)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)
    VBO_vertices = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_vertices)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(0)
    VBO_colors = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO_colors)
    glBufferData(GL_ARRAY_BUFFER, colors.nbytes, colors, GL_STATIC_DRAW)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(1)
    glBindVertexArray(0)

    # --- Engine Setup ---
    camera = Camera()
    clock = pygame.time.Clock()
    
    glUseProgram(shader_program)
    model_loc = glGetUniformLocation(shader_program, "model")
    view_loc = glGetUniformLocation(shader_program, "view")
    proj_loc = glGetUniformLocation(shader_program, "projection")

    projection_matrix = glm.perspective(glm.radians(45.0), display_width / display_height, 0.1, 1000.0)
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection_matrix))
    
    # Fixed model matrix with correct orientation
    model_matrix = glm.mat4(1.0)
    model_matrix = glm.rotate(model_matrix, glm.radians(151.20), glm.vec3(1, 0, 0))  # Pitch
    model_matrix = glm.rotate(model_matrix, glm.radians(-2.70), glm.vec3(0, 1, 0))  # Yaw
    model_matrix = glm.rotate(model_matrix, glm.radians(-1.35), glm.vec3(0, 0, 1))  # Roll
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model_matrix))

    # --- Part 3: Main Game Loop ---
    running = True
    while running:
        delta_time = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()
        mouse_rel = pygame.mouse.get_rel()
        camera.process_input(keys, mouse_rel, delta_time)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader_program)
        
        view_matrix = camera.get_view_matrix()
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view_matrix))
        
        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, len(vertices))
        glBindVertexArray(0)
        
        pygame.display.flip()

    # --- Cleanup ---
    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO_vertices])
    glDeleteBuffers(1, [VBO_colors])
    glDeleteProgram(shader_program)
    pygame.quit()

if __name__ == "__main__":
    print("--------------------------------------------------")
    print("Triangle Splatting Engine - Python/OpenGL Demo")
    print("Controls:")
    print("  W, A, S, D: Move camera")
    print("  Mouse: Look around")
    print("  Space: Move camera up")
    print("  L-Ctrl/L-Shift: Move camera down")
    print("  Escape: Exit")
    print("--------------------------------------------------")
    main()
