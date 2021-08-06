import pygame,sys,os,random,csv
#Starting the game
pygame.init()
clock=pygame.time.Clock()
#Sprite groups
bullet_group=pygame.sprite.Group()
grenade_group=pygame.sprite.Group()
explosion_group=pygame.sprite.Group()
enemy_group=pygame.sprite.Group()
item_box_groups=pygame.sprite.Group()
decoration_group=pygame.sprite.Group()
water_group=pygame.sprite.Group()
exit_group=pygame.sprite.Group()
#The screen
SCREEN_WIDTH=800
SCREEN_HEIGHT=int(SCREEN_WIDTH*0.8)
screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")
#game variables
GRAVITY=0.75
SCROLL_THRESH=200
ROWS=16
COLS=150
TILE_SIZE=SCREEN_HEIGHT//ROWS
TILE_TYPES=21
screen_scroll=0
bg_scroll=0
level=1
#Player action variables
moving_left=False
moving_right=False
shoot=False
clicked=False
grenade=False
grenade_thrown=False
ai_moving_right=False
ai_moving_left=False
#images
img_list=[]
for x in range(TILE_TYPES):
    img=pygame.image.load(f"Ssg/img/Tiles/{x}.png")
    img=pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
    img_list.append(img)
bullet_img=pygame.image.load("Ssg/img/icons/bullet.png").convert_alpha()
grenade_img=pygame.image.load("Ssg/img/icons/grenade.png").convert_alpha()
healthbox_img=pygame.image.load("Ssg/img/icons/health_box.png").convert_alpha()
grenadebbox_img=pygame.image.load("Ssg/img/icons/grenade_box.png").convert_alpha()
ammobox_img=pygame.image.load("Ssg/img/icons/ammo_box.png").convert_alpha()
item_boxes={
    "Health":healthbox_img,
    "Grenade":grenadebbox_img,
    "Ammo":ammobox_img
}
pine1_img=pygame.image.load("Scrollingle/Background/pine1.png").convert_alpha()
pine2_img=pygame.image.load("Scrollingle/Background/pine2.png").convert_alpha()
mountain_img=pygame.image.load("Scrollingle/Background/mountain.png").convert_alpha()
sky_img=pygame.image.load("Scrollingle/Background/sky_cloud.png").convert_alpha()
#define a font
font=pygame.font.SysFont("Futura",30)
#draw txts for ammo,health,grenade
def draw_text(text,font,text_col,x,y):
    img=font.render(text,True,text_col)
    screen.blit(img,(x,y))
#Classes
class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed,ammo,grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive=True
        self.char_type=char_type
        self.jump=False
        self.in_air=True
        self.health=100
        self.max_health=self.health
        self.shoot_cooldown=0
        self.ammo=ammo
        self.grenades=grenades
        self.speed=speed
        self.direction=1
        self.vel_y=0
        self.flip=False
        self.animation_list=[]
        self.index=0
        self.action=0
        self.update_time=pygame.time.get_ticks()
        #ai variables
        self.move_counter=0
        self.vision=pygame.Rect(0,0,150,20)
        self.idling=False
        self.idling_counter=0
        #load the images for the player
        animation_types=["idle","Run","Jump","Death"]
        temp_list=[]
        for animation in animation_types: 
            #temporary reset
            temp_list=[]
            num_frames=len(os.listdir(f"Ssg/img/{self.char_type}/{animation}"))
            for i in range(num_frames):
                img=pygame.image.load(f"Ssg/img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img=pygame.transform.scale(img,(int(img.get_width()*scale),int(img.get_height()*scale))).convert_alpha()
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image=self.animation_list[self.action][self.index]
        self.rect=self.image.get_rect()
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.rect.center=(x,y)
    def update(self):
        self.update_animation()
        self.check_for_alive()
        if self.shoot_cooldown>0:
            self.shoot_cooldown-=1
    def move(self,moving_left,moving_right):
        screen_scroll=0
        dx=0
        dy=0
        #Movements
        if moving_left:
            dx=-self.speed
            self.flip=True
            self.direction=-1
        if moving_right:
            dx=self.speed
            self.flip=False
            self.direction=1
        #Jumping
        if self.jump and self.in_air==False:
            self.vel_y=-11
            self.jump=False
            self.in_air=True
        self.vel_y+=GRAVITY
        if self.vel_y>10:
            self.vel_y=10
        dy+=self.vel_y
        #Collision with the line(temporary)
        # if self.rect.bottom+dy>300:
        #     dy=300-self.rect.bottom
        #     self.in_air=False
        #Collision detection(perm)
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                dx=0
                if self.char_type=="enemy":
                    self.direction*=-1
                    self.move_counter=0
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                if self.vel_y<0:
                    self.vel_y=0
                    dy=tile[1].bottom-self.rect.top
                elif self.vel_y>=0:
                    self.vel_y=0
                    self.in_air=False
                    dy=tile[1].top-self.rect.bottom
        #check if going of edges
        if self.char_type=="player":
            if self.rect.left+dx<0 or self.rect.right+dx>SCREEN_WIDTH:
                dx=0
        #Doing the movement
        self.rect.x+=dx
        self.rect.y+=dy
        if self.char_type=="player":
            if (self.rect.right>SCREEN_WIDTH-SCROLL_THRESH and bg_scroll<(TILE_SIZE*world.level_length)-SCREEN_WIDTH)\
                or (self.rect.left<SCROLL_THRESH and bg_scroll>abs(dx)):
                self.rect.x-=dx
                screen_scroll=-dx
        return screen_scroll
    def ai(self):
        if player.alive and self.alive:
            if random.randint(0,300)==1 and self.idling==False:
                self.update_action(0)
                self.idling=True
                self.idling_counter=50
            if self.vision.colliderect(player):
                self.update_action(0)
                self.shoot()
            else:
                if self.idling==False:
                    if self.direction==1:
                        ai_moving_right=True
                    else:
                        ai_moving_right=False
                    ai_moving_left=not ai_moving_right
                    self.move(ai_moving_left,ai_moving_right)
                    self.update_action(1)
                    self.move_counter+=1
                    self.vision.center=(self.rect.centerx+75*self.direction,self.rect.centery)
                    if self.move_counter>TILE_SIZE:
                        self.direction*=-1
                        self.move_counter*=-1
                else:
                    self.idling_counter-=1
                    if self.idling_counter<=0:
                        self.idling=False
        self.rect.x+=screen_scroll
    def shoot(self):
        if self.shoot_cooldown==0 and self.ammo>0:
            bullet=Bullet(self.rect.centerx+(0.75*self.rect.size[0])*self.direction,self.rect.centery,self.direction)
            bullet_group.add(bullet)
            self.shoot_cooldown=20
            self.ammo-=1
    def update_animation(self):
        Animation_cooldown=100
        self.image=self.animation_list[self.action][self.index]
        if pygame.time.get_ticks()-self.update_time>Animation_cooldown:
            self.index+=1
            self.update_time=pygame.time.get_ticks()
        if self.index>=len(self.animation_list[self.action]):
            if self.action==3:
                self.index=len(self.animation_list[self.action])-1
            else:
                self.index=0
    def check_for_alive(self):
        if self.health<=0:
            self.health=0
            self.speed=0
            self.alive=False
            self.update_action(3)
    def update_action(self,new_action):
        #Check to see if new action!=previous_action
        if new_action!=self.action:
            self.action=new_action
            self.index=0
            self.update_time=pygame.time.get_ticks()
    def draw(self):
        screen.blit(pygame.transform.flip(self.image,self.flip,False),self.rect)
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed=10
        self.image=bullet_img
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.direction=direction
    def update(self):
        self.rect.x+=(self.direction*self.speed)+screen_scroll
        if self.rect.right<0 or self.rect.left>SCREEN_WIDTH:
            self.kill()
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                self.kill()
                player.health-=5
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False) and enemy.alive:
                if enemy.alive:
                    enemy.health-=25
                    print(enemy.health)
                    self.kill()
class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer=100
        self.vel_y=-11
        self.speed=10
        self.image=grenade_img
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.width=self.image.get_width()
        self.height=self.image.get_height()
        self.direction=direction
    def update(self):
        self.vel_y+=GRAVITY
        dx=self.speed*self.direction+screen_scroll
        dy=self.vel_y
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                self.direction=self.direction*-1
                dx=self.direction+self.speed
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                self.speed=0
                if self.vel_y<0:
                    self.vel_y=0
                    dy=tile[1].bottom-self.rect.top
                elif self.vel_y>=0:
                    self.vel_y=0
                    self.in_air=False
                    dy=tile[1].top-self.rect.bottom
        self.rect.x+=dx
        self.rect.y+=dy
        #Explosion timer
        self.timer-=1
        if self.timer<0:
            self.kill()
            explosion=Explosion(self.rect.x,self.rect.y+5,2)
            explosion_group.add(explosion)
            #do kill
            if abs(self.rect.centerx-player.rect.centerx)<TILE_SIZE*2 and\
                abs(self.rect.centery-player.rect.centery)<TILE_SIZE*2:
                player.health-=50
            for enemy in enemy_group:
                if abs(self.rect.centerx-enemy.rect.centerx)<TILE_SIZE*2 and\
                    abs(self.rect.centery-enemy.rect.centery)<TILE_SIZE*2:
                    enemy.health-=50
class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)
        self.images=[]
        for num in range(1,6):
            img=pygame.image.load(f"Ssg/img/explosions/exp{num}.png").convert_alpha()
            img=pygame.transform.scale(img,(int(img.get_width()*scale),int(img.get_height()*scale))).convert_alpha()
            self.images.append(img)
        self.index=0
        self.image=self.images[self.index]
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)
        self.counter=0
    def update(self):
        self.rect.x+=screen_scroll
        EXPLOSION_SPEED=4
        self.counter+=1
        if self.counter>=EXPLOSION_SPEED:
            self.counter=0
            self.index+=1
            if self.index>=len(self.images):
                self.kill()
            else:
                self.image=self.images[self.index]
class Decoration(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=img
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x+=screen_scroll
class Water(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=img
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x+=screen_scroll
class Exit(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=img
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x+=screen_scroll
class World():
    def __init__(self):
        self.obstacle_list=[]
    def process_data(self,data):
        self.level_length=len(data[0])
        for y,row in enumerate(data):
            for x,tile in enumerate(row):
                if tile>=0:
                    img=img_list[tile]
                    img_rect=img.get_rect()
                    img_rect.x=x*TILE_SIZE
                    img_rect.y=y*TILE_SIZE
                    tile_data=(img,img_rect)
                    if tile>=0 and tile<=8:
                        self.obstacle_list.append(tile_data)
                    elif tile>=9 and tile<=10:
                        water=Water(img,x*TILE_SIZE,y*TILE_SIZE)
                        water_group.add(water)
                    elif tile>=11 and tile<=14:
                        decoration=Decoration(img,x*TILE_SIZE,y*TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile==15:
                        player=Soldier("player",x*TILE_SIZE,y*TILE_SIZE,1.65,4,20,5)
                        healthbar=Healthbar(10,10,player.health,player.health)
                    elif tile==16:
                        enemy=Soldier("enemy",x*TILE_SIZE,y*TILE_SIZE,1.65,2,20,0)
                        enemy_group.add(enemy)
                    elif tile==17:
                        itembox=ItemBox("Ammo",x*TILE_SIZE,y*TILE_SIZE)
                        item_box_groups.add(itembox)
                    elif tile==18:
                        itembox=ItemBox("Grenade",x*TILE_SIZE,y*TILE_SIZE)
                        item_box_groups.add(itembox)
                    elif tile==19:
                        itembox=ItemBox("Health",x*TILE_SIZE,y*TILE_SIZE)
                        item_box_groups.add(itembox)
                    elif tile==20:
                        exit=Exit(img,x*TILE_SIZE,y*TILE_SIZE)
                        exit_group.add(exit)
        return player,healthbar
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0]+=screen_scroll
            screen.blit(tile[0],tile[1])
class ItemBox(pygame.sprite.Sprite):
    def __init__(self,item_type,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type=item_type
        self.image=item_boxes[self.item_type]
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE//2,y+(TILE_SIZE-self.image.get_height()))
    def update(self):
        self.rect.x+=screen_scroll
        if pygame.sprite.collide_rect(self,player):
            if self.item_type=="Health":
                if player.health+25>=100:
                    player.health=100
                elif player.health+25<=100:
                    player.health+=25
            elif self.item_type=="Ammo":
                player.ammo+=5
            elif self.item_type=="Grenade":
                player.grenades+=2
            self.kill()
class Healthbar():
    def __init__(self,x,y,health,max_health):
        self.x=x
        self.y=y
        self.health=health
        self.max_health=max_health
    def draw(self,health):
        self.health=health
        pygame.draw.rect(screen,BLACK,(self.x-2,self.y-2,154,24))
        pygame.draw.rect(screen,RED,(self.x,self.y,150,20))
        ratio=self.health / self.max_health
        pygame.draw.rect(screen,GREEN,(self.x,self.y,150*ratio,20))
#define colors
BG=(144,201,120)
RED=(255,0,0)
WHITE=(255,255,255)
GREEN=(0,255,0)
BLACK=(0,0,0)
#Defs
def pyquit():
    pygame.quit()
    sys.exit()
def draw_bg():
    screen.fill(BG)
    width=sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img,((x*width)-bg_scroll*0.5,0))
        screen.blit(mountain_img,((x*width)-bg_scroll*0.6,SCREEN_HEIGHT-mountain_img.get_height()-300))
        screen.blit(pine1_img,((x*width)-bg_scroll*0.7,SCREEN_HEIGHT-pine1_img.get_height()-150))
        screen.blit(pine2_img,((x*width)-bg_scroll*0.8,SCREEN_HEIGHT-pine2_img.get_height()))
#Variables
fps=60
#World data
world_data=[]
for row in range(ROWS):
    r=[-1]*COLS
    world_data.append(r)
with open("level1_data.csv",newline="") as csvfile:
    reader=csv.reader(csvfile,delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y]=int(tile)
world=World()
player,healthbar=world.process_data(world_data)
#the game loop
run=True
while run:
    clock.tick(fps)
    draw_bg()
    world.draw()
    #show player health
    healthbar.draw(player.health)
    draw_text(f"Ammo: ",font,WHITE,10,35)
    for x in range(player.ammo):
        screen.blit(bullet_img,(90+(x*10),40))
    draw_text(f"Grenade: ",font,WHITE,10,60)
    for x in range(player.grenades):
        screen.blit(grenade_img,(105+(x*15),65))
    player.update()
    player.draw()
    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()
    bullet_group.update()
    grenade_group.update()
    explosion_group.update()
    item_box_groups.update()
    decoration_group.update()
    exit_group.update()
    water_group.update()
    bullet_group.draw(screen)
    grenade_group.draw(screen)
    explosion_group.draw(screen)
    item_box_groups.draw(screen)
    decoration_group.draw(screen)
    exit_group.draw(screen)
    water_group.draw(screen)
    if player.alive:
        if shoot:
            player.shoot()
        elif grenade and grenade_thrown==False and player.grenades>0:
            grenade=Grenade(player.rect.centerx+(player.rect.size[0]*0.5),\
                           player.rect.top,player.direction)
            grenade_group.add(grenade)
            grenade_thrown=True
            player.grenades-=1
        if player.in_air:
            player.update_action(2)
        elif moving_left or moving_right:
            player.update_action(1)
        else:
            player.update_action(0)
        screen_scroll=player.move(moving_left,moving_right)
        bg_scroll-=screen_scroll
    for event in pygame.event.get():
        #quit game
        if event.type==pygame.QUIT:
            pyquit()
        #Keyboard button presses
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_a:
                moving_left=True
            if event.key==pygame.K_d:
                moving_right=True
            if event.key==pygame.K_ESCAPE:
                pyquit()
            if event.key==pygame.K_SPACE and player.alive:
                player.jump=True
            if event.key==pygame.K_q:
                grenade=True
            if event.key==pygame.K_LSHIFT:
                player.speed=5
        #Keyboard button releases
        if event.type==pygame.KEYUP:
            if event.key==pygame.K_a:
                moving_left=False
            if event.key==pygame.K_d:
                moving_right=False
            if event.key==pygame.K_q:
                grenade=False
                grenade_thrown=False
            if event.key==pygame.K_LSHIFT:
                player.speed=4
        if pygame.mouse.get_pressed()[0]==1:
            shoot=True
        if pygame.mouse.get_pressed()[0]==0:
            shoot=False
    pygame.display.update()