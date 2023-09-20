import pygame


class TextBox:
    def __init__(self, x, y, width, height, text_color=(0, 0, 0), font_size=24, background_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text_color = text_color
        self.font_size = font_size
        self.background_color = background_color
        self.text = ""
        self.active = False
        self.font = pygame.font.Font(None, self.font_size)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = (0, 0, 0) if self.active else (255, 255, 255)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    # Lorsque l'utilisateur appuie sur Entrée, l'entrée est terminée.
                    self.active = False
                elif event.key == pygame.K_BACKSPACE:
                    # Lorsque l'utilisateur appuie sur Retour arrière, supprime le dernier caractère.
                    self.text = self.text[:-1]
                else:
                    # Ajoute le caractère saisi à la chaîne de texte.
                    self.text += event.unicode

    def update(self):
        # Crée une copie de la zone de texte avec un rectangle blanc pour effacer le texte précédent.
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.surface.fill(self.background_color)
        self.surface.set_alpha(200)
        text_surface = self.font.render(self.text, True, self.text_color)
        self.surface.blit(text_surface, (5, 5))
        self.rect.width = max(200, text_surface.get_width() + 10)

    def draw(self, screen):
        screen.blit(self.surface, self.rect)
