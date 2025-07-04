import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class CubeConfig:
    """Configuration class for cube appearance and behavior"""
    def __init__(self):
        self.size = 2.0
        self.mouse_sensitivity = 0.5
        
        # Face colors: [front, back, left, right, top, bottom]
        self.face_colors = [
            (1.0, 0.0, 0.0),  # Red front
            (0.0, 1.0, 0.0),  # Green back
            (0.0, 0.0, 1.0),  # Blue left
            (1.0, 1.0, 0.0),  # Yellow right
            (1.0, 0.0, 1.0),  # Magenta top
            (0.0, 1.0, 1.0)   # Cyan bottom
        ]
        
        # Gradient settings
        self.use_gradient = True
        self.gradient_origin = (0.0, 0.0, 0.0)  # Center of cube
        self.gradient_factor = 0.3  # How much gradient affects color

class Cube3D:
    """3D Cube class with rotation and rendering capabilities"""
    
    def __init__(self, config):
        self.config = config
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        
        # Define cube vertices
        self.vertices = np.array([
            [-1, -1, -1],  # 0
            [ 1, -1, -1],  # 1
            [ 1,  1, -1],  # 2
            [-1,  1, -1],  # 3
            [-1, -1,  1],  # 4
            [ 1, -1,  1],  # 5
            [ 1,  1,  1],  # 6
            [-1,  1,  1]   # 7
        ]) * config.size
        
        # Define cube faces (vertices indices)
        self.faces = [
            [0, 1, 2, 3],  # Front
            [4, 7, 6, 5],  # Back
            [0, 4, 7, 3],  # Left
            [1, 5, 6, 2],  # Right
            [3, 2, 6, 7],  # Top
            [0, 1, 5, 4]   # Bottom
        ]
        
        # Face normals for lighting
        self.face_normals = [
            (0, 0, -1),   # Front
            (0, 0, 1),    # Back
            (-1, 0, 0),   # Left
            (1, 0, 0),    # Right
            (0, 1, 0),    # Top
            (0, -1, 0)    # Bottom
        ]
    
    def calculate_gradient_color(self, base_color, vertex_pos):
        """Calculate gradient color based on distance from gradient origin"""
        if not self.config.use_gradient:
            return base_color
        
        # Calculate distance from gradient origin
        distance = math.sqrt(
            (vertex_pos[0] - self.config.gradient_origin[0])**2 +
            (vertex_pos[1] - self.config.gradient_origin[1])**2 +
            (vertex_pos[2] - self.config.gradient_origin[2])**2
        )
        
        # Normalize distance and apply gradient factor
        max_distance = self.config.size * math.sqrt(3)  # Max distance in cube
        normalized_distance = min(distance / max_distance, 1.0)
        
        # Apply gradient
        gradient_multiplier = 1.0 - (normalized_distance * self.config.gradient_factor)
        
        return tuple(c * gradient_multiplier for c in base_color)
    
    def render(self):
        """Render the cube with current rotation"""
        glPushMatrix()
        
        # Apply rotations
        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        glRotatef(self.rotation_z, 0, 0, 1)
        
        # Draw each face
        for face_idx, face in enumerate(self.faces):
            glBegin(GL_QUADS)
            
            base_color = self.config.face_colors[face_idx]
            
            for vertex_idx in face:
                vertex_pos = self.vertices[vertex_idx]
                
                # Calculate gradient color for this vertex
                color = self.calculate_gradient_color(base_color, vertex_pos)
                glColor3f(*color)
                
                # Set vertex position
                glVertex3f(*vertex_pos)
            
            glEnd()
        
        # Draw wireframe for better visibility
        glColor3f(0.2, 0.2, 0.2)
        glLineWidth(1.0)
        
        for face in self.faces:
            glBegin(GL_LINE_LOOP)
            for vertex_idx in face:
                glVertex3f(*self.vertices[vertex_idx])
            glEnd()
        
        glPopMatrix()
    
    def rotate(self, delta_x, delta_y, delta_z=0):
        """Rotate the cube by given angles"""
        sensitivity = self.config.mouse_sensitivity
        self.rotation_x += delta_y * sensitivity
        self.rotation_y += delta_x * sensitivity
        self.rotation_z += delta_z * sensitivity
        
        # Keep rotations within reasonable bounds
        self.rotation_x %= 360
        self.rotation_y %= 360
        self.rotation_z %= 360

class CubeSimulator:
    """Main simulator class that handles window, events, and rendering"""
    
    def __init__(self):
        self.config = CubeConfig()
        self.cube = Cube3D(self.config)
        
        # Mouse tracking
        self.mouse_dragging = False
        self.last_mouse_pos = (0, 0)
        
        # Initialize Pygame and OpenGL
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        
        pygame.display.set_mode((self.screen_width, self.screen_height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Cube Simulator - Click and drag to rotate")
        
        self.setup_opengl()
        
    def setup_opengl(self):
        """Initialize OpenGL settings"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Set up perspective
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.screen_width / self.screen_height), 0.1, 50.0)
        
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0.0, 0.0, -8)
        
        # Basic lighting
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 5, 1])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1])
        
        # Material properties
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.mouse_dragging = True
                    self.last_mouse_pos = pygame.mouse.get_pos()
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_dragging:
                    current_pos = pygame.mouse.get_pos()
                    delta_x = current_pos[0] - self.last_mouse_pos[0]
                    delta_y = current_pos[1] - self.last_mouse_pos[1]
                    
                    self.cube.rotate(delta_x, delta_y)
                    self.last_mouse_pos = current_pos
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keyboard(event.key)
        
        return True
    
    def handle_keyboard(self, key):
        """Handle keyboard input for customization"""
        if key == pygame.K_r:
            # Reset rotation
            self.cube.rotation_x = 0
            self.cube.rotation_y = 0
            self.cube.rotation_z = 0
            
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
            # Increase size
            self.config.size = min(self.config.size + 0.2, 5.0)
            self.cube = Cube3D(self.config)
            
        elif key == pygame.K_MINUS:
            # Decrease size
            self.config.size = max(self.config.size - 0.2, 0.5)
            self.cube = Cube3D(self.config)
            
        elif key == pygame.K_s:
            # Increase mouse sensitivity
            self.config.mouse_sensitivity = min(self.config.mouse_sensitivity + 0.1, 2.0)
            
        elif key == pygame.K_d:
            # Decrease mouse sensitivity
            self.config.mouse_sensitivity = max(self.config.mouse_sensitivity - 0.1, 0.1)
            
        elif key == pygame.K_g:
            # Toggle gradient
            self.config.use_gradient = not self.config.use_gradient
            
        elif key == pygame.K_c:
            # Cycle through color schemes
            self.cycle_color_scheme()
    
    def cycle_color_scheme(self):
        """Cycle through different color schemes"""
        schemes = [
            # Default RGB scheme
            [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), 
             (1.0, 1.0, 0.0), (1.0, 0.0, 1.0), (0.0, 1.0, 1.0)],
            
            # Warm colors
            [(1.0, 0.5, 0.0), (1.0, 0.0, 0.5), (0.8, 0.2, 0.2), 
             (1.0, 0.8, 0.0), (0.9, 0.3, 0.3), (1.0, 0.6, 0.2)],
            
            # Cool colors
            [(0.0, 0.5, 1.0), (0.0, 0.8, 0.8), (0.2, 0.2, 0.8), 
             (0.5, 0.0, 1.0), (0.0, 0.6, 0.9), (0.3, 0.7, 0.9)],
            
            # Monochrome
            [(0.9, 0.9, 0.9), (0.7, 0.7, 0.7), (0.5, 0.5, 0.5), 
             (0.3, 0.3, 0.3), (0.1, 0.1, 0.1), (0.0, 0.0, 0.0)]
        ]
        
        current_scheme = None
        for i, scheme in enumerate(schemes):
            if self.config.face_colors == scheme:
                current_scheme = i
                break
        
        if current_scheme is None:
            next_scheme = 0
        else:
            next_scheme = (current_scheme + 1) % len(schemes)
        
        self.config.face_colors = schemes[next_scheme]
    
    def render(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Set background color
        glClearColor(0.1, 0.1, 0.1, 1.0)
        
        # Render the cube
        self.cube.render()
        
        pygame.display.flip()
    
    def display_help(self):
        """Display help information"""
        help_text = """
        3D Cube Simulator Controls:
        
        Mouse:
        - Click and drag to rotate the cube in all axes
        
        Keyboard:
        - R: Reset rotation
        - +/=: Increase cube size
        - -: Decrease cube size
        - S: Increase mouse sensitivity
        - D: Decrease mouse sensitivity
        - G: Toggle gradient effect
        - C: Cycle through color schemes
        - ESC: Exit
        
        The cube features:
        - Interactive 3D rotation
        - Customizable colors for each face
        - Gradient effects from center
        - Adjustable size and mouse sensitivity
        """
        print(help_text)
    
    def run(self):
        """Main game loop"""
        self.display_help()
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self.handle_events()
            self.render()
            clock.tick(60)  # 60 FPS
        
        pygame.quit()

if __name__ == "__main__":
    try:
        simulator = CubeSimulator()
        simulator.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have pygame and PyOpenGL installed:")
        print("pip install pygame PyOpenGL PyOpenGL_accelerate numpy")
