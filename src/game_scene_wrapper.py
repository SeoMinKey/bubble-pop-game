import threading
import pygame
from game import Game

class GameSceneWrapper:
    def __init__(self,manager):
        self.manager=manager
        self.game=None
        self.thread=None
        self.done=False

        self.start_game()

    def start_game(self):
        self.game=Game()

        # Game.run()은 자체 루프를 가지므로 별도 스레드로 실행
        def _run():
            self.game.run()
            self.done=True

        self.thread=threading.Thread(target=_run,daemon=True)
        self.thread.start()

    def handle_event(self,event):
        pass    # Game.run() 자체 루프에서 event 처리함

    def update(self):
        if self.done:
            self.manager.change('menu')

    def draw(self,screen):
        pass    # Game 자체가 화면을 그리므로 여기선 비움
