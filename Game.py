import pygame
import math

FPS = 60

BlockWidth = 25
BlockHeight = 25

startX = 1*BlockWidth
startY = -2*BlockHeight
playerW = 1*BlockWidth
playerH = 2*BlockHeight
PlayerHealth = 100

enemyW = 1*BlockWidth
enemyH = 2*BlockHeight
enemyHealth = 50

bulletH = 5
bulletW = 5

bullets = []
walls = []
ladders = []
doors = []
enemies = []


# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

class Kamera:
    def __init__(self, width, height):
        self.kamera = pygame.Rect(0, 0, width, height)
    
    def update(self, target):
        self.kamera.x = target.PosX - 1280 / 2 + target.Width / 2
        self.kamera.y = target.PosY - 720 / 2 + target.Height / 2

    def apply(self, rect):
        return pygame.Rect(rect.x - self.kamera.x, rect.y - self.kamera.y, rect.width, rect.height)

class Entity:
    def __init__(self, PosX, PosY, Width, Height, health, TidSidenSidsteSkud):
        self.PosX = PosX
        self.PosY = PosY
        self.Width = Width
        self.Height = Height
        self.health = health
        self.TidSidenSidsteSkud = TidSidenSidsteSkud
        self.skade = 25
    
    def GetRect(self):
        return pygame.Rect(self.PosX, self.PosY, self.Width, self.Height)
    
    def Hit(self, bullets):
        for bullet in bullets:
            
            if bullet.shooter == self:
                continue  # går videre til næste bullet hvis bulleten er skudt af samme person som der checkes

            bulletRect = bullet.GetRect()

            if bulletRect.colliderect(self.GetRect()):
                self.health -= self.skade
                bullet.active = False
        
        if self.health <= 0:
            if isinstance(self, Player): # tjekker om self er et objekt af Player klassen
                print("Du døde, og tabte derfor spillet")
                pygame.quit()
                exit()

            elif isinstance(self, Enemy): # tjekker om self er et objekt af Enemy klassen
                enemies.remove(self)

class Player(Entity):
    def __init__(self, PosX, PosY, Width, Height, health, TidSidenSidsteSkud ):
        super().__init__(PosX, PosY, Width, Height, health, TidSidenSidsteSkud)

        self.movespeed = 5
        self.fallStrength = 0.5
        self.verticalVelocity = 0
        self.jumpStrength = self.fallStrength*17.5
        self.jumpCount = 0
        self.canJump = True
    
    def draw(self, kamera):
        pygame.draw.rect(screen,"aqua", kamera.apply(pygame.Rect(self.PosX, self.PosY, self.Width, self.Height)))

    def movement(self):

        keys = pygame.key.get_pressed()
        if keys[pygame.K_d]:
             self.PosX += self.movespeed

        if keys[pygame.K_a]:
            self.PosX -= self.movespeed

        if keys[pygame.K_LCTRL] :
            if self.Height > BlockHeight:
                self.Height = self.Height/2
                self.PosY += BlockHeight

        elif self.Height < playerH:
            self.Height = 2*BlockHeight
            self.PosY -= BlockHeight

        if keys[pygame.K_w] and self.jumpCount < 1 and self.canJump == True:
            self.verticalVelocity = -self.jumpStrength
            self.jumpcount = 1
            self.canJump = False
    
    def Gravity(self):
        self.verticalVelocity = self.verticalVelocity + self.fallStrength
        self.PosY = self.PosY + self.verticalVelocity

class Enemy(Entity):
    def __init__(self, PosX, PosY, Width, Height, health, TidSidenSidsteSkud, Player):
        super().__init__(PosX, PosY, Width, Height, health, TidSidenSidsteSkud)
        self.Player = Player
    
    def draw(self, kamera):
        pygame.draw.rect(screen, "green", kamera.apply(pygame.Rect(self.PosX, self.PosY, self.Width, self.Height)))

    def PlayerDetect(self, Kamera, Player):
        Range = 250
        if (Player.PosX + Player.Width > self.PosX - Range and 
            Player.PosX < self.PosX + Range and 
            Player.PosY + Player.Height > self.PosY - Range and
            Player.PosY - Player.Height < self.PosY + Range):
            shoot(Player, self, "player", Kamera)

class Object:
    def __init__(self, X, Y, Width, Height):
        self.X = X
        self.Y = Y
        self.Width = Width
        self.Height = Height
    
    def GetRect(self):
        return pygame.Rect(self.X, self.Y, self.Width, self.Height)

class Wall(Object):
    def __init__(self, X, Y, Width, Height):
        super().__init__(X, Y, Width, Height)
    
    def draw(self, kamera):
        pygame.draw.rect(screen,"white", kamera.apply(pygame.Rect(self.X, self.Y, self.Width, self.Height)))

class Ladder(Object):
    def __init__(self, X, Y, Width, Height):
        super().__init__(X, Y, Width, Height)
    
    def draw(self, kamera):
        pygame.draw.rect(screen,"grey", kamera.apply(pygame.Rect(self.X, self.Y, self.Width, self.Height)))

class Door(Object):
    def __init__(self, X, Y, Width, Height):
        super().__init__(X, Y, Width, Height)
    
    def draw(self, kamera):
        pygame.draw.rect(screen,"chocolate4", kamera.apply(pygame.Rect(self.X, self.Y, self.Width, self.Height)))

class Bullet:
    def __init__(self, BulletX, BulletY, retningX, retningY, shooter):
        self.BulletX = BulletX
        self.BulletY = BulletY
        self.retningX = retningX
        self.retningY = retningY
        self.shooter = shooter
        
        self.BulletWidth = bulletW
        self.BulletHeight = bulletH
        self.hastighed = 5

        self.traveled = 0
        self.maxDistance = 300
        self.active = True

    def draw(self, kamera):
        pygame.draw.rect(screen,"red", kamera.apply(pygame.Rect(self.BulletX, self.BulletY, self.BulletWidth, self.BulletHeight)))
    
    def GetRect(self):
        return pygame.Rect(self.BulletX, self.BulletY, self.BulletWidth, self.BulletHeight)

    def opdater(self):
        self.BulletX += self.retningX * self.hastighed
        self.BulletY += self.retningY * self.hastighed
        self.traveled += self.hastighed

def ColisionHandler(Player, walls, ladders):
    PlayerRect = Player.GetRect()
    
    for Wall in walls:
        WallRect = Wall.GetRect()

        if PlayerRect.colliderect(WallRect):
            forskelX = PlayerRect.centerx - WallRect.centerx # forskel mellem midten af spilleren og midten af væggen, er den negativ er man venstre for og positiv højre for 
            forskelY = PlayerRect.centery - WallRect.centery # forskel mellem midten af spilleren og midten af væggen, er den negativ er man over væggen og positiv under væggen
            overlapX = (PlayerRect.width + WallRect.width) / 2 - abs(forskelX) # hvor meget de overlapper vandret
            overlapY = (PlayerRect.height + WallRect.height) / 2 - abs(forskelY) # hvor meget de overlapper lodret

            if overlapX < overlapY:
                if forskelX > 0: # til højre for kassen
                    Player.PosX = WallRect.right
                else: # til venstre for kassen
                    Player.PosX = WallRect.left - PlayerRect.width
            else:    
                if forskelY > 0: # under kassen
                    Player.PosY = WallRect.bottom
                    Player.verticalVelocity = 0
                else: # over kassen
                    Player.PosY = WallRect.top - PlayerRect.height
                    Player.verticalVelocity = 0
                    Player.jumpCount = 0
                    Player.canJump = True
    
    for Ladder in ladders:
        LadderRect = Ladder.GetRect()
        if PlayerRect.colliderect(LadderRect):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                Player.verticalVelocity = -3.5

    for Door in doors:
        DoorRect = Door.GetRect()
        if PlayerRect.colliderect(DoorRect):
            print("Du nåede til udgangen uden at dø, og klarede derfor banen!")
            pygame.quit()
            exit()

def shoot(player, shooter, Target, kamera):
    Tick = pygame.time.get_ticks()
    cd = 300

    if Tick - shooter.TidSidenSidsteSkud < cd:
        return
    
    PlayerRect = player.GetRect()

    if Target == "mouse" and shooter == player:
        ShooterRect = shooter.GetRect()
        TargetX, TargetY = pygame.mouse.get_pos()
        shooterX, shooterY = -(kamera.kamera.x) + (ShooterRect.centerx), -(kamera.kamera.y) + (ShooterRect.centery)

    elif Target == "player" and shooter != player:
        ShooterRect = shooter.GetRect() 
        TargetX, TargetY = PlayerRect.centerx, PlayerRect.centery
        shooterX, shooterY = ShooterRect.centerx, ShooterRect.centery
    
    if Tick - shooter.TidSidenSidsteSkud >= cd:
        
        xÆndring = TargetX - shooterX
        yÆndring = TargetY - shooterY 
        L = math.hypot(xÆndring, yÆndring)
        retningX = xÆndring/L
        retningY = yÆndring/L

        newbullet = Bullet(ShooterRect.centerx, ShooterRect.centery, retningX, retningY, shooter)
        newbullet.draw(kamera)
        bullets.append(newbullet)
        shooter.TidSidenSidsteSkud = Tick

def bulletRemover(bullet):
    bulletRect = bullet.GetRect()
    for Wall in walls:
        wallRect = Wall.GetRect()
        if bulletRect.colliderect(wallRect) or bullet.traveled >= bullet.maxDistance:
            bullet.active = False

#currentPlayer = Player(startX, startY, playerW, playerH, moveSpeed, fallStrength, Playerhealth)
currentPlayer = Player(startX,startY, playerW, playerH, PlayerHealth, 0)

kamera = Kamera(1280, 720)

# start etage
walls.append(Wall(0,0,1000,25)) # bund
walls.append(Wall(-25,-275,25,300)) # venstre væg
walls.append(Wall(1000,-275,25,300)) # højre væg
ladders.append(Ladder(925,-300,50,300)) # stige 1
walls.append(Wall(75,-275,25,250))
walls.append(Wall(150, -25, 25, 25))
walls.append(Wall(275,-50,25,50))
walls.append(Wall(450,-100,25,100))
enemies.append(Enemy(450,-150,enemyW,enemyH,enemyHealth,0,currentPlayer))
walls.append(Wall(550,-25,25,25))
walls.append(Wall(625,-100,25,100))
walls.append(Wall(625,-275,25,150))
walls.append(Wall(750,-50,25,50))
walls.append(Wall(875,-100,25,100))
walls.append(Wall(875,-275,25,125))

# etage 1
walls.append(Wall(0,-275,925,25)), walls.append(Wall(975,-275,25,25)) # bund
walls.append(Wall(-25, -550, 25, 300)) # venstre væg
walls.append(Wall(1000,-550,25,300)) # højre væg
ladders.append(Ladder(25,-575,50,300)) # stige 2
 
walls.append(Wall(775,-550,225,150))
walls.append(Wall(750,-400,50,25))
enemies.append(Enemy(750,-450,enemyW,enemyH,enemyHealth,0,currentPlayer))
walls.append(Wall(600,-550,25,250))
walls.append(Wall(350, -325,25,50))
enemies.append(Enemy(350,-375,enemyW,enemyH,enemyHealth,0,currentPlayer))
walls.append(Wall(200,-375,25,125))
walls.append(Wall(75,-550,25,175))
# etage 2
walls.append(Wall(75,-550,925,25)), walls.append(Wall(0,-550,25,25)) # bund
walls.append(Wall(-25, -825, 25, 300)) # venstre væg
walls.append(Wall(1000,-825,25,300)) # højre væg
ladders.append(Ladder(925,-850,50,300)) # stige 3

walls.append(Wall(100, -550, 25, 25))
walls.append(Wall(200, -600, 25, 75))
walls.append(Wall(300, -675, 125, 25))
enemies.append(Enemy(350,-600,enemyW,enemyH,enemyHealth,0,currentPlayer))
walls.append(Wall(500, -600, 25, 75))
walls.append(Wall(600, -600, 100, 25))
enemies.append(Enemy(625, -650, enemyW, enemyH, enemyHealth, 0, currentPlayer))
walls.append(Wall(800, -650, 75, 25))
enemies.append(Enemy(825, -700, enemyW, enemyH, enemyHealth, 0, currentPlayer))

# etage 3
walls.append(Wall(0,-825,925,25)), walls.append(Wall(975,-825,25,25)) # bund
walls.append(Wall(-25, -1100, 25, 300)) # venstre væg
walls.append(Wall(1000,-1100,25,300)) # højre væg
ladders.append(Ladder(25,-1125,50,300)) # stige 4

walls.append(Wall(100, -900, 150, 25))
enemies.append(Enemy(125, -950, enemyW, enemyH, enemyHealth, 0, currentPlayer))
walls.append(Wall(350, -925, 100, 25))
walls.append(Wall(375,-900,50,75))
enemies.append(Enemy(475,-875,enemyW,enemyH,enemyHealth,0,currentPlayer))
walls.append(Wall(575, -900, 125, 25))
walls.append(Wall(575,-1000,25,100))
walls.append(Wall(600,-950,25,25))
enemies.append(Enemy(625, -950, enemyW, enemyH, enemyHealth, 0, currentPlayer))
walls.append(Wall(675,-900,25,75))
walls.append(Wall(800, -875, 100, 50))

# etage 4
walls.append(Wall(75,-1100,925,25)), walls.append(Wall(0,-1100,25,25)) # bund
walls.append(Wall(-25, -1250, 25, 175)) # venstre væg
walls.append(Wall(250,-1250,25,175)) # højre væg
walls.append(Wall(0,-1250,250,25)) # tag
doors.append(Door(175,-1175,50,75)) # win door

# Kører spillet i loop
while running:
    #gør så man kan lukke spillet med krydset i hjørnet
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    #Funktioner der skal køres:
    for wall in walls:
        wall.draw(kamera)
    for ladder in ladders:
        ladder.draw(kamera)
    for enemy in enemies:
        enemy.draw(kamera)
        enemy.PlayerDetect(kamera, currentPlayer)
        enemy.Hit(bullets)
    for Door in doors:
        Door.draw(kamera)
    for bullet in bullets:
        bullet.opdater()
        bullet.draw(kamera)
        bulletRemover(bullet)
        if bullet.active == False:
            bullets.remove(bullet)

    kamera.update(currentPlayer)
    currentPlayer.movement()
    currentPlayer.Gravity()
    currentPlayer.Hit(bullets)
    ColisionHandler(currentPlayer, walls, ladders)
    currentPlayer.draw(kamera)
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        shoot(currentPlayer, currentPlayer, "mouse", kamera)

    #--------------------------

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(FPS)  # limits FPS to 60

pygame.quit()