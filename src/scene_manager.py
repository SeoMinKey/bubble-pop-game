class SceneManager:
    # def __init__(self,start_scene):
    #     self.current_scene = start_scene
    def __init__(self, factory):
        self.factory = factory
        self.current_scene=None


    def change(self,scene_name):
        """씬 전환"""
        self.current_scene=self.factory(scene_name,self)

    def handle_event(self,event):
        """현재 씬 이벤트 처리"""
        self.current_scene.handle_event(event)

    def update(self):
        """현재 씬 업데이트"""
        self.current_scene.update()

    def draw(self,screen):
        """현재 씬 그리기."""
        self.current_scene.draw(screen)
