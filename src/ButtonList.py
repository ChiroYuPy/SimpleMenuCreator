import pygame
import sys

from src.Button import Button

# Initialisation de pygame
pygame.init()

# Paramètres de la fenêtre
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Selectable Options List")

# Liste d'éléments pour la liste d'options
items = ["Option 1", "Option 2", "Option 3", "Option 4"]

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Police
font = pygame.font.Font(None, 36)

# Utilisez la classe Button pour créer des boutons pour chaque option
buttons = []


def option_selected(index):
    print(f"Option selected: {items[index]}")


for i, item in enumerate(items):
    button = Button(
        text=item,
        rect=(screen_width // 2, 100 + i * 70, 200, 50),  # Position et taille du bouton
        command=lambda i=i: option_selected(i),  # Utilisation d'une lambda pour transmettre l'indice
        font_size=36,
        default_top_color='#475F77',  # Couleur par défaut du bouton
        hover_top_color='#D74B4B',  # Couleur lors du survol du bouton
        bottom_color='#354B5E',  # Couleur de la partie inférieure du bouton
        text_color=(255, 255, 255)  # Couleur du texte
    )
    buttons.append(button)

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for button in buttons:
            button.is_clicked()

    screen.fill(WHITE)

    # Dessiner les boutons
    for button in buttons:
        button.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
