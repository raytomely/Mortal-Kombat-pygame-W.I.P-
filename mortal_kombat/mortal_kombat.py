import pygame,sys,random
from pygame.locals import *


BLACK=pygame.color.THECOLORS["black"]
WHITE=pygame.color.THECOLORS["white"]
RED=pygame.color.THECOLORS["red"]
GREEN=pygame.color.THECOLORS["green"]
BLUE=pygame.color.THECOLORS["blue"]
YELLOW=pygame.color.THECOLORS["yellow"]
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_SIZE = (640, 480)
DISPLAY_SURFACE_WIDTH = 320
DISPLAY_SURFACE_HEIGHT = 240
DISPLAY_SURFACE_SIZE = (320, 240)
CENTER_X = int(320/2)


def load_sprite_data(sprite_file):
    sprites = {'rect':[], 'axis_shift':[], 'offense_box':[], 'defense_box':[]}
    with open(sprite_file, 'r') as file:
         data=file.read()
         data=data.split(';')
         del(data[-1])
         for i in range(len(data)):
             data[i] = data[i].split(",")
             for j in range(len(data[i])):
                 data[i][j] = data[i][j].split(" ")
                 for k in range(len(data[i][j])):
                     data[i][j][k] = int(data[i][j][k])
             sprites['rect'].append(data[i][0])
             sprites['axis_shift'].append(data[i][1])
             sprites['offense_box'].append(data[i][2])
             sprites['defense_box'].append(data[i][3])
    return sprites

def load_animation_data(animation_file):
    animations = None
    with open(animation_file, 'r') as file:
         data=file.read()
         data=data.split(',')
         del(data[-1])
         for i in range(len(data)):
             data[i] = data[i].split(" ")
             if data[i][0] == "-1":
                del(data[i][0])
             else:
                data[i].append(-1)
             for j in range(len(data[i])):
                 data[i][j] = int(data[i][j])
         animations = data
    return animations


class Character():
    def __init__(self, image, sprite_file, animation_file, axis_pos, direction=1):
        self.left_side_sprites = self.get_sprites(image, sprite_file)
        self.right_side_sprites = self.get_right_side_sprites(self.left_side_sprites)
        self.sprites = self.left_side_sprites
        self.animations = self.get_animations(animation_file)
        self.axis_pos = axis_pos
        self.current_animation = self.animations['stand']
        self.animation_frame = 0
        self.max_anim_time = 1
        self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
        self.image = self.current_sprite['image']
        self.image_pos=[
        self.axis_pos[0] + self.current_sprite['axis_shift'][0],
        self.axis_pos[1] + self.current_sprite['axis_shift'][1]]
        self.anim_time = 0
        self.direction = direction
        self.controls_mapping(direction)
        self.opponent = None
        self.attack_type = None
        self.hit_connect = False
        self.up = False
        self.down = False
        self.forward = False
        self.backward = False
        self.punch1 = False
        self.punch2 = False
        self.kick1 = False
        self.kick2 = False        
        self.timer = 0
        self.xvel = 0
        self.yvel = 0
        self.walk_speed = 3
        self.jump_speed = 13
        self.gravity = 1.3
        self.hit_freeze_time = 0
        self.health = 120
        self.current_state = 'stand'
        self.states = {'stand':self.stand, 'walk':self.walk, 'jump_start':self.jump_start, 'jump':self.jump,
                       'stand_to_crouch':self.stand_to_crouch, 'crouch':self.crouch,
                       'attack':self.attack, 'crouch_attack':self.crouch_attack, 'air_attack':self.air_attack}

    def get_sprites(self, image, player_sprite_file):
        sprites = []
        sprites_data = load_sprite_data(player_sprite_file)
        for i in range(len(sprites_data['rect'])):
            sprites.append({'image':image.subsurface(sprites_data['rect'][i]),
                            'axis_shift':sprites_data['axis_shift'][i],
                            'offense_box':sprites_data['offense_box'][i],
                            'defense_box':sprites_data['defense_box'][i]})
        return sprites
                            
    def get_animations(self, player_animation_file):
        animations = {}
        animations_data = load_animation_data(player_animation_file)
        animations['stand'] = animations_data[0]
        animations['walk_forward'] = animations_data[1]
        animations['walk_backward'] = animations_data[2]
        animations['jump_start'] = animations_data[11]
        animations['jump_up'] = animations_data[7]
        animations['jump_forward'] = animations_data[9]
        animations['jump_backward'] = animations_data[10]
        animations['land'] = animations_data[8]
        animations['stand_to_crouch'] = animations_data[4]
        animations['crouch_to_stand'] = animations_data[5]
        animations['crouch'] = animations_data[6]
        animations['low_punch1'] = animations_data[12]
        animations['low_punch2'] = animations_data[13]
        animations['high_punch1'] = animations_data[14]
        animations['high_punch2'] = animations_data[15]
        animations['low_kick1'] = animations_data[16]
        animations['low_kick2'] = animations_data[17]
        animations['high_kick1'] = animations_data[18]
        animations['high_kick2'] = animations_data[19]
        animations['close_punch'] = animations_data[20]
        animations['close_kick'] = animations_data[21]
        animations['crouch_punch'] = animations_data[22]
        animations['crouch_kick'] = animations_data[23]
        animations['jump_punch1'] = animations_data[24]
        animations['jump_punch2'] = animations_data[25]        
        return animations
                            
    def get_right_side_sprites(self, sprites):
        right_side_sprites=[]
        for sprite in sprites:
            image_width, image_height = sprite['image'].get_size()             
            right_side_sprite={
            'image':pygame.transform.flip(sprite['image'], True, False),    
            'axis_shift':[-(image_width + sprite['axis_shift'][0]), sprite['axis_shift'][1]],
            'offense_box':sprite['offense_box'],
            'defense_box':sprite['defense_box']}
            if sprite['offense_box'] != [0,0,0,0]:
               offense_box = sprite['offense_box']
               right_side_offense_box = [image_width - (offense_box[0] + offense_box[2]),
                                        offense_box[1], offense_box[2], offense_box[3]]
               right_side_sprite['offense_box'] = right_side_offense_box
            if sprite['defense_box'] != [0,0,0,0]:
               defense_box = sprite['defense_box']
               right_side_defense_box = [image_width - (defense_box[0] + defense_box[2]),
                                        defense_box[1], defense_box[2], defense_box[3]]
               right_side_sprite['defense_box'] = right_side_defense_box
            right_side_sprites.append(right_side_sprite)            
        return right_side_sprites
    
    def update_animation(self):
        self.anim_time += 1
        if self.anim_time  >= self.max_anim_time:
           self.anim_time = 0
           self.animation_frame += 1
           if self.current_animation[self.animation_frame] == -1:
              self.animation_frame = 0
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
           self.image = self.current_sprite['image']
           
    def change_animation(self, animation):
        self.current_animation = self.animations[animation]
        self.anim_time = 0
        self.animation_frame = 0
        self.current_sprite = self.sprites[self.current_animation[self.animation_frame]]
        self.image = self.current_sprite['image']
        
    def end_of_animation(self):
        return self.animation_frame == 0 and self.anim_time == 0
                           
    def scroll_background(self):
        global right_pit, left_pit
        if self.timer < 128:
           self.timer += 1
           self.update_animation()
           if self.anim_time > 0:
              self.anim_time = self.max_anim_time 
           dx = -2 * self.direction
           #if self.timer == 66:
              #self.change_animation('stand')
           #elif self.timer > 66:
              #self.axis_pos[0] += dx
           x_offset = background_pos[0] % (256 * self.direction)
           if x_offset != 0:
              if (self.axis_pos[0] - (self.x_boundary + x_offset)) * self.direction > 10:
                 self.change_animation('stand')
                 self.axis_pos[0] += dx
           background_pos[0] += dx
           self.opponent.axis_pos[0] += dx
           if right_pit:
              right_pit_pos[0] += dx
              right_pit_old_pos[0] += dx
           if left_pit:
              left_pit_pos[0] += dx
              left_pit_old_pos[0] += dx
           game_event.scroll(dx)
        else: 
           self.timer = 0
           self.rounds += 1
           self.current_state = 'stand'
           self.reset_buttons()
           self.stamina = 200
           self.opponent.stamina = 200
           self.opponent.reset_buttons()
           self.opponent.current_state = 'stand'
           if right_pit:
              right_pit_old_pos[0] = right_pit_pos[0]
           if left_pit:
              left_pit_old_pos[0] = left_pit_pos[0]
           global time, timer
           time= 99
           timer = 0
           game_event.clear()

    def controls_mapping(self, direction):
        if direction == 1:
           self.FORWARD = K_RIGHT
           self.BACKWARD = K_LEFT
           self.UP = K_UP
           self.DOWN = K_DOWN
           self.PUNCH1 = K_o
           self.PUNCH2 = K_p
           self.KICK1 = K_k
           self.KICK2 = K_l
        elif direction == -1:
           self.FORWARD = K_a
           self.BACKWARD = K_d
           self.UP = K_w
           self.DOWN = K_s
           self.PUNCH1 = K_r
           self.PUNCH2 = K_t
           self.KICK1 = K_f
           self.KICK2 = K_g
           
    def handle_controls(self, event):
        if event.type == KEYDOWN:
           if event.key == self.FORWARD:
              self.forward = True
              self.backward = False
           elif event.key == self.BACKWARD:
              self.backward = True
              self.forward = False
           if event.key == self.UP:
              self.up = True
              self.down = False
           elif event.key == self.DOWN:
              self.down = True
              self.up = False                      
           if event.key == self.PUNCH1:
              self.punch1 = True
           if event.key == self.PUNCH2:
              self.punch2 = True         
           if event.key == self.KICK1:
              self.kick1 = True
           if event.key == self.KICK2:
              self.kick2 = True         
        if event.type == KEYUP:
           if event.key == self.FORWARD:
              self.forward = False
           elif event.key == self.BACKWARD:
              self.backward = False
           if event.key == self.UP:
              self.up = False
           elif event.key == self.DOWN:
              self.down = False

    def stand(self):
        self.update_animation()
        if self.forward:
           self.current_state = 'walk'
           self.change_animation('walk_forward')
           self.xvel = self.walk_speed * self.direction
        elif self.backward:
           self.current_state = 'walk'
           self.change_animation('walk_backward')
           self.xvel = self.walk_speed * -self.direction
        if self.up:
           self.yvel = self.jump_speed
           if self.forward:
              self.current_state = 'jump_start' 
              self.change_animation('jump_start')
              self.xvel = self.walk_speed * self.direction
           elif self.backward:
              self.current_state = 'jump_start' 
              self.change_animation('jump_start')
              self.xvel = self.walk_speed * -self.direction
           else:
              self.current_state = 'jump' 
              self.change_animation('jump_up')
        elif self.down:
           self.current_state = 'stand_to_crouch' 
           self.change_animation('stand_to_crouch')
        if self.punch1:
           self.punch1 = False
           self.current_state = 'attack'
           self.change_animation('low_punch1')
        elif self.punch2:
           self.punch2 = False
           self.current_state = 'attack'
           self.change_animation('high_punch1')
        elif self.kick1:
           self.kick1 = False
           self.current_state = 'attack'
           if self.backward:
              self.change_animation('low_kick2') 
           else:
              self.change_animation('low_kick1')
        elif self.kick2:
           self.kick2 = False
           self.current_state = 'attack'
           if self.backward:
              self.change_animation('high_kick2') 
           else:
              self.change_animation('high_kick1')

    def walk(self):
        self.update_animation()
        self.axis_pos[0] += self.xvel
        if self.axis_pos[0] < 20 or self.axis_pos[0] > 300:
           self.axis_pos[0] -= self.xvel        
        if not (self.backward or self.forward):
           self.current_state = 'stand'
           self.change_animation('stand')
           self.xvel = 0
        if self.up:
           self.yvel = self.jump_speed
           if self.forward:
              self.current_state = 'jump_start' 
              self.change_animation('jump_start')
              self.xvel = self.walk_speed * self.direction
           elif self.backward:
              self.current_state = 'jump_start' 
              self.change_animation('jump_start')
              self.xvel = self.walk_speed * -self.direction
           else:
              self.current_state = 'jump' 
              self.change_animation('jump_up')
        elif self.down:
           self.current_state = 'stand_to_crouch' 
           self.change_animation('stand_to_crouch')
        if self.punch1:
           self.punch1 = False
           self.current_state = 'attack'
           self.change_animation('low_punch1')
        elif self.punch2:
           self.punch2 = False
           self.current_state = 'attack'
           self.change_animation('high_punch1')
        elif self.kick1:
           self.kick1 = False
           self.current_state = 'attack'
           if self.backward:
              self.change_animation('low_kick2') 
           else:
              self.change_animation('low_kick1')
        elif self.kick2:
           self.kick2 = False
           self.current_state = 'attack'
           if self.backward:
              self.change_animation('high_kick2') 
           else:
              self.change_animation('high_kick1')
           
    def jump_start(self):
        self.update_animation()
        if self.yvel > 0:
           self.axis_pos[0] += self.xvel
           self.axis_pos[1] -= self.yvel
           self.yvel -= self.gravity
           if self.axis_pos[0] < 20 or self.axis_pos[0] > 300:
              self.axis_pos[0] -= self.xvel
        if self.end_of_animation():
           if self.yvel > 0:
              self.current_state = 'jump'
              if self.xvel > 0:
                 self.change_animation('jump_forward')
              elif self.xvel < 0:
                 self.change_animation('jump_backward')                 
           else:
              self.current_state = 'stand'
              self.change_animation('stand')

    def jump(self):
        self.update_animation()
        self.axis_pos[0] += self.xvel
        self.axis_pos[1] -= self.yvel
        self.yvel -= self.gravity        
        if self.axis_pos[0] < 20 or self.axis_pos[0] > 300:
           self.axis_pos[0] -= self.xvel
        if self.punch1 or self.punch2:
           self.punch1 = False
           self.punch2 = False
           self.current_state = 'air_attack'
           if self.xvel == 0:
              self.change_animation('jump_punch1')
           else:
              self.change_animation('jump_punch2')
        if self.axis_pos[1] >= ground_y_pos:
           self.axis_pos[1] = ground_y_pos
           self.current_state = 'jump_start'
           if self.xvel != 0:
              self.change_animation('jump_start')
           else:
              self.change_animation('land')
           self.xvel = 0
           self.yvel = 0
           
    def stand_to_crouch(self):
        self.update_animation()
        if self.end_of_animation():
           if self.current_animation == self.animations['stand_to_crouch']:
              self.current_state = 'crouch'
              self.change_animation('crouch')
           else:
              self.current_state = 'stand'
              self.change_animation('stand')              

    def crouch(self):
        self.update_animation()
        if self.punch1 or self.punch2:
           self.punch1 = False
           self.punch2 = False
           self.current_state = 'attack'
           self.change_animation('crouch_punch')
        elif self.kick1 or self.kick2:
           self.kick1 = False
           self.kick2 = False
           self.current_state = 'crouch_attack'
           self.change_animation('crouch_kick')           
        elif not self.down:
           self.current_state = 'stand_to_crouch'
           self.change_animation('crouch_to_stand')

    def attack(self):
        self.update_animation()
        if self.end_of_animation():
           self.current_state = 'stand'
           self.change_animation('stand')
        if self.punch1:
           if self.current_animation == self.animations['low_punch1']:
              if self.animation_frame > 4:
                 self.punch1 = False
                 self.change_animation('low_punch2')
           elif self.current_animation == self.animations['low_punch2']:
              if self.animation_frame > 5:
                 self.punch1 = False
                 self.change_animation('low_punch1')
        if self.punch2:
           if self.current_animation == self.animations['high_punch1']:
              if self.animation_frame > 5:
                 self.punch2 = False
                 self.change_animation('high_punch2')
           elif self.current_animation == self.animations['high_punch2']:
              if self.animation_frame > 5:
                 self.punch2 = False
                 self.change_animation('high_punch1')
                 
    def crouch_attack(self):
        self.update_animation()
        if self.end_of_animation():
           if self.down:
              self.current_state = 'crouch'
              self.change_animation('crouch')              
           elif not self.down:
              self.current_state = 'stand_to_crouch'
              self.change_animation('crouch_to_stand')

    def air_attack(self):
        self.update_animation()
        self.axis_pos[0] += self.xvel
        self.axis_pos[1] -= self.yvel
        self.yvel -= self.gravity
        if self.axis_pos[0] < 20 or self.axis_pos[0] > 300:
           self.axis_pos[0] -= self.xvel
        if self.axis_pos[1] >= ground_y_pos:
           self.axis_pos[1] = ground_y_pos
           self.current_state = 'jump_start'
           if self.xvel != 0:
              self.change_animation('jump_start')
           else:
              self.change_animation('land')
           self.xvel = 0
           self.yvel = 0
        
    def reset(self):
        self.reset_buttons()
        self.look_at_direction()
        self.current_state = 'stand'
        self.change_animation('stand')
        self.axis_pos[0] = self.x_boundary + (18 * self.direction)
        self.axis_pos[1] = ground_y_pos
        self.stamina = 200
        self.points = 3
        self.rounds = 1
        self.timer = 0
        self.xvel = 0
        self.yvel = 0
        self.hit_freeze_time = 0
        self.attack_type = None
        self.hit_connect = False
        self.fight_distance = False
        self.fight_stance = 'high'
        
    def reset_buttons(self):
        self.punch1 = False
        self.punch2 = False
        self.kick1 = False
        self.kick2 = False

    def reset_directions(self):
        self.forward = False
        self.backward = False
        self.up = False
        self.down = False
        
    def hurt(self):
        if self.xvel != 0:
           self.axis_pos[0] += self.xvel
           self.xvel = 0
           self.attack_type = None
           self.hit_connect = False
           self.reset_buttons()
        self.update_animation()
        if self.end_of_animation():
           self.attack_type = None
           self.hit_connect = False
           self.current_state = 'stand'
           self.change_animation('stand')
           self.reset_buttons()
                      
    def knocked_up(self):
        self.axis_pos[0] += self.xvel
        self.axis_pos[1] -= self.yvel
        self.yvel -= 0.5
        if self.current_animation[self.animation_frame + 1] != -1:   
           self.update_animation()
        if self.axis_pos[1] >= ground_y_pos:
           if ((right_pit and self.direction == -1)
           or (left_pit and self.direction == 1)) \
           and self.out_of_boundary(self.axis_pos[0]):
             if abs(self.axis_pos[0] - self.x_boundary) < 10:
                self.axis_pos[0] -= 10 * self.direction 
             self.fight_distance = False              
             self.current_state = 'fall'
             self.change_animation('knocked_down')
             self.opponent.current_state = 'wait'
           else:   
              self.axis_pos[1] = ground_y_pos
              #self.xvel = 1 * -self.direction
              self.yvel = 0
              self.fight_distance = False
              self.current_state = 'knocked_down'
              self.change_animation('knocked_down')
           
    def knocked_down(self):
        global right_pit, left_pit
        self.axis_pos[0] += self.xvel
        self.update_animation()
        if self.end_of_animation():
           self.xvel = 0
           self.attack_type = None
           self.hit_connect = False
           self.reset_buttons()
           if self.out_of_boundary(self.axis_pos[0]) \
           and not ((right_pit and self.direction == -1)
           or (left_pit and self.direction == 1)):
              if self.direction == -1  and self.axis_pos[0] < 266 \
              or self.direction == 1  and self.axis_pos[0] > -10:   
                 self.xvel = 1 * -self.direction
                 self.current_state = 'knocked_down'
                 self.change_animation('roll')
                 self.opponent.current_state = 'wait'
                 game_event.wait = True
              else:
                 self.points -= 1
                 if self.direction == -1:
                    self.axis_pos[0] = 204 + 256
                    #if background_pos[0] <= -768:
                    if self.points <= 1:
                       right_pit = True
                       right_pit_pos[0] = (256 * 2) - 40
                       right_pit_old_pos[0] = (256 * 2) - 40
                    if left_pit:
                       left_pit_pos[0] = 256
                 elif self.direction == 1:
                    self.axis_pos[0] = -204
                    #if background_pos[0] >= -256:
                    if self.points <= 1:    
                       left_pit = True
                       left_pit_pos[0] = -256
                       left_pit_old_pos[0] = -256            
                    if right_pit:
                       right_pit_pos[0] = -40    
                 self.current_state = 'wait'
                 self.change_animation('stand')
                 self.opponent.timer = 0
                 self.opponent.current_state = 'scroll_background'
                 self.opponent.change_animation('walk_forward')
           else:
              self.current_state = 'stand'
              self.change_animation('stand')
      
    def fall(self):
        self.axis_pos[0] += self.xvel
        self.axis_pos[1] -= self.yvel
        if self.axis_pos[1] > 180:
           self.axis_pos[0] = -100
           self.axis_pos[1] = -100
           self.current_state = 'wait'
           self.opponent.current_state = 'win'
           self.opponent.change_animation('win')
           self.opponent.timer = 0
           game_event.add_event('happy_lady')
           global timer
           timer = -1000
           
    def win(self):
        self.timer += 1
        if self.timer > 20:
           self.timer = 0
           self.switch_sprites()
           self.change_animation('win')
        
    def wait(self):
        pass

    def dizzy(self):
        if self.current_animation[self.animation_frame + 1] != -1:
           self.update_animation()
        self.anim_time += 1
        if self.anim_time >= self.max_anim_time:
           self.anim_time = 0
           self.switch_sprites()
           self.current_sprite = self.sprites[self.current_animation[self.animation_frame]] 
           self.image = self.current_sprite['image']
           self.timer += 1
           if self.timer >= 13:
              self.timer = 0
              self.reset_buttons()
              self.look_at_direction()
              self.current_state = 'stand'
              if self.fight_distance:
                 if self.fight_stance == 'high':
                    self.change_animation('fight_stance1')
                 elif self.fight_stance == 'low':
                    self.change_animation('fight_stance2')
              else:
                 self.change_animation('stand')
              
    def switch_sprites(self):
        if self.sprites == self.left_side_sprites:
           self.sprites = self.right_side_sprites
        elif self.sprites == self.right_side_sprites:
           self.sprites = self.left_side_sprites
           
    def look_at_direction(self):
        if self.direction == 1:
           self.sprites = self.left_side_sprites
        elif self.direction == -1:
           self.sprites = self.right_side_sprites                 
        
    def draw(self, surface):
        self.image_pos[0] = self.axis_pos[0] + self.current_sprite['axis_shift'][0]
        self.image_pos[1] = self.axis_pos[1] + self.current_sprite['axis_shift'][1]
        surface.blit(self.image, self.image_pos)
def main():
    
    pygame.init()

    #Open Pygame window
    screen = pygame.display.set_mode((640, 480),) #add RESIZABLE or FULLSCREEN
    display_surface = pygame.Surface((320, 240)).convert()
    scaled_display_surface = pygame.transform.scale(display_surface,(640,480))
    #Title
    pygame.display.set_caption("Mortal Kombat")
    #icon
    icon = pygame.Surface((1, 1))
    icon.set_alpha(0)
    pygame.display.set_icon(icon)    
    #font
    font=pygame.font.SysFont('Arial', 30)
    #clock
    clock = pygame.time.Clock()

    #images
    image = pygame.image.load('SNES - Mortal Kombat - Scorpion.png').convert()
    background = pygame.image.load('SNES - Mortal Kombat - Warrior Shrine.png').convert()
    image.set_colorkey(image.get_at((0, 0)))
    #variables
    global walk_speed, ground_y_pos, background_pos
    ground_y_pos =220
    character = Character(image, 'Scorpion.spr', 'Scorpion.anm', [80, ground_y_pos], 1)
    background_width, background_height = background.get_size()
    background_pos = [CENTER_X-int(background_height/2), 240-background_height]

        
    #pygame.key.set_repeat(400, 30)

    while True:
        #loop speed limitation
        #30 frames per second is enought
        pygame.time.Clock().tick(30)
        
        for event in pygame.event.get():    #wait for events
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
               if event.key == K_ESCAPE:
                  game_mode = TITLE_SCREEN 
               #elif event.key == K_p:
                  #pause(screen, uc_font)
            character.handle_controls(event)

            
        character.states[character.current_state]()


        #draw everything
        display_surface.fill(BLUE)
        #display_surface.blit(background, background_pos)
        character.draw(display_surface)
        #opponent.draw(display_surface)
        scaled_display_surface = pygame.transform.scale(display_surface, (640, 480))
        screen.blit(scaled_display_surface, (0,0))
        pygame.display.flip()

if __name__ == "__main__":
    main()
