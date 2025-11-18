# src/main.py
import pygame
from scene_manager import SceneManager
from menu_scene import MenuScene
from game import Game
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

def scene_factory(name, manager):
    if name == 'menu':
        return MenuScene(manager)
    if name == 'game':
        return Game(manager)
    raise ValueError(f'unknown scene: {name}')

def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except:
        pass

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    manager = SceneManager(scene_factory)
    manager.change('menu')

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.handle_event(event)

        manager.update(dt)
        manager.draw(screen)
        pygame.display.flip()

        # if current scene is a Game and game.running False -> return to menu or exit
        cur = manager.current_scene
        if hasattr(cur, 'running') and not cur.running:
            # Game이 끝났으면 메뉴로 돌아가거나 앱 종료 — 지금은 메뉴로 복귀
            # 만약 스테이지 파일이 끝나서 전체 종료라면 manager.change('menu') 대신 running=False로도 가능
            manager.change('menu')

    pygame.quit()

if __name__ == "__main__":
    main()
