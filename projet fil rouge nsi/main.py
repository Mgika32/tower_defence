import pygame
import sys
from random import *
import constants as c
from pygame.math import Vector2
import math
from enemy_data import ENEMY_DATA
from world import World
import json
from turret import Turret

# Variable initialization
inv = {"a": 0, "b": 0, "artillerie": 0, "c": 0, "lance_grenade": 0, "d": 0, "sorcier": 0, "cannonier": 0, "lance_pierre": 0, "archer": 0, "caserne": 0, "ralentisseur" : 0}
liste_item = {5: ["a", "b"], 4: ["artillerie", "c"], 3: ['lance_grenade', "d"], 2: ['sorcier', 'cannonier'], 1: ['lance_pierre', 'archer', 'caserne']}
button_caisse_rect = pygame.Rect(50, 100, 100, 50)
button_epique_rect = pygame.Rect(250, 100, 100, 50)

pygame.init()

WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Menu avec Play et Gasha")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Load background image
background_img = pygame.image.load("ton_image_de_fond.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Create fonts
font = pygame.font.Font(None, 50)

# Button texts
play_text = font.render('Play', True, BLACK)
gasha_text = font.render('Gasha', True, BLACK)
retour_text = font.render('Retour', True, BLACK)


# Button positions
play_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 100, 200, 50)
gasha_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
button_retour_rect = pygame.Rect(50, 550, 100, 50)

def draw_button(rect, text):
    pygame.draw.rect(screen, GRAY, rect)
    screen.blit(text, (rect.x + (rect.width - text.get_width()) // 2, rect.y + (rect.height - text.get_height()) // 2))

def tirage(crate):
    tirage_proba = randint(1,100)
    sorti_etoile = 0
    if crate == 1:
        
        if tirage_proba <= 50:
            sorti_etoile = 1
        elif tirage_proba <= 80:
            sorti_etoile = 2
        elif tirage_proba <= 90:
            sorti_etoile = 3
        elif tirage_proba <= 96:
            sorti_etoile = 4 
        else: 
            sorti_etoile = 5
    else :
        if tirage_proba <= 30:
            sorti_etoile = 1
        elif tirage_proba <= 60:
            sorti_etoile = 2
        elif tirage_proba <= 75:
            sorti_etoile = 3
        elif tirage_proba <= 90:
            sorti_etoile = 4 
        else: 
            sorti_etoile = 5
    
    return sorti_etoile

def choix_item(sortie_etoile,liste_item,inv):
    item = liste_item[sortie_etoile] [randint(0,len(liste_item[sortie_etoile])-1)]
    if item in inv:
        print(f"tu as eu {item} ")
        inv[item] += 1
        font = pygame.font.Font(None, 36)
        item_text = font.render(item, True, BLACK)
        item_x = screen.get_width() // 2 - item_text.get_width() // 2
        item_y = screen.get_height() // 2 - item_text.get_height() // 2
        screen.blit(item_text, (item_x, item_y))
        pygame.display.flip()
        pygame.time.delay(2000)  # 2 seconds
        screen.fill(WHITE, (item_x, item_y, item_text.get_width(), item_text.get_height()))
        pygame.display.flip()
        return item
    

#classes : 

class Button():
  def __init__(self, x, y, image, single_click):
    self.image = image
    self.rect = self.image.get_rect()
    self.rect.topleft = (x, y)
    self.clicked = False
    self.single_click = single_click

  def draw(self, surface):
    action = False
    #get mouse position
    pos = pygame.mouse.get_pos()

    #check mouseover and clicked conditions
    if self.rect.collidepoint(pos):
      if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
        action = True
        #if button is a single click type, then set clicked to True
        if self.single_click:
          self.clicked = True

    if pygame.mouse.get_pressed()[0] == 0:
      self.clicked = False

    #draw button on screen
    surface.blit(self.image, self.rect)

    return action
  
class Enemy(pygame.sprite.Sprite):
  def __init__(self, enemy_type, waypoints, images):
    pygame.sprite.Sprite.__init__(self)
    self.waypoints = waypoints
    self.pos = Vector2(self.waypoints[0])
    self.target_waypoint = 1
    self.health = ENEMY_DATA.get(enemy_type)["health"]
    self.speed = ENEMY_DATA.get(enemy_type)["speed"]
    self.angle = 0
    self.original_image = images.get(enemy_type)
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos

  def update(self, world):
    self.move(world)
    self.rotate()
    self.check_alive(world)

  def move(self, world):
    #define a target waypoint
    if self.target_waypoint < len(self.waypoints):
      self.target = Vector2(self.waypoints[self.target_waypoint])
      self.movement = self.target - self.pos
    else:
      #enemy has reached the end of the path
      self.kill()
      world.health -= 1
      world.missed_enemies += 1

    #calculate distance to target
    dist = self.movement.length()
    if dist >= (self.speed * world.game_speed):
      self.pos += self.movement.normalize() * (self.speed * world.game_speed)
    else:
      if dist != 0:
        self.pos += self.movement.normalize() * dist
      self.target_waypoint += 1

  def rotate(self):
    #calculate distance to next waypoint
    dist = self.target - self.pos
    #use distance to calculate angle
    self.angle = math.degrees(math.atan2(-dist[1], dist[0]))
    #rotate l'image et met a jour le rectangle
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect()
    self.rect.center = self.pos

  def check_alive(self, world):
    if self.health <= 0:
      world.killed_enemies += 1
      world.money += c.KILL_REWARD
      self.kill()
#game variables
game_over = False
game_outcome = 0 # -1 is loss & 1 is win
level_started = False
last_enemy_spawn = pygame.time.get_ticks()
placing_turrets = False
selected_turret = None

#load images
map_image = pygame.image.load('levels/level.png').convert_alpha()
#turret spritesheets
turret_spritesheets = []
for x in range(1, c.TURRET_LEVELS + 1):
  turret_sheet = pygame.image.load(f'assets/images/turrets/turret_{x}.png').convert_alpha()
  turret_spritesheets.append(turret_sheet)
#individual turret image for mouse cursor
cursor_turret = pygame.image.load('assets/images/turrets/cursor_turret.png').convert_alpha()
#enemies
enemy_images = {
  "weak": pygame.image.load('assets/images/enemies/enemy_1.png').convert_alpha(),
  "medium": pygame.image.load('assets/images/enemies/enemy_2.png').convert_alpha(),
  "strong": pygame.image.load('assets/images/enemies/enemy_3.png').convert_alpha(),
  "elite": pygame.image.load('assets/images/enemies/enemy_4.png').convert_alpha()
}
#buttons
buy_turret_image = pygame.image.load('assets/images/buttons/buy_turret.png').convert_alpha()
cancel_image = pygame.image.load('assets/images/buttons/cancel.png').convert_alpha()
upgrade_turret_image = pygame.image.load('assets/images/buttons/upgrade_turret.png').convert_alpha()
begin_image = pygame.image.load('assets/images/buttons/begin.png').convert_alpha()
restart_image = pygame.image.load('assets/images/buttons/restart.png').convert_alpha()
fast_forward_image = pygame.image.load('assets/images/buttons/fast_forward.png').convert_alpha()
#gui
heart_image = pygame.image.load("assets/images/gui/heart.png").convert_alpha()
coin_image = pygame.image.load("assets/images/gui/coin.png").convert_alpha()
logo_image = pygame.image.load("assets/images/gui/logo.png").convert_alpha()

#load sounds
shot_fx = pygame.mixer.Sound('assets/audio/shot.wav')
shot_fx.set_volume(0.5)

#load json data
with open('levels/level.tmj') as file:
  world_data = json.load(file)

#police pour afficher le texte
text_font = pygame.font.SysFont("Consolas", 24, bold = True)
large_font = pygame.font.SysFont("Consolas", 36)

#fonction poru afficher le texte a l'ecran
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

def display_data():
  pygame.draw.rect(screen, "maroon", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, c.SCREEN_HEIGHT))
  pygame.draw.rect(screen, "grey0", (c.SCREEN_WIDTH, 0, c.SIDE_PANEL, 400), 2)
  screen.blit(logo_image, (c.SCREEN_WIDTH, 400))
  #affiche les données 
  draw_text("LEVEL: " + str(world.level), text_font, "grey100", c.SCREEN_WIDTH + 10, 10)
  screen.blit(heart_image, (c.SCREEN_WIDTH + 10, 35))
  draw_text(str(world.health), text_font, "grey100", c.SCREEN_WIDTH + 50, 40)
  screen.blit(coin_image, (c.SCREEN_WIDTH + 10, 65))
  draw_text(str(world.money), text_font, "grey100", c.SCREEN_WIDTH + 50, 70)
  

def create_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  #calcule les sequence pour les tiles de la map 
  mouse_tile_num = (mouse_tile_y * c.COLS) + mouse_tile_x
  #check if that tile is grass
  if world.tile_map[mouse_tile_num] == 7:
    #regarde si il n'y a pas deja une tourelle 
    space_is_free = True
    for turret in turret_group:
      if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
        space_is_free = False
    #si l'espace est libre alors on cree la tourelle
    if space_is_free == True:
      new_turret = Turret(turret_spritesheets, mouse_tile_x, mouse_tile_y, shot_fx)
      turret_group.add(new_turret)
      #paye la tourelle
      world.money -= c.BUY_COST

def select_turret(mouse_pos):
  mouse_tile_x = mouse_pos[0] // c.TILE_SIZE
  mouse_tile_y = mouse_pos[1] // c.TILE_SIZE
  for turret in turret_group:
    if (mouse_tile_x, mouse_tile_y) == (turret.tile_x, turret.tile_y):
      return turret

def clear_selection():
  for turret in turret_group:
    turret.selected = False

#crée le monde
world = World(world_data, map_image)
world.process_data()
world.process_enemies()

#crée les groupes
enemy_group = pygame.sprite.Group()
turret_group = pygame.sprite.Group()

#crée les boutons
turret_button = Button(c.SCREEN_WIDTH + 30, 120, buy_turret_image, True)
cancel_button = Button(c.SCREEN_WIDTH + 50, 180, cancel_image, True)
upgrade_button = Button(c.SCREEN_WIDTH + 5, 180, upgrade_turret_image, True)
begin_button = Button(c.SCREEN_WIDTH + 60, 300, begin_image, True)
restart_button = Button(310, 300, restart_image, True)
fast_forward_button = Button(c.SCREEN_WIDTH + 50, 300, fast_forward_image, False)

running = True
inmenu = True
ingasha = False
in_play = False

while running:
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
    if inmenu:
        screen.blit(background_img, (0, 0))
        draw_button(play_button_rect, play_text)
        draw_button(gasha_button_rect, gasha_text)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    print("Play Button Pressed!")
                    inmenu = False
                    in_play = True
                if gasha_button_rect.collidepoint(event.pos):
                    print("Gasha Button Pressed!")
                    inmenu = False
                    ingasha = True

    elif ingasha:
        screen.fill(WHITE)
        pygame.draw.rect(screen, RED, button_caisse_rect)
        pygame.draw.rect(screen, GREEN, button_epique_rect)
        pygame.draw.rect(screen, GRAY, button_retour_rect)
        font = pygame.font.Font(None, 36)
        text1 = font.render("simple", True, BLACK)
        text2 = font.render("double", True, BLACK)
        text3 = font.render("Retour", True, BLACK)
        screen.blit(text1, (button_caisse_rect.x + 10, button_caisse_rect.y + 10))
        screen.blit(text2, (button_epique_rect.x + 10, button_epique_rect.y + 10))
        screen.blit(text3, (button_retour_rect.x + 10, button_retour_rect.y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_caisse_rect.collidepoint(event.pos):
                    crate = 1
                    print(choix_item(tirage(crate), liste_item, inv))
                    print(inv)
                elif button_epique_rect.collidepoint(event.pos):
                    crate = 2
                    print(choix_item(tirage(crate), liste_item, inv))
                    print(inv)
                elif button_retour_rect.collidepoint(event.pos):
                    print("Retour Button Pressed!")
                    ingasha = False
                    inmenu = True

        pygame.display.flip()

    elif in_play:
       if game_over == False:
        #regarde si le joueur a perdu
        if world.health <= 0:
          game_over = True
          game_outcome = -1 #loss
        #regarde si le joueur a gagne
        if world.level > c.TOTAL_LEVELS:
          game_over = True
          game_outcome = 1 #win

        #update groups
        enemy_group.update(world)
        turret_group.update(enemy_group, world)

        #surligne la tourelle selectionnée
        if selected_turret:
          selected_turret.selected = True
        #dessine le level
        world.draw(screen)
        #dessine les groups
        enemy_group.draw(screen)
        for turret in turret_group:
          turret.draw(screen)
        display_data()
        if game_over == False:
          #regarde si le niveau a été démarré ou non
          if level_started == False:
            if begin_button.draw(screen):
              level_started = True
          else:
            #deplacement rapide 
            world.game_speed = 1
            if fast_forward_button.draw(screen):
              world.game_speed = 2
            #spawn enemies
            if pygame.time.get_ticks() - last_enemy_spawn > c.SPAWN_COOLDOWN:
              if world.spawned_enemies < len(world.enemy_list):
                enemy_type = world.enemy_list[world.spawned_enemies]
                enemy = Enemy(enemy_type, world.waypoints, enemy_images)
                enemy_group.add(enemy)
                world.spawned_enemies += 1
                last_enemy_spawn = pygame.time.get_ticks()
          #regarde si le niveau est fini
          if world.check_level_complete() == True:
            world.money += c.LEVEL_COMPLETE_REWARD
            world.level += 1
            level_started = False
            last_enemy_spawn = pygame.time.get_ticks()
            world.reset_level()
            world.process_enemies()
          draw_text(str(c.BUY_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 135)
          screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 130))
          if turret_button.draw(screen):
            placing_turrets = True
          #si tu places des tourelles alors montre le bouton annuler
          if placing_turrets == True:
            #affiche le curseur tourelle 
            cursor_rect = cursor_turret.get_rect()
            cursor_pos = pygame.mouse.get_pos()
            cursor_rect.center = cursor_pos
            if cursor_pos[0] <= c.SCREEN_WIDTH:
              screen.blit(cursor_turret, cursor_rect)
            if cancel_button.draw(screen):
              placing_turrets = False
          #si il y a une tourelle selectionnée alors montre le bouton annuler
          if selected_turret:
            #if a turret can be upgraded then show the upgrade button
            if selected_turret.upgrade_level < c.TURRET_LEVELS:
              #montre le prix et l'affiche
              draw_text(str(c.UPGRADE_COST), text_font, "grey100", c.SCREEN_WIDTH + 215, 195)
              screen.blit(coin_image, (c.SCREEN_WIDTH + 260, 190))
              if upgrade_button.draw(screen):
                if world.money >= c.UPGRADE_COST:
                  selected_turret.upgrade()
                  world.money -= c.UPGRADE_COST
        else:
          pygame.draw.rect(screen, "dodgerblue", (200, 200, 400, 200), border_radius = 30)
          if game_outcome == -1:
            draw_text("GAME OVER", large_font, "grey0", 310, 230)
          elif game_outcome == 1:
            draw_text("YOU WIN!", large_font, "grey0", 315, 230)
          #restart
          if restart_button.draw(screen):
            game_over = False
            level_started = False
            placing_turrets = False
            selected_turret = None
            last_enemy_spawn = pygame.time.get_ticks()
            world = World(world_data, map_image)
            world.process_data()
            world.process_enemies()
            #empty groups
            enemy_group.empty()
            turret_group.empty()
        #event handler
        for event in pygame.event.get():
          if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            #regarde si la souris est dans la page 
            if mouse_pos[0] < c.SCREEN_WIDTH and mouse_pos[1] < c.SCREEN_HEIGHT:
              #clear les tourelles selectionnée
              selected_turret = None
              clear_selection()
              if placing_turrets == True:
                #regarde si tu as la thune pour acheter une tourelle
                if world.money >= c.BUY_COST:
                  create_turret(mouse_pos)
              else:
                selected_turret = select_turret(mouse_pos)
        pygame.display.flip()

    pygame.display.update()

pygame.quit()