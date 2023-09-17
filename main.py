import random

import pygame
import sys
from src.button import Button
from src.config import *
from src.particle import ParticleEmitter
import numpy as np

# Initialisation de Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.NOFRAME)
pygame.display.set_caption(app_name)
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)

# Classe de base pour les menus
class BaseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.background_image = pygame.image.load("assets/images/backgrounds/background1.jpg")
        self.buttons = []
        self.particle_emitter = None

    def init_particle_emitter(self, particle_type, num_particles, particle_color1, particle_color2, particle_size, particle_speed):
        self.particle_emitter = ParticleEmitter(self.screen, particle_type, num_particles, particle_color1, particle_color2,
                                                particle_size, particle_speed)

    def handle_click(self):
        for button in self.buttons:
            if button.is_clicked():
                button.command()

    def draw(self):
        x, y = pygame.mouse.get_pos()
        dx = (x - WIDTH / 2) / 10
        dy = (y - HEIGHT / 2) / 10
        zoom = 1.1
        img_width = self.background_image.get_width() * zoom
        img_height = self.background_image.get_height() * zoom
        img_x = (WIDTH - img_width) / 2 + dx
        img_y = (HEIGHT - img_height) / 2 + dy
        scaled_background = pygame.transform.scale(self.background_image, (int(img_width), int(img_height)))
        self.screen.blit(scaled_background, (img_x, img_y))
        for button in self.buttons:
            button.draw(self.screen)

# Classe du menu principal
def quit_game():
    pygame.quit()
    sys.exit()

def switch_to_options():
    switch_to_menu(options_menu)

def switch_to_conway():
    switch_to_menu(conway_menu)

class MainMenu(BaseMenu):
    def __init__(self, screen):
        super().__init__(screen)

        self.conway_button = Button("Jeu de Conway", (WIDTH / 2, 250, 200, 50), switch_to_conway)
        self.options_button = Button("Options", (WIDTH / 2, 350, 200, 50), switch_to_options)
        self.quit_button = Button("Quitter", (WIDTH / 2, 450, 200, 50), quit_game)

        self.buttons = [self.conway_button, self.options_button, self.quit_button]

        self.init_particle_emitter("floating", num_particles=75, particle_color1=(152, 37, 0),
                                   particle_color2=(32, 14, 7), particle_size=6, particle_speed=10)

        self.particle_emitter.start_snowfall()

# Classe du menu des options
def switch_to_main_menu():
    switch_to_menu(main_menu)

class OptionsMenu(BaseMenu):
    def __init__(self, screen):
        super().__init__(screen)

        self.back_button = Button("Retour", (WIDTH / 2, 400, 200, 50), switch_to_main_menu)

        self.buttons = [self.back_button]

        self.init_particle_emitter("floating", num_particles=100, particle_color1=(101, 109, 112),
                                   particle_color2=(0, 0, 0), particle_size=8, particle_speed=5)

        self.particle_emitter.start_snowfall()

class ConwayMenu(BaseMenu):
    def __init__(self, screen):
        super().__init__(screen)

        self.back_button = Button("Retour au Menu Principal", (WIDTH / 2, 500, 200, 50), switch_to_main_menu)

        # Bouton pour démarrer/arrêter la simulation
        self.start_stop_button = Button("Démarrer", (WIDTH / 2, 50, 100, 40), self.toggle_simulation)

        self.buttons = [self.back_button, self.start_stop_button]

        # Dimensions de la grille
        self.grid_width = 16
        self.grid_height = 16
        self.cell_size = 16

        # Position de départ pour centrer la grille
        self.grid_x = (WIDTH - self.grid_width * self.cell_size) // 2
        self.grid_y = (HEIGHT - self.grid_height * self.cell_size) // 2

        # Initialisez la grille avec des cellules aléatoires
        self.grid = np.random.choice([0, 1], size=(self.grid_width, self.grid_height))

        # État de la simulation
        self.running = False

        # Intervalle de mise à jour de la simulation (en millisecondes)
        self.update_interval = 500  # Par défaut, une mise à jour toutes les 500 ms
        self.last_update_time = pygame.time.get_ticks()

    def toggle_simulation(self):
        # Inversez l'état de la simulation (démarrer/arrêter)
        self.running = not self.running
        self.start_stop_button.text = "Arrêter" if self.running else "Démarrer"

    def update_conway(self):
        if self.running:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_update_time >= self.update_interval:
                self.last_update_time = current_time

                new_grid = np.copy(self.grid)

                for x in range(self.grid_width):
                    for y in range(self.grid_height):
                        # Comptez le nombre de voisins vivants
                        neighbors = np.sum(self.grid[max(0, x - 1):min(self.grid_width, x + 2),
                                                     max(0, y - 1):min(self.grid_height, y + 2)]) - self.grid[x, y]

                        # Appliquez les règles de Conway
                        if self.grid[x, y] == 1 and (neighbors < 2 or neighbors > 3):
                            new_grid[x, y] = 0
                        elif self.grid[x, y] == 0 and neighbors == 3:
                            new_grid[x, y] = 1

                self.grid = new_grid

    def draw(self):
        super().draw()

        # Dessinez la grille du jeu de Conway au centre de l'écran
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                color = (0, 0, 0) if self.grid[x, y] == 0 else (255, 255, 255)
                cell_rect = pygame.Rect(self.grid_x + x * self.cell_size, self.grid_y + y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(self.screen, color, cell_rect)

    def handle_click(self):
        super().handle_click()

        # Réinitialisez la grille avec des cellules aléatoires lorsqu'un bouton est cliqué
        self.grid = np.random.choice([0, 1], size=(self.grid_width, self.grid_height))

    def handle_keydown(self, key):
        if key == pygame.K_SPACE:
            self.toggle_simulation()

    def update(self):
        super().update()

        # Mettez à jour la simulation du jeu de Conway
        self.update_conway()

        # Calculer les FPS
        fps = int(clock.get_fps())

        # Afficher les FPS en haut à gauche
        fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
        self.screen.blit(fps_text, (10, 10))

# Fonction pour passer d'un menu à un autre
def switch_to_menu(new_menu):
    global current_menu, switching_menu, alpha
    switching_menu = new_menu
    alpha = 0


# Fonction pour dessiner le menu actuellement visible
def draw_menu(menu):
    menu.draw()
    if menu.particle_emitter:
        menu.particle_emitter.update()
        menu.particle_emitter.draw()


# Fonction pour effectuer une transition de fondu
def fade_out(screen):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))

    for alpha in range(0, 50, 1):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(20)


# Instance des menus
main_menu = MainMenu(screen)
options_menu = OptionsMenu(screen)
conway_menu = ConwayMenu(screen)

# Variables pour gérer les menus
current_menu = main_menu
switching_menu = None
alpha = 0
fade_speed = 30


# Boucle de jeu principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                current_menu.handle_click()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                fade_out(screen)
                running = False

    # Gérer la transition de fondu
    if switching_menu:
        alpha += fade_speed
        if alpha >= 255:
            alpha = 255
            current_menu = switching_menu
            switching_menu = None
    elif alpha > 0:
        alpha -= fade_speed
        if alpha < 0:
            alpha = 0

    # Calculer les FPS
    fps = int(clock.get_fps())

    # Afficher le menu actuellement visible
    x, y = pygame.mouse.get_pos()
    dx = (x - WIDTH / 2) / 10
    dy = (y - HEIGHT / 2) / 10
    zoom = 1.1
    img_width = current_menu.background_image.get_width() * zoom
    img_height = current_menu.background_image.get_height() * zoom
    img_x = (WIDTH - img_width) / 2 + dx
    img_y = (HEIGHT - img_height) / 2 + dy
    scaled_background = pygame.transform.scale(current_menu.background_image, (int(img_width), int(img_height)))
    screen.blit(scaled_background, (img_x, img_y))

    # Update and draw the ParticleEmitter
    if current_menu.particle_emitter:
        current_menu.particle_emitter.update()
        current_menu.particle_emitter.draw()

    # Appeler la méthode draw de ConwayMenu si le menu actuel est ConwayMenu
    if isinstance(current_menu, ConwayMenu):
        current_menu.draw()

    # Dessiner les boutons
    for button in current_menu.buttons:
        button.draw(screen)

    # Afficher les FPS en haut à gauche
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

    # Dessiner l'effet de fondu
    if alpha > 0:
        fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, alpha))
        screen.blit(fade_surface, (0, 0))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()