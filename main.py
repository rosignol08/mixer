import pyray as rl
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & THEME (Style "Blender")
# ==========================================
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
TITLE = "RayBuilder - Python 3D Generator"

# Couleurs du thème (Dark UI)
COLOR_BG = rl.Color(30, 30, 30, 255)        # Fond de la fenetre 3D
COLOR_UI_BG = rl.Color(45, 45, 45, 255)     # Fond des panneaux
COLOR_UI_BORDER = rl.Color(60, 60, 60, 255) # Bordures
COLOR_TEXT = rl.WHITE
COLOR_ACCENT = rl.Color(66, 135, 245, 255)  # Bleu style VS Code

# ==========================================
# 2. STRUCTURE DE DONNÉES (SCÈNE)
# ==========================================
class SceneObject:
    """Représente un objet dans ta scène (Cube, Sphere, etc.)"""
    def __init__(self, obj_type, position, color, size):
        self.type = obj_type  # 'cube', 'sphere', 'plane'
        self.position = position # rl.Vector3
        self.color = color
        self.size = size # float ou Vector3
        self.name = f"{obj_type}_{datetime.now().strftime('%S%f')}" # ID unique simple

    def draw(self):
        """Dessine l'objet dans la vue 3D de l'éditeur"""
        if self.type == 'cube':
            rl.draw_cube_v(self.position, self.size, self.color)
            rl.draw_cube_wires_v(self.position, self.size, rl.BLACK)
        elif self.type == 'sphere':
            rl.draw_sphere(self.position, self.size, self.color)
            rl.draw_sphere_wires(self.position, self.size, 10, 10, rl.BLACK)
        elif self.type == 'grid':
            rl.draw_grid(20, 1.0)

    def to_python_code(self):
        """
        TODO: C'est ici que la magie opère. 
        On convertit l'objet en string de code Python Raylib.
        """
        x, y, z = self.position.x, self.position.y, self.position.z
        
        if self.type == 'cube':
            # Exemple de génération de code pour un cube
            # On doit formater la couleur et le vecteur
            return f"    rl.draw_cube(rl.Vector3({x}, {y}, {z}), {self.size.x}, {self.size.y}, {self.size.z}, rl.RED)"
        
        if self.type == 'sphere':
             return f"    rl.draw_sphere(rl.Vector3({x}, {y}, {z}), {self.size}, rl.BLUE)"
             
        return "# Objet inconnu"

# ==========================================
# 3. GESTION DE L'INTERFACE (UI)
# ==========================================
class EditorUI:
    """Gère l'affichage des boutons et panneaux par dessus la 3D"""
    def __init__(self):
        self.panel_width = 250
        
    def draw_panel(self, screen_w, screen_h):
        # Fond du panneau latéral droit
        rect = rl.Rectangle(screen_w - self.panel_width, 0, self.panel_width, screen_h)
        rl.draw_rectangle_rec(rect, COLOR_UI_BG)
        rl.draw_rectangle_lines_ex(rect, 1, COLOR_UI_BORDER)
        
        rl.draw_text("PROPRIÉTÉS", int(screen_w - self.panel_width + 10), 10, 20, COLOR_TEXT)
        
        # TODO: Ajouter ici des sliders pour modifier la position de l'objet sélectionné
        # TODO: Ajouter un ColorPicker (selecteur de couleur)

    def draw_button(self, text, x, y, width, height):
        """Un bouton simple. Retourne True si cliqué."""
        rect = rl.Rectangle(x, y, width, height)
        mouse_point = rl.get_mouse_position()
        clicked = False
        
        # Interaction (Hover & Click)
        color = COLOR_UI_BG
        if rl.check_collision_point_rec(mouse_point, rect):
            color = rl.Color(70, 70, 70, 255) # Hover
            if rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT):
                color = COLOR_ACCENT
                clicked = True
        
        # Dessin
        rl.draw_rectangle_rec(rect, color)
        rl.draw_rectangle_lines_ex(rect, 1, COLOR_UI_BORDER)
        rl.draw_text(text, int(x + 10), int(y + 10), 20, COLOR_TEXT)
        
        return clicked

# ==========================================
# 4. GÉNÉRATEUR DE CODE
# ==========================================
class CodeExporter:
    @staticmethod
    def export(scene_objects, filename="generated_scene.py"):
        """Ecrit le fichier Python final"""
        header = """
import pyray as rl

# Code généré par RayBuilder
def main():
    rl.init_window(800, 600, "Ma Scene Generee")
    rl.set_target_fps(60)
    
    camera = rl.Camera3D()
    camera.position = rl.Vector3(10.0, 10.0, 10.0)
    camera.target = rl.Vector3(0.0, 0.0, 0.0)
    camera.up = rl.Vector3(0.0, 1.0, 0.0)
    camera.fovy = 45.0
    camera.projection = rl.CAMERA_PERSPECTIVE

    while not rl.window_should_close():
        rl.update_camera(camera, rl.CAMERA_ORBITAL)
        
        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        rl.begin_mode_3d(camera)
        
        rl.draw_grid(20, 1.0)
"""
        footer = """
        rl.end_mode_3d()
        rl.draw_fps(10, 10)
        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    main()
"""
        
        with open(filename, "w") as f:
            f.write(header)
            # Écriture des objets
            for obj in scene_objects:
                f.write(f"    {obj.to_python_code()}\n")
            f.write(footer)
            
        print(f"Succès ! Fichier {filename} créé.")

# ==========================================
# 5. MAIN LOOP (MOTEUR)
# ==========================================
def main():
    rl.init_window(SCREEN_WIDTH, SCREEN_HEIGHT, TITLE)
    rl.set_target_fps(60)
    
    # Camera de l'éditeur
    camera = rl.Camera3D()
    camera.position = rl.Vector3(10.0, 10.0, 10.0)
    camera.target = rl.Vector3(0.0, 0.0, 0.0)
    camera.up = rl.Vector3(0.0, 1.0, 0.0)
    camera.fovy = 45.0
    camera.projection = rl.CAMERA_PERSPECTIVE

    # État de l'application
    scene_objects = []
    ui = EditorUI()
    
    # Ajout d'objets par défaut pour tester
    scene_objects.append(SceneObject('grid', rl.Vector3(0,0,0), rl.WHITE, 0))
    
    while not rl.window_should_close():
        # --- LOGIQUE ---
        
        # TODO: Implémenter le "Ray Picking" (rl.get_ray_collision...) 
        # pour sélectionner un objet avec la souris dans la scène 3D.
        
        # Contrôle caméra seulement si on n'est pas sur l'UI (TODO: check collision souris/UI)
        rl.update_camera(camera, rl.CAMERA_ORBITAL)
        
        # --- RENDU ---
        rl.begin_drawing()
        rl.clear_background(COLOR_BG)
        
        # 1. Rendu 3D
        rl.begin_mode_3d(camera)
        for obj in scene_objects:
            obj.draw()
        rl.end_mode_3d()
        
        # 2. Rendu UI (Overlay 2D)
        # Panneau latéral
        ui.draw_panel(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Barre d'outils (Boutons)
        if ui.draw_button("+ CUBE", 10, 10, 100, 40):
            # TODO: Faire apparaître le cube devant la caméra
            new_cube = SceneObject('cube', rl.Vector3(0, 2, 0), rl.RED, rl.Vector3(2, 2, 2))
            scene_objects.append(new_cube)
            
        if ui.draw_button("+ SPHERE", 120, 10, 100, 40):
            new_sphere = SceneObject('sphere', rl.Vector3(3, 2, 0), rl.BLUE, 1.5)
            scene_objects.append(new_sphere)

        # Bouton EXPORTER
        if ui.draw_button("EXPORT PY", SCREEN_WIDTH - 240, SCREEN_HEIGHT - 60, 230, 50):
            CodeExporter.export(scene_objects)

        rl.draw_fps(10, SCREEN_HEIGHT - 30)
        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    main()