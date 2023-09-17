import pygame


class Button:
    def __init__(self, text, rect, command=None, font_size=None,
                 default_top_color=None, hover_top_color=None,
                 bottom_color=None, text_color=None):
        x, y, w, h = rect
        pos = x, y
        x = pos[0] - w / 2
        y = pos[1] - h / 2
        self.elevation = None
        self.pressed = False
        self.command = command
        self.elevation = 6
        self.dyn_elevation = self.elevation
        self.original_y_position = pos[1]
        self.top_rect = pygame.Rect((x, y), (w, h))
        self.default_top_color = default_top_color if default_top_color is not None else '#475F77'
        self.hover_top_color = hover_top_color if hover_top_color is not None else '#D74B4B'
        self.font_size = font_size if font_size is not None else 26
        self.bottom_rect = pygame.Rect((x, y), (w, self.elevation))
        self.bottom_color = bottom_color if bottom_color is not None else '#354B5E'
        gui_font = pygame.font.Font(None, self.font_size)
        self.text_surf = gui_font.render(text, True, text_color if text_color is not None else (255, 255, 255))
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    def draw(self, screen):
        self.top_rect.y = self.original_y_position - self.dyn_elevation
        self.text_rect.center = self.top_rect.center
        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dyn_elevation

        # Utilisation de la couleur de survol appropriée en fonction de l'état
        if self.is_hovered():
            top_color = self.hover_top_color
        else:
            top_color = self.default_top_color

        pygame.draw.rect(screen, self.bottom_color, self.bottom_rect, border_radius=12)
        pygame.draw.rect(screen, top_color, self.top_rect, border_radius=12)
        screen.blit(self.text_surf, self.text_rect)
        self.is_clicked()

    def is_hovered(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.top_rect.collidepoint(mouse_pos)

    def is_clicked(self):
        if self.is_hovered():
            if pygame.mouse.get_pressed()[0]:
                self.dyn_elevation = 0
                if self.command:
                    self.command()
                self.pressed = True
            else:
                self.dyn_elevation = self.elevation
                if self.pressed:
                    self.pressed = False
        else:
            self.dyn_elevation = self.elevation

