import cocos
import cocos.actions as ac
import cocos.layer
import cocos.sprite
import cocos.collision_model as cm
import cocos.euclid as eu
from cocos import mapcolliders
import sys
import pygame
from pygame.locals import *
import cocos.tiles
from collections import defaultdict
from pyglet.window import key
import pyglet
import random
from pygame import mixer
from pyglet.image import Animation, ImageGrid, load

class Actor(cocos.sprite.Sprite):
    def __init__(self, image, x, y):
        super(Actor, self).__init__(image)
        self.position = eu.Vector2(x, y)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

    def move(self, offset):
        self.position += offset
        self.cshape.center += offset

    def update(self, elapsed):
        pass

    def collide(self, other):
        pass


class Astronaut(cocos.sprite.Sprite):
    KEYS_PRESSED = defaultdict(int)

    def __init__(self, image, x, y, collision_handler):
        super(Astronaut, self).__init__(image, position=(x, y), scale=0.5, rotation=0)
        self.speed = eu.Vector2(0,0)
        #self.speed2 = eu.Vector2(0, 200)
        self.gravity = 0.75
        self.fps = 100
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5, self.height*0.5)  #png 각 사진 사이에 빈 공간 너무 많아서 직접 픽셀 사진에서 편집헤서 얼만지 계산 후 대입한 값
        self.collide_map = collision_handler
        self.schedule(self.update)
        
        
        
    def update(self, elapsed):
        pressed = Astronaut.KEYS_PRESSED
        space_pressed = pressed[key.SPACE] == 1
        left = 0; right = 0
        if pressed[key.LEFT]:
            self.rotation = -30
        if pressed[key.RIGHT]:
            self.rotation = 30
        if pressed[key.RIGHT] != 1 and pressed[key.LEFT] != 1:
            self.rotation = 0

        vel_y = 50
        vel_x = (pressed[key.RIGHT] - pressed[key.LEFT]) * 300
        if pressed[key.UP] or pressed[key.DOWN]:
            vel_y = (pressed[key.UP] - pressed[key.DOWN]) * 300
        #print(vel_y)

        dx = vel_x * elapsed
        dy = vel_y * elapsed

        
        last = self.get_rect()
        last.center = self.position

        new = last.copy()
        new.x += dx
        new.y += dy
        
        self.speed = self.collide_map(last, new, vel_x, vel_y)
        #print(new.center)
        self.position = new.center
        self.cshape.center = new.center
        scroller.set_focus(new.center[0], new.center[1])
        #print(new.center)

    def move(self, offset):
        self.position += offset
        self.cshape.center += offset
        
class Alien(cocos.sprite.Sprite):

    def __init__(self, alien_list):
        super(Alien, self).__init__(image=alien_list[0], scale = alien_list[3])
        self.position = eu.Vector2(alien_list[1]+self.width*0.5, alien_list[2]+self.height*0.5)
        self.start_position = self.position
        self.limit = eu.Vector2(alien_list[4]+self.width*0.5, alien_list[5]+self.height*0.5)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)
        self.speed = eu.Vector2(10, 0)
        self.direction = 1
        self.schedule(self.update)

    def update(self, elapsed):
        offset = self.direction * self.speed
        if (self.position + offset)[0] <= (self.start_position)[0]:
            self.direction *= -1
        elif (self.position + offset)[0] >= (self.limit).x:
            self.direction *= -1
        else:
            self.position += offset
            self.cshape.center = self.position

    def on_exit(self):
        super(Alien, self).on_exit()
        return Coin(self.position)
        
class Coin(cocos.sprite.Sprite):
    def __init__(self, position):
        super(Coin, self).__init__(image='image/coin.png', position=position)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

class Bullet(cocos.sprite.Sprite):
    def __init__(self, image, x, y, start_position):
        super(Bullet, self).__init__(image=image, scale = 1)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)
        self.position = (start_position[0]+self.width*0.5, start_position[1]+self.height*0.5)
        #self.start_position = eu.Vector2(start_position_x, start_position_y)
        #self.speed = eu.Vector2(20,20)
        self.schedule(self.update)
        if start_position[0] < 450:
            self.new_x = x
        elif start_position[0] >= 450 and start_position[0] <= 2750:
            self.new_x = start_position[0] - 450 + x
        else:
            self.new_x = start_position[0] -(900-(3200-start_position[0])) + x

        
        #self.x = x; self.y = y
        #self.direction = (self.start_position.x-self.x)//(self.start_position.y-self.y)
        self.move(y)

    def update(self, dt):
        '''print("start", self.start_position)
        offset = self.speed * self.direction
        self.position += offset'''
        self.cshape.center = self.position
        #print(self.position)

    def move(self, y):
        print(self.new_x, y)
        self.do(ac.MoveTo((self.new_x, y), 1) + ac.Delay(0.5) + ac.CallFunc(self.kill))

class GameLayer(cocos.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self, hud, w, h):
        super(GameLayer, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.hud = hud
        self.get_background()
        self.px_width = self.bg.px_width
        self.px_height = self.bg.px_height
        mixer.init()
        self.coin_sound = mixer.Sound('hit2.wav')
        self.width = w
        self.height = h
        self.coll_manager = cm.CollisionManagerBruteForce()
        self.is_bullet = 0
        self.is_coin = 0
        self.coin_group = []
        self.score = 0
        self.level = 1
        self.lives = 3
        
        self.create_player()
        self.create_alien()
        self.update_score()
        self.update_level()
        self.schedule(self.update)
        # self.add(GameLayer.Scroller)

    def update_score(self, score=0):
        self.score += score
        self.hud.update_score(self.score)

    def update_level(self):
        self.level += 1
        self.hud.update_level(self.level)

    def respawn_player(self):
        self.lives -= 1
        if self.lives < 0:
            print("Game Over")
            '''self.unschedule(self.update)
            self.hud.show_game_over_lose(self.level)
            pyglet.clock.schedule_once(self.add_new_scene, 3)'''

        else:
            self.create_player()

    def on_key_press(self, k, _):
        Astronaut.KEYS_PRESSED[k] = 1

    def on_key_release(self, k, _):
        Astronaut.KEYS_PRESSED[k] = 0

    def on_mouse_press(self, x, y, buttons, mod):
        self.bullet = Bullet(self.bullet_img, x, y, self.player.position)
        self.add(self.bullet)
        self.is_bullet = 1
        print("PLAYER: ", self.player.position)

    def get_background(self):
        self.tmx_map = cocos.tiles.load('level_1_space_map.tmx')
        self.bg = self.tmx_map['Level1']
        self.colliders = self.tmx_map['Colliders']
        self.bg.set_view(0, 0, self.bg.px_width, self.bg.px_height)
        self.add(self.bg)
        #self.add(self.colliders)
        #self.add(self.colliders)

        #return bg

    def create_player(self):
        mapcollider = mapcolliders.TmxObjectMapCollider()
        mapcollider.on_bump_handler = mapcollider.on_bump_bounce
        collision_handler = mapcolliders.make_collision_handler(mapcollider, self.colliders)

        animation_image = pyglet.image.load('image/character_idle.png')
        image_grid = pyglet.image.ImageGrid(animation_image, 1, 21, item_width=126, item_height=180)
        anim = pyglet.image.Animation.from_image_sequence(image_grid[0:], 0.1, loop=True)
        
        self.player = Astronaut(anim, 960*0.5, 100, collision_handler)
        self.add(self.player)
        self.hud.update_lives(self.lives)

    def create_alien(self):
        alien_list = [['Alien1.png', 32, 416, 0.05, 160, 416], ['ufo.png', 672, 448, 1, 896, 448]]
        self.alien_group = []
        for i, alien in enumerate(alien_list):
            self.alien_group.append(Alien(alien))
            self.add(self.alien_group[i])                

    def update(self, dt):
        for alien in self.alien_group:
            if self.coll_manager.they_collide(self.player, alien):
                print("COLLIDE")
                self.player.kill()
                self.create_player()
            if self.is_bullet == 1 and self.coll_manager.they_collide(self.bullet, alien):
                print("SHOT")
                self.coin = alien.on_exit()
                self.add(self.coin)
                self.coin_group.append(self.coin)
                self.is_coin = 1
                alien.kill()
                self.alien_group.remove(alien)

        for coin in self.coin_group:
            if self.is_coin == 1 and self.coll_manager.they_collide(self.player, coin):
                print("COIN")
                coin.kill()
                self.coin_sound.play()
                self.coin_group.remove(coin)

class HUD(cocos.layer.Layer):
    RESTART_MENU = None
    IS_OVER = 1

    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18)
        self.score_text.position = (20, h - 40)
        self.lives_text = cocos.text.Label('', font_size=18)
        self.lives_text.position = (w - 100, h - 40)
        self.level_text = cocos.text.Label('', font_size=18)
        self.level_text.position = (20, h - 65)
        self.level = 0
        self.add(self.score_text)
        self.add(self.lives_text)
        self.add(self.level_text)

    def update_score(self, score):
        self.score_text.element.text = 'Score: %s' % score

    def update_lives(self, lives):
        self.lives_text.element.text = 'Lives: %s' % lives

    def update_level(self, level):
        self.level_text.element.text = 'Level: %s' % level

    '''def show_game_over_lose(self, level):
        HUD.IS_OVER = 0
        self.level = level
        w, h = cocos.director.director.get_window_size()
        self.game_over = cocos.text.Label('Game Over', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        self.game_over.position = w * 0.5, h * 0.5
        self.add(self.game_over)
        GameLayer.ALIEN_CNT = 0
        pyglet.clock.schedule_once(self.delete_text, 3)

    def show_game_over_win(self, level):
        HUD.IS_OVER = 0
        self.level = level
        w, h = cocos.director.director.get_window_size()
        self.game_over = cocos.text.Label('You Win!', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        self.game_over.position = w * 0.5, h * 0.5
        self.add(self.game_over)
        GameLayer.ALIEN_CNT = 0
        pyglet.clock.schedule_once(self.delete_text, 3)
        
    
    def show_next_level(self, level, score, lives):
        HUD.IS_OVER = 1
        self.level = level
        self.score = score
        self.lives = lives
        w, h = w, h = cocos.director.director.get_window_size()
        self.next_level = cocos.text.Label('Next Level', font_size=50,
                                     anchor_x='center',
                                     anchor_y='center')
        self.next_level.position = w * 0.5, h * 0.5
        self.add(self.next_level)
        GameLayer.ALIEN_CNT = 0
        pyglet.clock.schedule_once(self.delete_text, 3)

    def delete_text(self, dt):  #무조건 dt를 파라미터로 전달 받는다. 스케쥴 once를 사용하면, 그래서 dt를 받도록 설정함.
        if HUD.IS_OVER == 1:
            self.remove(self.next_level)
        else:
            self.remove(self.game_over)'''


if __name__ == '__main__':
    cocos.director.director.init(caption='Game',
                                 width=900, height=640)
    main_scene = cocos.scene.Scene()
    scroller = cocos.layer.ScrollingManager()
    hud_layer = HUD()
    gamelayer = GameLayer(hud_layer, 900, 640)
    scroller.add(gamelayer)
    main_scene.add(scroller, z = 0)
    main_scene.add(hud_layer, z = 1)
    #level_1 = GameLayer(hud_layer, 0, 0, 480)
    #main_scene.add(level_1, z=0)
    cocos.director.director.run(main_scene)
#외계인 사라지면 점수 올라가게, 키 모으면 다음 레벨 이동
#key num + door collision
#alien 배치 level 1 완료
#HUD, MENU(시작, 레벨 선택,,?), 종료화면, 레벨 전환 화면
#공격 색 다르게, space로 전환
#bullet 속도 조절