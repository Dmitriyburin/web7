import pygame
import requests
import sys
import os
from search import Search

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))


def update(event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
        point.spn = (point.spn[0] * 2, point.spn[1] * 2)
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
        point.spn = (point.spn[0] / 2, point.spn[1] / 2)
    if event.type == pygame.KEYUP and event.key == pygame.K_UP:
        point.ll = (point.ll[0], point.ll[1] + point.spn[1])
    if event.type == pygame.KEYUP and event.key == pygame.K_DOWN:
        point.ll = (point.ll[0], point.ll[1] - point.spn[1])
    if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
        point.ll = (point.ll[0] - point.spn[0], point.ll[1])
    if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
        point.ll = (point.ll[0] + point.spn[0], point.ll[1])
    if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
        pygame.display.iconify()
    param = {
        "ll": ",".join(map(str, point.ll)),
        "spn": ",".join(map(str, point.spn)),
        "l": "map",
        # "pt": ",".join(map(str, point.ll))
    }
    return point.map_api(param)


point = Search()
param = point.point_param
map_file = point.map_api(param)
screen.blit(pygame.image.load(map_file), (0, 0))
text = ["Проверка"]
if text:
    font = pygame.font.Font(None, 20)
    for i in range(len(text)):
        line = font.render(text[i], True, (0, 0, 0))
        screen.blit(line, (5, 5 + i * 25))

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYUP:
            map_file = update(event)
            screen.blit(pygame.image.load(map_file), (0, 0))

    pygame.display.flip()

pygame.quit()
os.remove(map_file)
