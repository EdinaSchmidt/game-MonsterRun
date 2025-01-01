import pygame
import random
from pygame.locals import *

class Button():
    def __init__(self, x: int, y: int, text: str, color: tuple):
        self.text = text
        self.x = x
        self.y = y
        self.button = pygame.Rect(x, y, 100, 30)
        self.color = color
        
        font = pygame.font.SysFont("Arial", 24)
        self.string = font.render(self.text, True, color)

        self.clicked = False

    def draw(self):
        action = False
	    
	#get mouse pos
        pos = pygame.mouse.get_pos()

	#check mouseover and clicked conditions
        if self.button.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
 
        screen.blit(self.string, (self.x + 12, self.y + 2))
        return action


class MainMenu():
    def __init__(self):
        screen.fill((14, 126, 173))
        font = pygame.font.SysFont("Arial", 40)
        line1 = font.render("Collect as many coins as you dare", True, (255, 255, 255))
        line2 = font.render("And leave the dungeon while you can,", True, (255, 255, 255))
        line3 = font.render("Use bombs to clear the traps with flair,", True, (255, 255, 255))
        line4 = font.render("Escape the danger, that's the plan!", True, (255, 255, 255))
        screen.blit(line1, (screen_width // 2 - 320, screen_height // 4 - 40))
        screen.blit(line2, (screen_width // 2 - 340, screen_height // 4 + 30))
        screen.blit(line3, (screen_width // 2 - 340, screen_height // 4 + 100))
        screen.blit(line4, (screen_width // 2 - 320, screen_height // 4 + 170))


class EndScreen():
    def __init__(self, win: int, loose: int):
        self.bg = pygame.Rect(0, 0, screen_width, screen_height)
        
    def draw(self):
        if loose == 1: 
            pygame.draw.rect(screen, (0, 0, 0), self.bg)
            font = pygame.font.SysFont("Arial", 63)
            text = font.render("YOU DIED", True, (255, 0, 0))
            screen.blit(text, (screen_width // 2 - 150, screen_height // 4 + 100))
            exit_button = Button(screen_width // 2 + 140, screen_height // 2 + 100, "Exit", (255, 0, 0))
            restart_button = Button(screen_width // 2 - 210, screen_height // 2 + 100, "Restart", (255, 0, 0))
            
            if restart_button.draw():
                return "restart"
            
            if exit_button.draw():
                return "exit"

        if win == 1: 
            pygame.draw.rect(screen, (148, 235, 19), self.bg)
            font = pygame.font.SysFont("Arial", 100)
            text = font.render("YOU WON", True, (255, 255, 255))
            screen.blit(text, (screen_width // 2 - 250, screen_height // 4 + 100))

            font = pygame.font.SysFont("Arial", 50)
            text = font.render(f"Score: {robot.points}", True, (255, 255, 255)) 
            screen.blit(text, (screen_width // 2 - 100, screen_height // 4 + 250))
            
            exit_button = Button(screen_width // 2 + 125, screen_height // 2 + 100, "Exit", (255, 255, 255))
            restart_button = Button(screen_width // 2 - 225, screen_height // 2 + 100, "Restart", (255, 255, 255))
  
            if restart_button.draw():
                return "restart"

            if exit_button.draw():
                return "exit"


class Player():
    def __init__(self, x, y):
        self.reset(x, y)

    def update(self, loose, win):
        dx = 0
        dy = 0

        line_start = self.rect.center

        # movement handling
        if loose == 0 and win == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                dx -= self.speed
            if key[pygame.K_RIGHT]:
                dx += self.speed
            if key[pygame.K_UP]:
                dy -= self.speed
            if key[pygame.K_DOWN]:
                dy += self.speed
            
            # turbo handling
            if key[pygame.K_LSHIFT] and self.turbo_pressed == False:
                self.turbo_pressed = True

            if self.turbo_pressed:
                self.turbo_timer -= 1
                self.speed = 6

                if self.turbo_timer <= 0:
                    self.speed = 3    
                    
                    self.turbo_charge -= 1
                    if self.turbo_charge <= 0:
                        self.turbo_charge = 90
                        self.turbo_timer = 15
                        self.turbo_pressed = False

            # bomb handling
            if key[pygame.K_SPACE] and self.bomb_pressed == False and self.bombs > 0:
                self.bombs -= 1
                self.epicenter = self.rect.center
                self.explosion = True
                self.bomb_pressed = True

            if self.explosion:
                explosion = Explosion(self.epicenter)
                explosion_group.add(explosion)
                for monster in monster_group:
                    if monster.danger_zone:
                        monster.is_dead = True
                self.explosion = False

            if self.bomb_pressed:       
                self.bomb_charge -= 1
                if self.bomb_charge <= 0:
                    self.bomb_pressed = False
                    self.bomb_charge = 200
                                      
            #check collisions with walls
            for tile in world.wall_list:
                if tile.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    dy = 0

            #check for collision with monster_dens
            for tile in world.monster_den_list:
                if tile.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    loose = 1
                if tile.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    loose = 1
         
            #check for collision with monsters
            if pygame.sprite.spritecollide(self, monster_group, False):
                if pygame.sprite.spritecollide(self, monster_group, False, pygame.sprite.collide_mask):
                    loose = 1

            #check for out of screen pixels = door exit
            if self.rect.left < 0 or self.rect.right > screen_width or self.rect.top < 0 or self.rect.bottom > screen_height:
                    win = 1

            #check for collision with coins
            if pygame.sprite.spritecollide(self, coin_group, False):
                if pygame.sprite.spritecollide(self, coin_group, True, pygame.sprite.collide_mask):
                    self.points += 1
                    new_coin = Coin()
                    new_coin.place_new_coin()
                    new_monster = Monster()

            #check for collision with bombs
            if pygame.sprite.spritecollide(self, bomb_group, False):
                if pygame.sprite.spritecollide(self, bomb_group, True, pygame.sprite.collide_mask):
                    self.bombs += 1
            
            #update player coords
            self.rect.x += dx 
            self.rect.y += dy 

        screen.blit(self.image, self.rect)

        return loose, win
    

    def monster_in_danger_zone(self):
        line_start = self.rect.centerx, self.rect.centery
        for monster in monster_group:
            line_end = monster.rect.centerx, monster.rect.centery

            monster.in_sight = True

            for wall in world.wall_list:
                if wall.clipline((line_start, line_end)):
                    monster.in_sight = False
                    break
                else:
                    monster.in_sight = True
               
            if monster.in_sight == True:
                if ((monster.rect.centerx - self.rect.centerx)**2 + (monster.rect.centery - self.rect.centery)**2)**0.5 <= tile_size * 3:
                    monster.danger_zone = True
                else:
                    monster.danger_zone = False
            

    def reset(self, x, y):
        img = pygame.image.load("robot.png")
        target_height = tile_size - 2

        original_width, original_height = img.get_size()
        
        scale_factor = target_height / original_height
        new_width = int(original_width * scale_factor)
        
        self.image = pygame.transform.scale(img, (new_width, target_height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.topleft = (x, y)
        self.mask = pygame.mask.from_surface(self.image)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.speed = 3
        self.turbo_pressed = False
        self.turbo_timer = 15
        self.turbo_charge = 90
        self.bomb_pressed = False
        self.explosion = False
        self.bomb_charge = 200
        self.points = 0
        self.bombs = 0


class World():
    def __init__(self, level_data):
        self.floor_list = []
        self.wall_list = []
        self.monster_den_list = []
        self.door_list = []

        row_count = 0
        for row in level_data:
            col_count = 0
            for tile in row:
                if tile == 0:
                    floor = pygame.Rect(col_count * tile_size, row_count * tile_size, tile_size, tile_size)
                    self.floor_list.append(floor)                

                if tile == 1:
                    wall = pygame.Rect(col_count * tile_size, row_count * tile_size, tile_size, tile_size)
                    self.wall_list.append(wall) 

                if tile == 2:
                    monster_den = pygame.Rect(col_count * tile_size, row_count * tile_size, tile_size, tile_size)
                    self.monster_den_list.append(monster_den)


                if tile == 3:
                    door_bg = pygame.Rect(col_count * tile_size, row_count * tile_size, tile_size, tile_size)
                    door_rect = pygame.Rect(col_count * tile_size, row_count * tile_size, tile_size, tile_size)
                    door_frame = pygame.Rect(col_count * tile_size, row_count * tile_size, tile_size, tile_size)
                    font = pygame.font.SysFont("Arial", 10)
                    text = font.render(f"EXIT", True, (0, 0, 0))
                    text_pos = (col_count * tile_size + 13, row_count * tile_size + 6, tile_size - 26, tile_size)
                    
                    self.door_list.append((door_bg, door_rect, door_frame, text, text_pos))

                col_count += 1
            row_count += 1


    def draw(self):
        for tile in self.floor_list:
            pygame.draw.rect(screen, (225, 225, 225), tile)
        
        for tile in self.wall_list:
            pygame.draw.rect(screen, (38, 70, 83), tile)

        for tile in self.monster_den_list:
            pygame.draw.rect(screen, (0, 0, 0), tile)
        
        for door in self.door_list:
            pygame.draw.rect(screen, (38, 70, 83), door[0])
            pygame.draw.rect(screen, (0, 255, 255), door[1])
            pygame.draw.rect(screen, (0, 0, 0), door[2], 2)
            screen.blit(door[3], door[4])
            

class Monster(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        
        img = pygame.image.load("monster.png")
        target_height = tile_size

        original_width, original_height = img.get_size()
        
        scale_factor = target_height / original_height
        new_width = int(original_width * scale_factor)
        
        self.image = pygame.transform.scale(img, (new_width, target_height))
        self.mask = pygame.mask.from_surface(self.image)
        self.is_dead = False 
        self.rect = self.image.get_rect()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.dx = 0
        self.dy = 0
        self.move_timer = random.randint(10, 35)
        self.in_sight = False
        self.danger_zone = False
        self.timer = 30
        self.out = False
        monster_group.add(self)
        
    def update(self, player):
        if self.timer > 0:
            self.timer -= 1

        if self.timer <= 0 and not self.out:
            den = random.choice(world.monster_den_list)
            self.rect.center = den.center
            self.out = True

        if self.out and not self.is_dead:
                
                #moving around aimlessly when far from the player
                if self.danger_zone == False:
                    self.speed = 1
                    self.move_timer -= 1
                    if self.move_timer <= 0:
                        self.dx = random.choice([-1, 0, 1])
                        self.dy = random.choice([-1, 0, 1])
                        self.move_timer = random.randint(150, 250)
                
                #chasing the player when it gets close
                else:
                    self.speed = 2
                    if player.rect.x > self.rect.x:
                        self.dx = 1
                    elif player.rect.x < self.rect.x:
                        self.dx = -1
                    else:
                        self.dx = 0

                    if player.rect.y > self.rect.y:
                        self.dy = 1
                    elif player.rect.y < self.rect.y:
                        self.dy = -1
                    else:
                        self.dy = 0

                #check collisions with walls
                for tile in world.wall_list:
                    if tile.colliderect(self.rect.x + (self.dx * self.speed), self.rect.y, self.width, self.height):
                        self.dx = 0
                    if tile.colliderect(self.rect.x, self.rect.y + (self.dy * self.speed), self.width, self.height):
                        self.dy = 0
                
                for tile in world.door_list:
                    if tile[1].colliderect(self.rect.x + (self.dx * self.speed), self.rect.y, self.width, self.height):
                        self.dx = 0
                    if tile[1].colliderect(self.rect.x, self.rect.y + (self.dy * self.speed), self.width, self.height):
                        self.dy = 0

                #update monster coords
                self.rect.x += (self.dx * self.speed)
                self.rect.y += (self.dy * self.speed)

                screen.blit(self.image, self.rect)
            
        if self.out and self.is_dead:
                splash = Blood(self.rect.center)
                blood_group.add(splash)
                self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.center = center
        self.r = 0
        
    def update(self):
        self.r += 25
        if self.r < tile_size * 3:
            pygame.draw.circle(screen, (255, 0, 0), self.center, self.r, 2)
        else:
            self.kill()

        
class Blood(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.center = center
        self.blood_timer = 100

    def update(self):
        self.blood_timer -= 1
        if self.blood_timer > 0:
            pygame.draw.circle(screen, (0, 0, 255), self.center, 20)
        else:
            self.kill()

class Bomb(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (216, 30, 91), (tile_size // 2, tile_size // 2), tile_size // 2 - 6)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.creation_time = pygame.time.get_ticks()
        
    def place_new_bomb(self):
        valid_tiles = [tile for tile in world.floor_list if not (any(tile.colliderect(coin.rect) for coin in coin_group) or any(tile.colliderect(bomb) for bomb in bomb_group))]    
        tile = random.choice(valid_tiles)
        self.rect.center = tile.center
        bomb_group.add(self)

    #removing old bombs
    def update(self):
        if pygame.time.get_ticks() - self.creation_time >= 10000:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        img = pygame.image.load("coin.png")
        target_height = tile_size // 2

        original_width, original_height = img.get_size()
        
        scale_factor = target_height / original_height
        new_width = int(original_width * scale_factor)
        
        self.image = pygame.transform.scale(img, (new_width, target_height))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()

    def place_new_coin(self):
        valid_tiles = [tile for tile in world.floor_list if not (any(tile.colliderect(coin.rect) for coin in coin_group) or any(tile.colliderect(bomb.rect) for bomb in bomb_group))]    
        tile = random.choice(valid_tiles)
        self.rect.center = tile.center
        coin_group.add(self)


pygame.init()
clock = pygame.time.Clock()
screen_width, screen_height = 1000, 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('MonsterRun')

#game varaiables
tile_size = 50
loose = 0
win = 0
main_menu = True
bomb_placed = False

# creating a map
# 1: wall, 2: monster den, 3: door
level_data = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,2,0,0,0,1],
            [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,1,1,1,1,1,0,0,0,0,0,0,1,0,0,0,0,1],
            [1,0,0,0,0,1,2,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,3],
            [1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1],
            [3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
            [1,0,0,0,0,1,0,0,1,1,1,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,2,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,3,1,1,1,1,1,1,1,1,1,1,1,1,1]
            ]

#placing the player in the middle of the screen
robot = Player(screen_width // 2, screen_height // 2)  

start_button = Button(screen_width // 2 - 300, screen_height // 2 + 100, "Start", (255, 255, 255))
exit_button = Button(screen_width // 2 + 200, screen_height // 2 + 100, "Exit", (255, 255, 255))

monster_group = pygame.sprite.Group()
blood_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
bomb_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

world = World(level_data)

#placing starting coins
for _ in range(2):
    coin = Coin()
    coin.place_new_coin()


#main loop
run = True
while run:
    if main_menu:
        MainMenu()
        if start_button.draw():
            main_menu = False
            
        if exit_button.draw():
            run = False
    
    else:
        screen.fill((225, 225, 225))
        world.draw()
        blood_group.update()
        explosion_group.update()
        
        if loose == 0 and win == 0:
            monster_group.update(robot)
            
        coin_group.draw(screen)
        bomb_group.draw(screen)

        loose = robot.update(loose, win)[0]
        win = robot.update(loose, win)[1]
        robot.monster_in_danger_zone()

    
        game_font = pygame.font.SysFont("Arial", 24)
        text_points = game_font.render(f"Score: {robot.points}", True, (255, 255, 255))
        text_turbo = game_font.render(f"Turbo: <Left Shift>", True, (255, 255, 255))
        text_bomb = game_font.render(f"Bombs: {robot.bombs}  <Space>", True, (255, 255, 255))
        screen.blit(text_points, (screen_width - 150, 10))
        screen.blit(text_turbo, (10, 10))
        screen.blit(text_bomb, (260, 10))

        coin_group.update()
        bomb_group.update()
       

        if bomb_placed == False and robot.points > 0 and robot.points % 5 == 0:
            bomb = Bomb()
            bomb.place_new_bomb()
            bomb_placed = True
        
        if robot.points % 5 != 0:
            bomb_placed = False


        if loose == 1 or win == 1:
            end_screen = EndScreen(win, loose)
            action = end_screen.draw()
            
            if loose == 1:
                if action == "restart":
                    robot.reset(screen_width // 2, screen_height // 2)
                    monster_group.empty()
                    loose = 0
                elif action == "exit":
                    run = False
            
            if win == 1:
                if action == "restart":
                    robot.reset(screen_width // 2, screen_height // 2)
                    monster_group.empty()
                    win = 0
                elif action == "exit":
                    run = False
            
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.flip()
    clock.tick(60)
