import sys
import numpy as np
import pygame

from src.Config import *
from src.Button import Button
from src.Particle import ParticleEmitter

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

    def init_particle_emitter(self, particle_type, num_particles, particle_color1, particle_color2, particle_size,
                              particle_speed):
        self.particle_emitter = ParticleEmitter(self.screen, particle_type, num_particles, particle_color1,
                                                particle_color2,
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


# Classe du menu de Conway
class ConwayMenu(BaseMenu):
    def __init__(self, screen):
        super().__init__(screen)

        self.selected_preset_name = None
        self.back_button = Button("Retour", (WIDTH / 2, HEIGHT * 0.9, 200, 50), switch_to_main_menu)
        self.start_button = Button("Démarrer", (WIDTH * 0.76, HEIGHT * 0.2, 100, 50), self.start_conway)
        self.stop_button = Button("Arrêter", (WIDTH * 0.76, HEIGHT * 0.3, 100, 50), self.stop_conway)
        self.clear_button = Button("Effacer tout", (WIDTH * 0.76, HEIGHT * 0.4, 100, 50), self.clear_grid)
        self.randomize_button = Button("Randomiser", (WIDTH * 0.76, HEIGHT * 0.5, 100, 50), self.randomize_grid)
        self.buttons = [self.back_button, self.start_button, self.stop_button, self.clear_button, self.randomize_button]

        # Liste de boutons pour les presets
        self.preset_buttons = [
            Button("Preset 1", (WIDTH * 0.76, HEIGHT * 0.6, 100, 50), self.select_preset_1),
            Button("Preset 2", (WIDTH * 0.76, HEIGHT * 0.7, 100, 50), self.select_preset_2),
            Button("Preset 3", (WIDTH * 0.76, HEIGHT * 0.8, 100, 50), self.select_preset_3),
            Button("Preset 4", (WIDTH * 0.85, HEIGHT * 0.6, 100, 50), self.select_preset_4),
            Button("Preset 5", (WIDTH * 0.85, HEIGHT * 0.7, 100, 50), self.select_preset_5),
        ]
        self.buttons.extend(self.preset_buttons)  # Ajoutez les boutons de presets à la liste principale de boutons

        # Surface (viewport)
        self.viewport_width = 512
        self.viewport_height = 512
        self.viewport = pygame.Surface((self.viewport_width, self.viewport_height))
        self.viewport_rect = self.viewport.get_rect(center=(WIDTH / 2, HEIGHT / 2))  # Ajuster le centre

        # Dimensions de la grille du jeu de la vie
        self.grid_width = 64
        self.grid_height = 64
        self.cell_size = self.viewport_width // self.grid_width
        self.grid = np.random.randint(2, size=(self.grid_width, self.grid_height))
        self.running_conway = False

        self.presets = [
            [(-1, 0), (0, 0), (1, 0)],
            [(0, 1), (0, 0), (1, 0)],
            [(0, -1), (0, 0), (0, 1), (1, 1), (-1, 1)],
            [(-2, -1), (-2, 0), (-2, 1), (-1, -2), (-1, 2), (0, -2), (0, 2), (1, -2), (1, 2), (2, -1), (2, 0), (2, 1)],
        ]

        self.selected_preset = None  # Le preset sélectionné
        self.preview_cells = []  # Les cellules de l'aperçu
        self.selected_cell_x = 0  # Ajout de l'initialisation de selected_cell_x
        self.selected_cell_y = 0  # Ajout de l'initialisation de selected_cell_y

    def draw_viewport(self, surface, rect):
        # Dessinez la grille du jeu de la vie de Conway au centre du viewport
        viewport_x = (WIDTH - self.viewport_width) / 2
        viewport_y = (HEIGHT - self.viewport_height) / 2

        # Effacez le viewport
        self.viewport.fill((0, 0, 0))

        # Dessinez la grille avec des cercles
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if self.grid[x, y] == 1:
                    cell_x = x * self.cell_size + self.cell_size // 2
                    cell_y = y * self.cell_size + self.cell_size // 2
                    cell_radius = self.cell_size // 2
                    pygame.draw.circle(self.viewport, (255, 255, 255), (cell_x, cell_y), cell_radius)

        # Copiez le viewport dans la surface principale
        surface.blit(self.viewport, (viewport_x, viewport_y))

    def start_conway(self):
        self.running_conway = True

    def stop_conway(self):
        self.running_conway = False

    def clear_grid(self):
        # Mettre toutes les cellules à mortes (état 0)
        self.grid = np.zeros((self.grid_width, self.grid_height), dtype=int)

    def randomize_grid(self):
        # Randomiser les cellules
        self.grid = np.random.randint(2, size=(self.grid_width, self.grid_height))

    def select_preset_1(self):
        self.selected_preset = self.presets[0]
        self.selected_preset_name = "Preset 1"

    def select_preset_2(self):
        self.selected_preset = self.presets[1]
        self.selected_preset_name = "Preset 2"

    def select_preset_3(self):
        self.selected_preset = self.presets[2]
        self.selected_preset_name = "Preset 3"

    def select_preset_4(self):
        self.selected_preset = self.presets[3]
        self.selected_preset_name = "Preset 4"

    def select_preset_5(self):
        self.selected_preset = self.presets[4]
        self.selected_preset_name = "Preset 5"

    def draw_preset_preview(self):
        if self.selected_preset:
            preview_grid_size = 16
            cell_size = self.viewport_width // preview_grid_size
            grid_x = WIDTH*0.82
            grid_y = HEIGHT/2
            for cx, cy in self.selected_preset:
                # Calculez les coordonnées du centre du cercle
                circle_x = grid_x + cx * cell_size/2
                circle_y = grid_y + cy * cell_size/2
                circle_radius = cell_size // 4
                pygame.draw.circle(self.screen, (255, 255, 255), (circle_x, circle_y), circle_radius)


    def update_conway_grid(self):
        if self.running_conway:
            new_grid = np.copy(self.grid)

            for x in range(self.grid_width):
                for y in range(self.grid_height):
                    # Règles du jeu de la vie de Conway
                    neighbors = self.get_neighbors(x, y)
                    if self.grid[x, y] == 1:
                        if neighbors < 2 or neighbors > 3:
                            new_grid[x, y] = 0
                    else:
                        if neighbors == 3:
                            new_grid[x, y] = 1

            self.grid = new_grid

    def get_neighbors(self, x, y):
        neighbors = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    neighbors += self.grid[nx, ny]
        return neighbors

    def handle_mouse_click(self, x, y):
        # Convertissez les coordonnées de la souris en coordonnées de la grille
        grid_x = (x - self.viewport_rect.left) // self.cell_size
        grid_y = (y - self.viewport_rect.top) // self.cell_size

        # Vérifiez si les coordonnées sont valides
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            # Inversez l'état de la cellule (vivante ou morte)
            self.grid[grid_x, grid_y] = 1 - self.grid[grid_x, grid_y]

            # Placez le preset de manière à ce que la cellule (0, 0) du preset corresponde à la cellule sélectionnée
            self.place_preset(grid_x, grid_y)

    def place_preset(self, x, y):
        if self.selected_preset:
            # Calculez l'offset en fonction de la cellule sélectionnée
            offset_x, offset_y = x - 0, y - 0  # Ajustez ces valeurs en fonction de la cellule (0, 0) du preset

            # Vérifiez si le preset peut être placé entièrement à l'intérieur de la grille
            preset_fits = all(0 <= cx + offset_x < self.grid_width and 0 <= cy + offset_y < self.grid_height
                              for cx, cy in self.selected_preset)

            if preset_fits:
                # Placez le preset dans la grille
                for cx, cy in self.selected_preset:
                    self.grid[cx + offset_x, cy + offset_y] = 1

    def handle_mouse_motion(self, x, y):
        self.draw_preview(x, y)

    def draw_selected_preset(self):
        if self.selected_preset:
            preset_name = f"Preset {self.presets.index(self.selected_preset) + 1}"
            text = font.render(preset_name, True, (255, 255, 255))
            screen.blit(text, (10, 50))

    def draw_preview(self, x, y):
        if self.selected_preset:
            # Effacez l'aperçu précédent
            for cx, cy in self.preview_cells:
                pygame.draw.rect(self.viewport, (0, 0, 0),
                                 (cx * self.cell_size, cy * self.cell_size, self.cell_size, self.cell_size))

            # Calculez l'offset en fonction de la position de la souris
            offset_x, offset_y = x - self.selected_cell_x, y - self.selected_cell_y

            # Créez un nouvel aperçu
            self.preview_cells = [(cx + offset_x, cy + offset_y) for cx, cy in self.selected_preset]

            # Dessinez l'aperçu en gris clair
            for cx, cy in self.preview_cells:
                if 0 <= cx < self.grid_width and 0 <= cy < self.grid_height:
                    cell_x = cx * self.cell_size
                    cell_y = cy * self.cell_size
                    pygame.draw.rect(self.viewport, (200, 200, 200), (cell_x, cell_y, self.cell_size, self.cell_size),
                                     1)


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

# Boucle principale du jeu
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                if isinstance(current_menu, ConwayMenu):
                    # Appel de la méthode pour gérer le clic de souris
                    current_menu.handle_mouse_click(event.pos[0], event.pos[1])
                current_menu.handle_click()
        if event.type == pygame.MOUSEMOTION:
            if isinstance(current_menu, ConwayMenu):
                current_menu.handle_mouse_motion(event.pos[0], event.pos[1])
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

    # Mettre à jour la simulation du jeu de la vie de Conway si elle est en cours
    if isinstance(current_menu, ConwayMenu) and current_menu.running_conway:
        current_menu.update_conway_grid()

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

    # Dessiner le viewport
    if isinstance(current_menu, ConwayMenu):
        current_menu.draw_viewport(screen, current_menu.viewport_rect)

        # Dessiner le contenu à côté du viewport
        # Vous pouvez ajouter du code ici pour dessiner ce que vous voulez à côté du viewport
        # Par exemple, pour afficher le nom du preset actuellement sélectionné :
        preset_text = font.render(f"Preset: {current_menu.selected_preset_name}", True, (255, 255, 255))
        screen.blit(preset_text, (10, 50))  # Ajustez la position du texte selon vos préférences

        # Dessiner les boutons du preset sélectionné
        for button in current_menu.preset_buttons:
            button.draw(screen)

    # Dessiner les boutons
    for button in current_menu.buttons:
        button.draw(screen)

    # Afficher les FPS en haut à gauche
    fps_text = font.render(f"FPS: {fps}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))

    # Afficher le nom du preset actuellement sélectionné
    if isinstance(current_menu, ConwayMenu) and current_menu.selected_preset:
        preset_text = font.render(f"Preset: {current_menu.selected_preset_name}", True, (255, 255, 255))
        screen.blit(preset_text, (10, 50))  # Ajustez la position du texte selon vos préférences

    # Dessiner les boutons du menu
    for button in current_menu.buttons:
        button.draw(screen)

    # Dessiner l'aperçu du preset sélectionné
    if isinstance(current_menu, ConwayMenu) and current_menu.selected_preset:
        current_menu.draw_preset_preview()

    # Dessiner l'effet de fondu
    if alpha > 0:
        fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, alpha))
        screen.blit(fade_surface, (0, 0))

    pygame.display.flip()
    clock.tick(FPS)
