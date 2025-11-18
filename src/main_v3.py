import pygame
import sys

from config import SCREEN_WIDTH,SCREEN_HEIGHT
from scene_manager import SceneManager
from scene_factory import scene_factory

def main():
    pygame.init()
    pygame.mixer.init()

    screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    clock=pygame.time.Clock()

    manager=SceneManager(scene_factory)
    manager.change('menu')

    running=True
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            manager.handle_event(event)

        manager.update()
        manager.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__=='__main__':
    main()
