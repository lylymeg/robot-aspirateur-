import pygame
import random
import math
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation de Robot Aspirateur Autonome")
clock = pygame.time.Clock()

# Couleurs (Thème Tech & Nettoyage)
DARK_BG = (15, 18, 25)
PANEL_BG = (25, 30, 42)
OBSTACLE_COLOR = (55, 65, 85)
CLEAN_FLOOR = (30, 40, 55)
DIRT_COLOR = (255, 180, 50)     # Poussière dorée
ROBOT_BODY = (0, 162, 255)      # Bleu tech
ROBOT_SENSOR = (255, 75, 75)    # Rayon lidar rouge
WHITE = (255, 255, 255)
GRAY = (120, 130, 150)

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 15)

class VacuumRobot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 16
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 3.0
        self.cleaning_score = 0

    def update(self, obstacles):
        # Avancer dans la direction actuelle
        next_x = self.x + math.cos(self.angle) * self.speed
        next_y = self.y + math.sin(self.angle) * self.speed

        # Détection de collision avec les bords de la pièce ou les obstacles
        collision = False
        if not (40 <= next_x <= WIDTH - 40 and 80 <= next_y <= HEIGHT - 40):
            collision = True
        else:
            for obs in obstacles:
                if math.hypot(next_x - obs["x"], next_y - obs["y"]) < self.radius + obs["radius"]:
                    collision = True
                    break

        if collision:
            # Tourner aléatoirement pour esquiver
            self.angle += random.uniform(math.pi / 2, math.pi * 1.5)
        else:
            self.x = next_x
            self.y = next_y

    def draw(self, surface):
        # Corps du robot
        pygame.draw.circle(surface, ROBOT_BODY, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius, 2)
        
        # Indicateur d'orientation (direction du robot)
        hx = self.x + math.cos(self.angle) * (self.radius + 6)
        hy = self.y + math.sin(self.angle) * (self.radius + 6)
        pygame.draw.line(surface, ROBOT_SENSOR, (self.x, self.y), (hx, hy), 3)

# Initialisation de la pièce, des obstacles et de la poussière
obstacles = [
    {"x": 300, "y": 250, "radius": 35},
    {"x": 600, "y": 400, "radius": 45},
    {"x": 700, "y": 200, "radius": 30},
    {"x": 250, "y": 450, "radius": 40}
]

# Génération de poussière aléatoire dans la pièce
dirt_particles = set()
for _ in range(120):
    while True:
        dx = random.randint(60, WIDTH - 60)
        dy = random.randint(100, HEIGHT - 40)
        # S'assurer que la poussière n'apparaît pas dans un meuble
        valid = True
        for obs in obstacles:
            if math.hypot(dx - obs["x"], dy - obs["y"]) < obs["radius"] + 10:
                valid = False
                break
        if valid:
            dirt_particles.add((dx, dy))
            break

robot = VacuumRobot(WIDTH // 2, HEIGHT // 2)

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Clic gauche : Ajouter un meuble / obstacle dans la pièce
            if mouse_pos[1] > 80:
                obstacles.append({"x": mouse_pos[0], "y": mouse_pos[1], "radius": random.randint(25, 45)})
                
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Réinitialiser la poussière et le robot
                robot = VacuumRobot(WIDTH // 2, HEIGHT // 2)
                dirt_particles.clear()
                for _ in range(120):
                    while True:
                        dx = random.randint(60, WIDTH - 60)
                        dy = random.randint(100, HEIGHT - 40)
                        valid = True
                        for obs in obstacles:
                            if math.hypot(dx - obs["x"], dy - obs["y"]) < obs["radius"] + 10:
                                valid = False
                                break
                        if valid:
                            dirt_particles.add((dx, dy))
                            break

    # Mise à jour du robot aspirateur
    robot.update(obstacles)

    # Nettoyage de la poussière au passage du robot
    cleaned = []
    for d in dirt_particles:
        if math.hypot(robot.x - d[0], robot.y - d[1]) < robot.radius:
            cleaned.append(d)
            robot.cleaning_score += 1

    for d in cleaned:
        dirt_particles.remove(d)

    screen.fill(CLEAN_FLOOR)

    # 1. Dessiner la zone de la pièce (murs délimités)
    room_rect = pygame.Rect(30, 70, WIDTH - 60, HEIGHT - 100)
    pygame.draw.rect(screen, DARK_BG, room_rect, border_radius=8)
    pygame.draw.rect(screen, GRAY, room_rect, 2, border_radius=8)

    # 2. Dessiner les obstacles (meubles)
    for obs in obstacles:
        pygame.draw.circle(screen, OBSTACLE_COLOR, (obs["x"], obs["y"]), obs["radius"])
        pygame.draw.circle(screen, GRAY, (obs["x"], obs["y"]), obs["radius"], 2)

    # 3. Dessiner la poussière restante
    for d in dirt_particles:
        pygame.draw.circle(screen, DIRT_COLOR, d, 3)

    # 4. Dessiner le robot
    robot.draw(screen)

    # 5. En-tête HUD et Instructions
    title_txt = font_medium.render("SIMULATION DE ROBOT ASPIRATEUR AUTONOME", True, WHITE)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 15))

    stats_txt = font_small.render(f"Poussières aspirées : {robot.cleaning_score} / 120 | Reste : {len(dirt_particles)}", True, DIRT_COLOR)
    screen.blit(stats_txt, (35, 45))

    inst_txt = font_small.render("CLIC GAUCHE : Ajouter un meuble | R : Réinitialiser", True, GRAY)
    screen.blit(inst_txt, (WIDTH - inst_txt.get_width() - 35, 45))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()