import pygame
import sys

from src.Config import *
from src.Button import Button

pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
font = pygame.font.Font(None, 36)

items = ["Option 1", "Option 2", "Option 3", "Option 4"]
buttons = []


def option_selected(index):
    print(f"Option selected: {items[index]}")


for i, item in enumerate(items):
    button = Button(
        text=item,
        rect=(screen_width // 2, 100 + i * 70, 200, 50),
        command=lambda i=i: option_selected(i),
        font_size=36,
        default_top_color='#475F77',
        hover_top_color='#D74B4B',
        bottom_color='#354B5E',
        text_color=(255, 255, 255)
    )
    buttons.append(button)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for button in buttons:
            button.is_clicked()
    screen.fill(WHITE)
    for button in buttons:
        button.draw(screen)
    pygame.display.flip()
pygame.quit()
sys.exit()
