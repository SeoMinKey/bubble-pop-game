import pygame
# from scene_manager import SceneManager
# from game_scene import GameScene
from config import SCREEN_HEIGHT,SCREEN_WIDTH

class MenuScene:
    # def __init__(self,manager):
    #     self.manager=manager
    #     # FIXME: 폰트 임시 설정
    #     self.font=pygame.font.Font(None,48)
    #     # FIXME: 메뉴 항목
    #     # self.options=['Start Game','Settings','Quit']
    #     self.opts=['Start Game','Quit']
    #     self.idx=0
    def __init__(self,manager):
        self.manager=manager
        self.font=pygame.font.Font(None,80)
        self.small=pygame.font.Font(None,40)

    # def handle_event(self,event):
    #     if event.type==pygame.KEYDOWN:
    #         # 위로 이동하면
    #         if event.key==pygame.K_UP:
    #             self.selected_index=(self.selected_index-1)%len(self.options)
    #         # 아래로 이동하면
    #         elif event.key==pygame.K_DOWN:
    #             self.selected_index=(self.selected_index+1)%len(self.options)
    #         # 선택하면
    #         elif event.key==pygame.K_RETURN:
    #             # Start Game 선택 시
    #             if self.selected_index==0:
    #                 # self.manager.change(GameScene(self.manager))
    #                 self.manager.change('game')
    #                     # scene_manager에 game 요청해서 팩토리에서 game 인스턴스 만들어짐.
    #             # Exit 선택 시
    #             elif self.selected_index==1:
    #                 pygame.quit()
    #                 raise SystemExit()
    def handle_event(self,event):
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_SPACE:
                self.manager.change('game')

    # def draw(self,screen):
    #     # FIXME: 배경 색상 임시 설정
    #     screen.fill((30,30,30))
    #     for index, option in enumerate(self.options):
    #         # FIXME: RGB 값 임시 설정
    #         color=(255,255,255)if index==self.selected_index else (180,180,180)

    #         text=self.font.render(option,True,color)
    #         # FIXME: 위치 조정: y좌표 조정
    #         # rect=text.get_rect(center=(400,300+index*60))
    #         rect=text.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2+index*60))
    #         screen.blit(text,rect)
    def draw(self,screen):
        screen.fill((0,0,0))
        title=self.font.render('BUBBLE POP',True,(255,255,255))
        sub=self.small.render('press SPACE to start',True,(200,200,200))

        screen.blit(title,title.get_rect(center=(screen.get_width()//2,screen.get_height()//2-60)))
        screen.blit(sub,sub.get_rect(center=(screen.get_width()//2,screen.get_height()//2+20)))

    # def run(self):
    #     scr=pygame.display.get_surface()
    #     clk=pygame.time.Clock()

    #     while True:
    #         for e in pygame.event.get():
    #             if e.type==pygame.QUIT:
    #                 pygame.quit();raise SystemExit
    #             if e.type==pygame.KEYDOWN:
    #                 if e.key==pygame.K_UP:self.idx=(self.idx-1)%len(self.opts)
    #                 elif e.key==pygame.K_DOWN:self.idx=(self.idx+1)%len(self.opts)
    #                 elif e.key==pygame.K_RETURN:
    #                     if self.idx==0:
    #                         self.manager.change("game")
    #                         return
    #                     else:
    #                         pygame.quit();raise SystemExit

    #         scr.fill((25,25,25))
    #         for i,t in enumerate(self.opts):
    #             col=(255,255,255) if i==self.idx else (120,120,120)
    #             txt=self.font.render(t,True,col)
    #             r=txt.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2+i*60))
    #             scr.blit(txt,r)

    #         pygame.display.flip()
    #         clk.tick(60)

    def update(self):
        # TODO: 업데이트할 내용 있으면 나중에 구현
        pass
