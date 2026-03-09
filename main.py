import pygame
import pip


pygame.init()

WIDTH = 800
HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("My Tower Defense")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Очистка экрана
    screen.fill(WHITE)

    #Обновление экрана
    pygame.display.flip()

    clock.tick(60)

pygame.quit()