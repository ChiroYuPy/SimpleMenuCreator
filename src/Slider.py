import pygame

class Slider:
    def __init__(self, screen, x, y, w, h, min_value, max_value, segments=0, default_value=None,
                 bar_color=None, cursor_color=None):
        self.screen = screen
        self.width, self.height = w, h
        self.x, self.y = x-w/2, y-h/2
        self.min_value, self.max_value = min_value, max_value
        self.num_segments = None if segments is None or segments <= 0 else segments
        self.value = default_value if default_value is not None else (min_value + max_value) / 2
        self.dragging = False
        self.bar_color = bar_color if bar_color is not None else '#475F77'
        self.cursor_color = cursor_color if cursor_color is not None else '#D74B4B'

    def draw(self):
        radius = self.height // 2

        # Dessiner la barre du slider
        pygame.draw.circle(self.screen, self.bar_color, (self.x + radius, self.y + self.height // 2 + 1), radius)
        pygame.draw.circle(self.screen, self.bar_color, (self.x + self.width - radius, self.y + self.height // 2 + 1), radius)
        pygame.draw.line(self.screen, self.bar_color, (self.x + radius, self.y + self.height // 2), (self.x + self.width - radius, self.y + self.height // 2), self.height)

        # Dessiner les segments s'il y en a
        if self.num_segments is not None:
            segment_width = (self.width - 2 * radius) / self.num_segments
            segment_radius = 2  # Rayon des points noirs
            for i in range(self.num_segments + 1):
                segment_x = int(self.x + radius + i * segment_width)
                segment_y = int(self.y + self.height / 2)  # Y au milieu de la hauteur du slider
                pygame.draw.circle(self.screen, (0, 0, 0), (segment_x, segment_y), segment_radius)

        # Dessiner le curseur
        radius = self.height
        cursor_x = int(self.x + (self.value - self.min_value) / (self.max_value - self.min_value) * (self.width - 2 * radius)) + radius
        pygame.draw.circle(self.screen, self.cursor_color, (cursor_x, self.y + self.height // 2), radius)

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()

        if pressed[0]:
            # Vérifier si la souris est dans la zone de prise en main (rectangle + curseur)
            if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
                self.dragging = True

        if self.dragging:
            # Mettre à jour la valeur en fonction de la position du curseur
            radius = self.height // 2  # Rayon des extrémités arrondies
            cursor_x = mouse_x - self.x  # Position relative du curseur par rapport au slider
            cursor_x = max(radius, min(self.width - radius, cursor_x))  # Limiter la position du curseur aux extrémités arrondies
            self.value = (cursor_x - radius) / (self.width - 2 * radius) * (self.max_value - self.min_value) + self.min_value
            self.value = max(self.min_value, min(self.max_value, self.value))

        if not pressed[0]:
            self.dragging = False

        # Arrondir la valeur aux positions segmentées les plus proches
        if self.num_segments is not None:
            segment_width = self.width / self.num_segments
            closest_segment = round(
                (self.value - self.min_value) / (self.max_value - self.min_value) * self.num_segments)
            self.value = closest_segment * (self.max_value - self.min_value) / self.num_segments + self.min_value

    def get_value(self):
        return self.value
