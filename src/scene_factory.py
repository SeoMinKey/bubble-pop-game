from menu_scene import MenuScene
from game_scene_wrapper import GameSceneWrapper

def scene_factory(name,manager):
    if name=='menu':
        return MenuScene(manager)
    if name=='game':
        return GameSceneWrapper(manager)
    raise ValueError(f'unknown scene: {name}')
