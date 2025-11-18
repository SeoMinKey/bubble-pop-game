class SceneManager:
#     def __init__(self,factory):
#         self.factory = factory
#         """씬 종류에 따른 적절한 씬 객체 생성"""
#         self.current_scene=None
    def __init__(self,scene_factory):
        self.scene_factory=scene_factory
        self.current_scene=None

    # def change(self,scene_name):
    #     """씬 이름 받아서 팩토리로부터 새 씬 객체 생성"""
    #     self.current_scene=self.factory(scene_name,self)
    def change(self,scene_name):
        self.current_scene=self.scene_factory(scene_name,self)

    # def handle_event(self,event):
    #     """현재 씬 이벤트 처리"""
    #     if self.current_scene and hasattr(self.current_scene,'handle_event'):
    #         self.current_scene.handle_event(event)
    def handle_event(self,event):
        if self.current_scene:
            self.current_scene.handle_event(event)

    # def update(self,dt):
    #     """현재 씬 업데이트"""
    #     if self.current_scene and hasattr(self.current_scene,'update'):
    #         self.current_scene.update(dt)
    def update(self):
        if self.current_scene:
            self.current_scene.update()

    # def draw(self,screen):
    #     """현재 씬 그리기."""
    #     if self.current_scene and hasattr(self.current_scene,'draw'):
    #         self.current_scene.draw(screen)
    def draw(self,screen):
        if self.current_scene:
            self.current_scene.draw(screen)

#     def run(self):
#         """현재 씬의 run() 또는 loop() 실행"""
#         if hasattr(self.current_scene, "run"):
#             self.current_scene.run()
