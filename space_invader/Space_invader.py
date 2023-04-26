import pygame
import os
import time
import random
from pygame.locals import *
from pygame import mixer


# Initialize Pygame
pygame.init()
pygame.font.init()

# Set up the game window
width = 750
height = 750
screen = pygame.display.set_mode((width, height))


# Load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("red_ship.svg"))
PINK_SPACE_SHIP = pygame.image.load(os.path.join("pink_ship.svg"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("blue_ship.svg"))

# Laser and Bomb
YELLOW_LASER = pygame.image.load(os.path.join("pixel_laser_yellow.png"))
THROWABLE_BOMB = pygame.image.load(os.path.join("power_up_bomb_throwable.svg"))
# Power up icons
POWER_UP_BOMB = pygame.image.load(os.path.join("power_up_bomb.svg"))
POWER_UP_DOUBLESHOT = pygame.image.load(os.path.join("power_up_doubleshot.svg"))
POWER_UP_HEART = pygame.image.load(os.path.join("power_up_heart.svg"))
POWER_UP_SPEED = pygame.image.load(os.path.join("power_up_speed.svg"))
THROWABLE_BOMB = pygame.image.load(os.path.join("power_up_bomb_throwable.svg"))

# Player ships
player_ship = pygame.image.load(os.path.join("player_ship.svg"))

# Player hearts
player_heart = pygame.image.load(os.path.join("player_heart.svg"))

# Load the backround
BG = pygame.transform.scale(pygame.image.load(os.path.join("background-black.png")), (width, height))

# Load music
music = pygame.mixer.music.load("mixkit-space-game-668.mp3")
pygame.mixer.music.set_endevent(pygame.USEREVENT)
pygame.mixer.music.play()

# Class bomb
class Bomb():
    def __init__(self, x, y , img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    # Draws the bomb
    def draw(self, window):
        window.blit(self.img,(self.x,self.y))

    # Move the bomb 
    def move(self, val):
        self.y += val

    # Check if bomb goes off the screen    
    def off_screen(self,height):
        return not(self.y <= height and self.y >= 0)

    # Call collide to see if laser over laped a enemy
    def collision(self, obj):
        return collide(self, obj)


# Create a class for the laser
class Laser:
    def __init__(self, x, y , img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    # Draws the laser
    def draw(self, window):
        window.blit(self.img,(self.x,self.y))

    # Move the laser 
    def move(self, val):
        self.y += val

    # Check if laser goes off the screen    
    def off_screen(self,height):
        return not(self.y <= height and self.y >= 0)

    # Call collide to see if laser over laped a enemy
    def collision(self, obj):
        return collide(self, obj)



class Ship:
    COOLDOWN = 20

    def __init__(self, x, y, point=0):
        self.x = x
        self.y = y
        self.points = point   
        self.lasers = []
        self.power_up = []
        self.cool_down_timer = 0
        self.true = True
        
    # Draw bomb and lasers
    def draw(self, window):
        window.blit(self.ship_img,(self.x, self.y))
        for bomb in self.power_up:
            bomb.draw(window)
            
        for laser in self.lasers:
            laser.draw(window)
    
    # Cooldown counter
    def cooldown(self):
        if self.cool_down_timer > 0:
            self.cool_down_timer -= 1
    
    # Shoot a laser
    def shoot(self):
        if self.cool_down_timer == 0:
            laser = Laser(self.x+52, self.y+50, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_timer = self.COOLDOWN
    
    # Power-up for doubleshot
    def double_shoot(self):
        if self.true:
            laser1 = Laser(self.x+30, self.y+50, self.laser_img)
            laser2 = Laser(self.x+75, self.y+50, self.laser_img)
            self.lasers.append(laser1)
            self.lasers.append(laser2)

    # checks cooldown and call bomb
    def bomb_shoot(self):
        if self.cool_down_timer == 0:
            bomb = Bomb(self.x, self.y, self.bomb_img)
            self.power_up.append(bomb)
            self.cool_down_timer = self.COOLDOWN


# Player class
class Player(Ship):
    def __init__(self, x, y, point=0):
        super().__init__(x, y, point)
        self.ship_img = player_ship
        self.laser_img = YELLOW_LASER
        self.bomb_img = THROWABLE_BOMB
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.lives = 3
        self.heart_imgs = [player_heart] * self.lives
        self.total_points = point

    # Laser bomb and checks if it collides with enemies
    def move_lasers(self,vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            self.points += 50
    
    # Moves bomb and checks if it collides with enemies
    def move_bomb(self,vel, objs):
        for bomb in self.power_up:
            bomb.move(vel)
            if bomb.off_screen(height):
                self.power_up.remove(bomb)
            else:
                for obj in objs:
                    if bomb.collision(obj):
                        objs.remove(obj)
                        if bomb in self.power_up:
                            self.power_up.remove(bomb)
                            self.points += 50

    # Draws players stats
    def draw_stats(self, window):
        font = pygame.font.Font(None, 30)
        score_text = font.render(f"Points: {self.points}", True, (255, 255, 255))
        window.blit(score_text, (10, 10))
        for i in range(self.lives):
            j = 60 * i
            window.blit(self.heart_imgs[i],(600,-60 +j))

    # If lives need to be removed it will take off on screen and on the live counter
    def remove_lives(self):
        self.lives -= 1
        self.heart_imgs.pop()
    
    # If lives need to be added it will draw on the screen and on the live counter
    def add_lives(self):
        self.lives += 1
        self.heart_imgs.append(player_heart)

    # Will update Player and stats
    def draw(self, window):
        super().draw(window)
        self.draw_stats(window)

    

class Enemy(Ship):
    # List of names and ship imgs 
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP),
                "pink": (PINK_SPACE_SHIP),
                "blue": (BLUE_SPACE_SHIP)
                }

    def __init__(self, x, y, color):
        super().__init__(x,y)
        self.ship_img= self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    # Movement speed
    def move(self, vel):
        self.y += vel

# Class for power-ups on the screen
class power_up_icon(Ship):
    
    # List of names and power-ups imgs 
    POWER_UP = {
        "bomb": (POWER_UP_BOMB),
        "doubleshot": (POWER_UP_DOUBLESHOT),
        "speed": (POWER_UP_SPEED),
        "life": (POWER_UP_HEART)
                }

    
    def __init__(self, x, y, power_up):
        super().__init__(x,y)
        self.ship_img = self.POWER_UP[power_up]
        self.mask = pygame.mask.from_surface(self.ship_img)
        
# Check x and y of obj1-2 if they over lap
def collide(obj1, obj2):
    offset_x = obj1.x - obj2.x
    offset_y = obj1.y - obj2.y
    return obj2.mask.overlap(obj1.mask, (offset_x, offset_y)) != None

def main():
    run = True
    lost = False
    FPS = 120
    power_check_ = []
    
    level = 0
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    power_up  =[]
    ammo = 10
    
    
    wave_length = 5
    enemy_vel = 2

    player_vel = 5
    lives = 3
    
    laser_vel = 5

    player = Player(300, 300)
    

    clock = pygame.time.Clock()

    
    
    # Updates the screen for enemies, power ups and player 
    def redraw_window():
        screen.blit(BG, (0,0))

        # Draws the enemies 
        for enemy in enemies:
            enemy.draw(screen)

        # Draws the power-ups
        for power in power_up:
            power.draw(screen)
        
        # Draws player
        player.draw(screen)
        
        # Check if lost
        if lives == 0:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            screen.blit(lost_label, (width/2 - lost_label.get_width()/2, 350))
           

        pygame.display.update()
    while run:
        clock.tick(FPS)
        
        # Redraw the background
        redraw_window()
        
        # Check if lives = 0
        if lives == 0:
            lost = True
            pygame.time.wait(2000)
            if lost:
                run = False

        # When all enemies are destroyed then a new power up will spawn
        if len(enemies) == 0:
            level += 1
            check = random.choice(["bomb","doubleshot","speed","life"])
            power = power_up_icon(random.randrange(-70, width-120), random.randrange(0,700), check)
            
            power_up.append(power)
            wave_length += 5

            # Spawe in new enimies in a wave
            for i in range(wave_length):
                enemy = Enemy(random.randrange(-70, width-120), random.randrange(-1000, -100), random.choice(["red", "blue", "pink"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        
        # Player movement 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > -70: # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel < width-120: # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > -100: # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + 15 < height-120: # down
            player.y += player_vel

        # Player shooting and other power-up keys
        if keys[pygame.K_q]:
            if power_check_ != []:
                if power_check_[0:] == "bomb":
                    player.bomb_shoot()
                    power_check_ = power_check_[1:]
                    power_check_ = "explode"
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_e]:
            if ammo >= 0:
                if power_check_[0:] == "doubleshot":
                    player.double_shoot()
                    ammo -= 1
                    if ammo == 0:
                        power_check_ = power_check_[1:]
                        ammo = 10
            
        # Check if enemies location collides with players
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            if collide(enemy, player):
                player_vel = 5
                enemies.remove(enemy)
                player.remove_lives()
                lives -= 1

            elif enemy.y > height-120:
                    lives -= 1
                    player.remove_lives()
                    player_vel = 5
                    enemies.remove(enemy)
            
            # Check if power_up location collides with players
            for power in power_up[:]:
                if collide(power, player):
                    power_check_ = check
                    if power_check_ == "life":
                        lives += 1
                        player.add_lives()
                    if power_check_ == "speed":
                        player_vel += 5
                    power_up.remove(power)
                
        # Move the lasers with also check if they collide 
        player.move_lasers(-laser_vel, enemies)
        player.move_bomb(-laser_vel, enemies)

def main_menu():
    title_font = pygame.font.SysFont("comicsans", 50)
    run = True
    while run:
        screen.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin", 0.5, (255,255,255))
        screen.blit(title_label, (width/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT:
                pygame.mixer.music.queue("mixkit-space-game-668.mp3")
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
