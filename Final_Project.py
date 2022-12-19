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
from pyglet import image
from pyglet.image import Animation, ImageGrid, load
from cocos.menu import *
import pyglet.app

class MainMenu(Menu):
    def __init__(self):
        super(MainMenu, self).__init__('Menu')
        self.font_title['font_name'] = 'Arial Black'
        self.font_title['font_size'] = 60
        self.font_title['bold'] = True
        self.font_item['font_name'] = 'Arial Black'
        self.font_item_selected['font_name'] = 'Arial Black'
        m1 = MenuItem('Start', self.start_game)
        m2 = MenuItem('How To Play', self.show_tutorial)
        m3 = MenuItem('Quit', pyglet.app.exit)
        self.create_menu([m1, m2, m3], shake(), shake_back())

    def start_game(self):
        main_scene.add(scroller, z = 0)
        main_scene.add(hud_layer, z = 1)
        main_scene.remove(menu)

    def show_tutorial(self):
        pic = image.load('image/Objects/tutorial.png')
        print(pic.width)
        print("ff")

class Restart(Menu):
    def __init__(self, win):
        if win == 0:
            self.a = 'Game Over'
        else:
            self.a = 'Game Clear'
        super(Restart, self).__init__(self.a)
        self.font_title['font_name'] = 'Arial Black'
        self.font_title['font_size'] = 60
        self.font_title['bold'] = True
        self.font_item['font_name'] = 'Arial Black'
        self.font_item_selected['font_name'] = 'Arial Black'
        m1 = MenuItem('Restart', self.start_game)
        m2 = MenuItem('Quit', pyglet.app.exit)
        self.create_menu([m1, m2], shake(), shake_back())

    def start_game(self):
        level_1 = GameLayer(hud_layer, 900, 640, 1, 480, 150, 0)
        scroller.add(level_1)
        main_scene.remove(self)

class Astronaut(cocos.sprite.Sprite):
    KEYS_PRESSED = defaultdict(int)
    JUMP = False

    def __init__(self, idle, run_L, run_R, jump_L, jump_R, x, y, collision_handler, level):
        super(Astronaut, self).__init__(idle, position=(x, y), scale=0.35, rotation=0) 
        self.speed = eu.Vector2(0,0)
        #self.speed2 = eu.Vector2(0, 200)
        self.gravity = 0.75
        self.fps = 100
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5, self.height*0.5)  #png 각 사진 사이에 빈 공간 너무 많아서 직접 픽셀 사진에서 편집헤서 얼만지 계산 후 대입한 값
        self.collide_map = collision_handler
        self.level = level
        self.jump_count = 0
        self.schedule(self.update)
        self.idle = idle
        self.run_L = run_L
        self.run_R = run_R
        self.jump_L = jump_L
        self.jump_R = jump_R

    def update_animation(self, animation):
        if animation == 'idle':
            self.image = self.idle
        elif animation == 'run_R':
            self.image = self.run_R
        elif animation == 'run_L':
            self.image = self.run_L
        elif animation == 'jump_L':
            self.image = self.jump_L
        else:
            self.image = self.jump_R
        
    def update(self, elapsed):
        pressed = Astronaut.KEYS_PRESSED
        space_pressed = pressed[key.SPACE] == 1
        left = 0; right = 0
        '''if pressed[key.LEFT]:
            self.rotation = -30
        if pressed[key.RIGHT]:
            self.rotation = 30
        if pressed[key.RIGHT] != 1 and pressed[key.LEFT] != 1:
            self.rotation = 0'''

        
        vel_x = (pressed[key.RIGHT] - pressed[key.LEFT]) * 300

        if self.level == 1:
            vel_y = 50    
            if pressed[key.UP] or pressed[key.DOWN]:
                vel_y = (pressed[key.UP] - pressed[key.DOWN]) * 300
        else:
            vel_y = 50    
            if pressed[key.UP] or pressed[key.DOWN]:
                vel_y = (pressed[key.UP] - pressed[key.DOWN]) * 300
            '''vel_y = -250
            if pressed[key.LEFT] or pressed[key.RIGHT]:
                self.jump_count = 0
            if pressed[key.DOWN]:
                vel_y = (pressed[key.UP] - pressed[key.DOWN]) * 300
            if pressed[key.UP] and Astronaut.JUMP == True:
                vel_y = 1500
                Astronaut.JUMP = False
                self.jump_count += 1'''

        
        

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
        self.tag = alien_list[0]
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
        super(Coin, self).__init__(image='image/Objects/coin.png', position=position)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

class Key(cocos.sprite.Sprite):
    def __init__(self, key_list):
        super(Key, self).__init__(image='image/Objects/key.png', position=(key_list[0], key_list[1]), scale=0.03)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

class Door(cocos.sprite.Sprite):
    def __init__(self, x, y):
        super(Door, self).__init__(image='image/Objects/door.png', position=(x, y))
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)

class Bullet(cocos.sprite.Sprite):
    BULLET_LIST = ['image/Objects/blue_bullet.png', 'image/Objects/red_bullet.png', 'image/Objects/purple_bullet.png']
    BULLET_INDEX = 0
    def __init__(self, x, y, start_position):
        super(Bullet, self).__init__(image=Bullet.BULLET_LIST[Bullet.BULLET_INDEX])
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)
        self.position = (start_position[0]+self.width*0.5, start_position[1]+self.height*0.5)
        self.tag = Bullet.BULLET_INDEX
        self.schedule(self.update)
        if start_position[0] < 450:
            self.new_x = x
        elif start_position[0] >= 450 and start_position[0] <= 2750:
            self.new_x = start_position[0] - 450 + x
        else:
            self.new_x = start_position[0] -(900-(3200-start_position[0])) + x
        self.move(y)

    def update(self, dt):
        self.cshape.center = self.position

    def move(self, y):
        print(self.new_x, y)
        self.do(ac.MoveTo((self.new_x, y), 1) + ac.CallFunc(self.kill))

class Alien_Shoot(cocos.sprite.Sprite):
    def __init__(self, position):
        super(Alien_Shoot, self).__init__(image='image/Objects/white_bullet.png', position=position)
        self.cshape = cm.AARectShape(self.position,
                                     self.width * 0.5,
                                     self.height * 0.5)
        self.speed = eu.Vector2(400, 0)

    def update(self, elapsed):
        self.move(self.speed * elapsed)


    def move(self, offset):
        self.position += offset
        self.cshape.center += offset        

class GameLayer(cocos.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self, hud, w, h, level, pos_x, pos_y, score):
        super(GameLayer, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.hud = hud
        self.level = level
        self.get_background()
        self.px_width = self.bg.px_width
        self.px_height = self.bg.px_height
        self.coin_sound = mixer.Sound('sound/coin.wav')
        self.key_sound = mixer.Sound('sound/key.wav')
        self.alien_hit_sound = mixer.Sound('sound/hit.mp3')
        self.GameOver_sound = mixer.Sound('sound/game_over.wav')
        self.next_level_sound = mixer.Sound('sound/next_level.wav')
        self.shoot_sound = mixer.Sound('sound/shoot.wav')
        self.alien_shoot_sound = mixer.Sound('sound/alien_shoot.wav')
        self.width = w
        self.height = h
        self.coll_manager = cm.CollisionManagerBruteForce()
        self.is_bullet = 0
        self.is_coin = 0
        self.coin_group = []
        self.bullet_list = []
        self.alien_shoot_list = []
        self.score = score
        self.lives = 3
        self.keyN = 0
        self.direction = 0 #jump left, right 판별
        self.create_door()
        self.create_player(pos_x, pos_y)
        self.create_alien()
        self.create_key()
        self.update_score()
        self.update_level()
        self.update_key(self.keyN)
        self.schedule(self.update)
        #pyglet.clock.schedule_interval(self.shoot(), 0.5)

    def shoot(self):
        if len(self.alien_group) > 3:
            for i in range(3):
                self.alien_shoot_list.append(Alien_Shoot(self.alien_group[i].position))
                self.add(self.alien_shoot_list[i])
                
            

    def update_score(self, score=0):
        self.score += score
        self.hud.update_score(self.score)

    def update_key(self, key):
        self.hud.update_key(self.keyN)

    def update_level(self):
        self.hud.update_level(self.level)
    
    def create_door(self):
        if self.level == 1:
            self.door = Door(3136, 366)
        elif self.level == 2:
            self.door = Door(3136, 552)
        else:
            self.door = Door(3136, 265)
        self.add(self.door)

    def respawn_player(self):
        self.lives -= 1
        if self.lives < 0:
            print("Game Over")
            self.unschedule(self.update)
            BGM.stop()
            self.GameOver_sound.play()
            scroller.remove(self)
            main_scene.add(restart_menu_lose)
        else:
            self.create_player(self.player.position[0]-200, self.player.position[1])
            

    def on_key_press(self, k, _):
        Astronaut.KEYS_PRESSED[k] = 1
        if Astronaut.KEYS_PRESSED[key.SPACE]:
            if Bullet.BULLET_INDEX == 2:
                Bullet.BULLET_INDEX = 0
            else:
                Bullet.BULLET_INDEX += 1
        
        if Astronaut.KEYS_PRESSED[key.UP]:
            Astronaut.JUMP = True


    def on_key_press(self, k, _):
        pressed = Astronaut.KEYS_PRESSED
        pressed[k] = 1
        if pressed[key.SPACE]:
            if Bullet.BULLET_INDEX == 2:
                Bullet.BULLET_INDEX = 0
            else:
                Bullet.BULLET_INDEX += 1
        if pressed[key.LEFT]:
            self.player.update_animation('run_L')
            self.direction = 1
        
        if pressed[key.RIGHT]:
            self.player.update_animation('run_R')
            self.direction = 0
        
        if pressed[key.UP]:
            Astronaut.JUMP = True
            if self.direction == 1:
                self.player.update_animation('jump_L')
            else:
                self.player.update_animation('jump_R')


    def on_key_release(self, k, _):
        Astronaut.KEYS_PRESSED[k] = 0
        self.player.update_animation('idle')

    def on_mouse_press(self, x, y, buttons, mod):
        self.bullet = Bullet(x, y, self.player.position)
        self.add(self.bullet)
        self.bullet_list.append(self.bullet)
        self.is_bullet = 1
        self.shoot_sound.play()

    def get_background(self):
        if self.level == 1:
            self.tmx_map = cocos.tiles.load('map/level_1_space_map.tmx')
            self.bg = self.tmx_map['Level1']
        elif self.level == 2:
            self.tmx_map = cocos.tiles.load('map/level_2_sky_map.tmx')
            self.bg = self.tmx_map['Level2']
        else:
            self.tmx_map = cocos.tiles.load('map/level_3_grass_map.tmx')
            self.bg = self.tmx_map['Level3']
        self.colliders = self.tmx_map['Colliders']
        self.bg.set_view(0, 0, self.bg.px_width, self.bg.px_height)
        self.add(self.bg)

    def create_player(self, player_x, player_y):
        mapcollider = mapcolliders.TmxObjectMapCollider()
        mapcollider.on_bump_handler = mapcollider.on_bump_slide
        collision_handler = mapcolliders.make_collision_handler(mapcollider, self.colliders)

        animation_image = pyglet.image.load('image/Objects/character_idle.png')
        image_grid = pyglet.image.ImageGrid(animation_image, 1, 21, item_width=126, item_height=180)
        idle = pyglet.image.Animation.from_image_sequence(image_grid[0:], 0.1, loop=True)

        animation_image = pyglet.image.load('image/Objects/character_run_L.png')
        image_grid = pyglet.image.ImageGrid(animation_image, 1, 10, item_width=148, item_height=180)
        run_L = pyglet.image.Animation.from_image_sequence(image_grid[0:], 0.1, loop=True)

        animation_image = pyglet.image.load('image/Objects/character_run_R.png')
        image_grid = pyglet.image.ImageGrid(animation_image, 1, 10, item_width=148, item_height=180)
        run_R = pyglet.image.Animation.from_image_sequence(image_grid[::-1], 0.1, loop=True)

        animation_image = pyglet.image.load('image/Objects/character_jump_L.png')
        image_grid = pyglet.image.ImageGrid(animation_image, 1, 11, item_width=146, item_height=180)
        jump_L = pyglet.image.Animation.from_image_sequence(image_grid[0:], 0.1, loop=True)

        animation_image = pyglet.image.load('image/Objects/character_jump_R.png')
        image_grid = pyglet.image.ImageGrid(animation_image, 1, 11, item_width=146, item_height=180)
        jump_R = pyglet.image.Animation.from_image_sequence(image_grid[::-1], 0.1, loop=True)

        self.player = Astronaut(idle, run_L, run_R, jump_L, jump_R, player_x, player_y, collision_handler, self.level)
        self.add(self.player)
        self.hud.update_lives(self.lives)

    def create_alien(self):
        self.ufo = 'image/Objects/ufo.png'
        self.red_alien = 'image/Objects/alien_red.png'
        self.green_alien = 'image/Objects/alien_green.png'
        self.purple_alien = 'image/Objects/alien_purple.png'
        if self.level == 1: 
            alien_list = [[self.purple_alien, 32, 416, 0.05, 160, 416], [self.red_alien, 672, 448, 1, 896, 448],\
            [self.purple_alien, 768, 224, 0.05, 896, 224], [self.ufo, 992, 512, 1, 1120, 512],\
            [self.ufo, 1088, 320, 1, 1248, 320], [self.purple_alien, 1184, 128, 0.05, 1344, 128],\
            [self.purple_alien, 1664, 224, 0.05, 1760, 224], [self.purple_alien, 2080, 160, 0.05, 2304, 160],\
            [self.purple_alien, 2016, 448, 0.05, 2208, 448], [self.purple_alien, 2496, 320, 0.05, 2848, 320],\
            [self.purple_alien, 3040, 320, 0.05, 3104, 320], [self.purple_alien, 2496, 96, 0.05, 2592, 96]]
        elif self.level == 2:
            alien_list = [[self.purple_alien, 32, 32, 0.05, 448, 32], [self.ufo, 448, 32, 1, 768, 32],
            [self.purple_alien, 1120, 192, 0.05, 1280, 192], [self.purple_alien, 1344, 288, 0.05, 1536, 288],
            [self.purple_alien, 1856, 96, 0.05, 2048, 96], [self.purple_alien, 2112, 192, 0.05, 2272, 192],
            [self.purple_alien, 1568, 32, 0.05, 1824, 32], [self.purple_alien, 2080, 32, 0.05, 2464, 32], 
            [self.purple_alien, 2658, 32, 0.05, 3136, 32], [self.purple_alien, 2752, 320, 0.05, 2880, 320]]
        else:
            alien_list = [[self.purple_alien, 32, 448, 0.05, 416, 448], [self.ufo, 32, 224, 1, 96, 224],
            [self.purple_alien, 256, 224, 0.05, 736, 224], [self.purple_alien, 576, 448, 0.05, 928, 448],
            [self.purple_alien, 928, 448, 0.05, 1312, 448], [self.purple_alien, 960, 224, 0.05, 1152, 224],
            [self.purple_alien, 1312, 224, 0.05, 1888, 224], [self.purple_alien, 2144, 224, 0.05, 2304, 224],
            [self.purple_alien, 2656, 224, 0.05, 2944, 224], [self.purple_alien, 3072, 224, 0.05, 3136, 224],
            [self.purple_alien, 1504, 448, 0.05, 1632, 448], [self.purple_alien, 1760, 448, 0.05, 2048, 448],
            [self.purple_alien, 2208, 448, 0.05, 2496, 448], [self.purple_alien, 2720, 448, 0.05, 3008, 448]]
        self.alien_group = []
        for i, alien in enumerate(alien_list):
            self.alien_group.append(Alien(alien))
            self.add(self.alien_group[i])
    
    def create_key(self):
        if self.level == 1:
            key_list = [[1472, 458], [1696, 234], [2560, 106]]
        elif self.level == 2:
            key_list = [[1472, 458], [1472, 458], [1472, 458]]
        else:
            key_list = [[1472, 458], [1472, 458], [1472, 458]]
        self.key_list = []
        for i, key in enumerate(key_list):
            self.key_list.append(Key(key))
            self.add(self.key_list[i])


    def update(self, dt):
        for alien in self.alien_group:            
            if self.coll_manager.they_collide(self.player, alien):
                print("COLLIDE")
                self.player.kill()
                self.respawn_player()

            for bullet in self.bullet_list:
                if len(self.bullet_list) >= 1 and self.coll_manager.they_collide(bullet, alien):
                    print("SHOT")
                    if (alien.tag == 'image/Objects/alien_red.png' and bullet.tag == 1) or (alien.tag == 'image/Objects/alien_purple.png' and bullet.tag == 2):
                        self.coin = alien.on_exit()
                        self.add(self.coin)
                        self.coin_group.append(self.coin)
                        self.is_coin = 1
                        alien.kill()
                        self.alien_group.remove(alien)
                        self.bullet_list.remove(bullet)
                        self.update_score(20)
                        self.alien_hit_sound.play()
                    else:
                        self.bullet_list.remove(bullet)

        for coin in self.coin_group:
            if self.is_coin == 1 and self.coll_manager.they_collide(self.player, coin):
                print("COIN")
                coin.kill()
                self.coin_sound.play()
                self.coin_group.remove(coin)
                self.update_score(10)

        for key in self.key_list:
            if self.coll_manager.they_collide(self.player, key):
                key.kill()
                self.key_sound.play()
                self.key_list.remove(key)
                self.keyN += 1
                self.update_key(self.keyN)
        
        if self.coll_manager.they_collide(self.player, self.door) and self.keyN == 3:
            self.next_level_sound.play()
            self.add_new_scene()

    def add_new_scene(self):
        print(self.level)
        if self.level == 1:
            scroller.remove(self)
            level_2 = GameLayer(hud_layer, 900, 640, 2, 150, 150, self.score)
            scroller.add(level_2) 
            #level_1.stop()
        elif self.level == 2:
            scroller.remove(self)
            level_3 = GameLayer(hud_layer, 900, 640, 3, 150, 150, self.score)
            scroller.add(level_3)
        else:
            scroller.remove(self)
            main_scene.add(restart_menu_win)


class HUD(cocos.layer.Layer):
    RESTART_MENU = None
    IS_OVER = 1

    def __init__(self):
        super(HUD, self).__init__()
        w, h = cocos.director.director.get_window_size()
        self.score_text = cocos.text.Label('', font_size=18)
        self.score_text.position = (20, h - 80)
        #self.key_text = cocos.text.Label('', font_size=18)
        #self.key_text.position = (20, 40)
        #self.lives_text = cocos.text.Label('', font_size=18)
        #self.lives_text.position = (w - 100, h - 40)
        self.level_text = cocos.text.Label('', font_size=18)
        self.level_text.position = (20, h - 55)
        self.add(self.score_text)
        #self.add(self.lives_text)
        self.add(self.level_text)
        #self.add(self.key_text)

    def update_score(self, score):
        self.score_text.element.text = 'Score: %s' % score

    def update_key(self, key):
        #self.key_text.element.text = 'Key: %s/3' % key
        self.key_1 = cocos.sprite.Sprite('image/Objects/key.png', scale=0.023, position=(20, 49), rotation=-90)
        self.key_2 = cocos.sprite.Sprite('image/Objects/key.png', scale=0.023, position=(40, 49), rotation=-90)
        self.key_3 = cocos.sprite.Sprite('image/Objects/key.png', scale=0.023, position=(60, 49), rotation=-90)
        self.key_blanck_1 = cocos.sprite.Sprite('image/Objects/key_blanck.png', scale=0.023, position=(20, 49), rotation=-90)
        self.key_blanck_2 = cocos.sprite.Sprite('image/Objects/key_blanck.png', scale=0.023, position=(40, 49), rotation=-90)
        self.key_blanck_3 = cocos.sprite.Sprite('image/Objects/key_blanck.png', scale=0.023, position=(60, 49), rotation=-90)
        
        if key == 0:
            self.add(self.key_blanck_1); self.add(self.key_blanck_2); self.add(self.key_blanck_3)
        elif key == 1:
            self.add(self.key_1)
        elif key == 2:
            self.add(self.key_2)
        else:
            self.add(self.key_3)

    def update_lives(self, lives):
        #self.lives_text.element.text = 'Lives: %s' % lives
        self.lives_1 = cocos.sprite.Sprite('image/Objects/full_heart.png', scale=0.015, position=(820, 590))
        self.lives_2 = cocos.sprite.Sprite('image/Objects/full_heart.png', scale=0.015, position=(850, 590))
        self.lives_3 = cocos.sprite.Sprite('image/Objects/full_heart.png', scale=0.015, position=(880, 590))
        self.lives_blank_1 = cocos.sprite.Sprite('image/Objects/empty_heart.png', scale=0.015, position=(880, 590))
        self.lives_blank_2 = cocos.sprite.Sprite('image/Objects/empty_heart.png', scale=0.015, position=(850, 590))
        self.lives_blank_3 = cocos.sprite.Sprite('image/Objects/empty_heart.png', scale=0.015, position=(820, 590))
        
        if lives == 3:
            self.add(self.lives_1); self.add(self.lives_2); self.add(self.lives_3)
        elif lives == 2:
            self.add(self.lives_blank_1)
        elif lives == 1:
            self.add(self.lives_blank_2)
        else:
            self.add(self.lives_blank_3)

    def update_level(self, level):
        self.level_text.element.text = 'Level: %s' % level



if __name__ == '__main__':
    mixer.init()
    cocos.director.director.init(caption='Game',
                                 width=900, height=640)
    scroller = cocos.layer.ScrollingManager()
    main_scene = cocos.scene.Scene()
    menu = MainMenu()
    restart_menu_lose = Restart(0)
    restart_menu_win = Restart(1)    
    hud_layer = HUD()
    level_1 = GameLayer(hud_layer, 900, 640, 1, 480, 150, 0)
    scroller.add(level_1)
    main_scene.add(menu)
    
    BGM = mixer.Sound('sound/bgm.wav')
    BGM.play(-1)
    cocos.director.director.run(main_scene)

#레벨 전환 화면
#alien 공격 - 레벨 2에서 몇 개만, 레벨 3는 player 좌표값으로 move로 구현
#key 배치
#점프 조정
