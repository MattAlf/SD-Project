import pygame, random, sys
from pygame.locals import *

WINDOWWIDTH = 600
WINDOWHEIGHT = 600
TEXTCOLOR = (0, 0, 0)
BACKGROUNDCOLOR = (255, 255, 255)
FPS = 60
BADDIEMINSIZE = 10
BADDIEMAXSIZE = 40
BADDIEMINSPEED = 1
BADDIEMAXSPEED = 8
ADDNEWBADDIERATE = 30
PLAYERMOVERATE = 5
ADDPLATEFORMERATE = 20
PLATEFORMHIGH = 10
PLATEFORMLARGE = 50
PLATEFORMESPEED = 1

def terminate():
    pygame.quit()
    sys.exit()

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: # Pressing ESC quits.
                    terminate()
                return

def playerHasHitBaddie(playerRect, baddies):
    for b in baddies:
        if playerRect.colliderect(b['rect']):
            return False
    return False

def playerIsOnAPlatform(playerRect, platforms):
    for p in platforms: 
        if playerRect.colliderect(p['rect']):
            return True
    return False

def drawText(text, font, surface, x, y):
    textobj = font.render(text, 1, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

# Set up pygame, the window, and the mouse cursor.
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Dodger')
pygame.mouse.set_visible(False)

# Set up gravity + jump
vel_y = 0            # Vertical velocity
gravity = 0.8       # Gravity acceleration
jump_strength = -15   # How strong the jump is
on_ground = False     # Is player on the ground?

# Set up the fonts.
font = pygame.font.SysFont(None, 48)

# Set up sounds.
gameOverSound = pygame.mixer.Sound('gameover.wav')
pygame.mixer.music.load('background.mid')

# Set up images
playerImage = pygame.image.load('player.png')
playerRect = playerImage.get_rect()
baddieImage = pygame.image.load('baddie.png')
plateformeImage = pygame.image.load('plateforme.png')

# Show the "Start" screen.
windowSurface.fill(BACKGROUNDCOLOR)
drawText('Dodger', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
drawText('Press a key to start.', font, windowSurface, (WINDOWWIDTH / 3) - 30, (WINDOWHEIGHT / 3) + 50)
pygame.display.update()
waitForPlayerToPressKey()

topScore = 0
while True:
    # Set up the start of the game.
    baddies = []
    platforms = []
    score = 0
    playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
    moveLeft = moveRight = moveUp = moveDown = False
    reverseCheat = slowCheat = False
    baddieAddCounter = 0
    platformAddCounter = 0
    pygame.mixer.music.play(-1, 0.0)

    num_platforms = 25
    spacing = WINDOWHEIGHT // (num_platforms + 1)  # dynamic spacing

    for i in range(num_platforms):
        x = random.randint(0, WINDOWWIDTH - 50)
        y = WINDOWHEIGHT - (i * spacing) - 50
        newPlatform = {
            'rect': pygame.Rect(x, y, 50, 15),
            'speed': PLATEFORMESPEED,
            'surface': pygame.transform.scale(plateformeImage, (50, 15))
        }
        platforms.append(newPlatform)

    while True: # The game loop runs while the game part is playing.
        score += 1 # Increase score.

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            if event.type == KEYDOWN:
                if event.key == K_z:
                    reverseCheat = True
                if event.key == K_x:
                    slowCheat = True
                if event.key == K_LEFT or event.key == K_a:
                    moveRight = False
                    moveLeft = True
                if event.key == K_RIGHT or event.key == K_d:
                    moveLeft = False
                    moveRight = True
                if event.key == K_UP or event.key == K_w:
                    if on_ground:
                        vel_y = jump_strength
                        on_ground = False

            if event.type == KEYUP:
                if event.key == K_z:
                    reverseCheat = False
                    score = 0
                if event.key == K_x:
                    slowCheat = False
                    score = 0
                if event.key == K_ESCAPE:
                        terminate()

                if event.key == K_LEFT or event.key == K_a:
                    moveLeft = False
                if event.key == K_RIGHT or event.key == K_d:
                    moveRight = False
                if event.key == K_UP or event.key == K_w:
                    moveUp = False
                if event.key == K_DOWN or event.key == K_s:
                    moveDown = False

            if event.type == MOUSEMOTION:
                # If the mouse moves, move the player where to the cursor.
                playerRect.centerx = event.pos[0]
                playerRect.centery = event.pos[1]
        # Add new baddies at the top of the screen, if needed.
        if not reverseCheat and not slowCheat:
            baddieAddCounter += 1
        if baddieAddCounter == ADDNEWBADDIERATE:
            baddieAddCounter = 0
            baddieSize = random.randint(BADDIEMINSIZE, BADDIEMAXSIZE)
            newBaddie = {'rect': pygame.Rect(random.randint(0, WINDOWWIDTH - baddieSize), 0 - baddieSize, baddieSize, baddieSize),
                        'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                        'surface':pygame.transform.scale(baddieImage, (baddieSize, baddieSize)),
                        }

            baddies.append(newBaddie)

        # Add plateforme
        platformAddCounter += 1
        if platformAddCounter == ADDPLATEFORMERATE:
            platformAddCounter = 0 
            platformhigh = PLATEFORMHIGH
            platformlarge = PLATEFORMLARGE
            newPlatform = {'rect': pygame.Rect(random.randint(0, WINDOWWIDTH - platformlarge), 0 - platformhigh, platformlarge, platformhigh),
                        'speed': PLATEFORMESPEED,
                        'surface':pygame.transform.scale(plateformeImage, (platformlarge, platformhigh)),
                        }
            
            platforms.append(newPlatform)

                 # Horizontal movement
        if moveLeft and playerRect.left > 0:
            playerRect.move_ip(-PLAYERMOVERATE, 0)
        if moveRight and playerRect.right < WINDOWWIDTH:
            playerRect.move_ip(PLAYERMOVERATE, 0)

  # Store previous bottom so we can detect if the player moved down onto a platform this frame
        prev_bottom = playerRect.bottom - 1

        # Apply gravity
        vel_y += gravity
        playerRect.y += vel_y

        # Platform collision: only when falling (vel_y > 0) and when the player
        # moved from above the platform to intersect it this frame.
        if vel_y >= PLATEFORMESPEED:
            for p in platforms:
                plat = p['rect']
                # horizontal overlap check
                if playerRect.right > plat.left and playerRect.left < plat.right:
                    # came from above and now intersects the platform top
                    if prev_bottom <= plat.top and playerRect.bottom >= plat.top:
                        playerRect.bottom = plat.top 
                        vel_y = PLATEFORMESPEED
                        on_ground = True
                        break

# Ground collision (bottom of screen)
        if playerRect.bottom >= WINDOWHEIGHT:
            playerRect.bottom = WINDOWHEIGHT
            vel_y = 0
            on_ground = True

        # Move the baddies down.
        for b in baddies:
            if not reverseCheat and not slowCheat:
                b['rect'].move_ip(0, b['speed'])
            elif reverseCheat:
                b['rect'].move_ip(0, -5)
            elif slowCheat:
                b['rect'].move_ip(0, 1)

        # Delete baddies that have fallen past the bottom.
        for b in baddies[:]:
            if b['rect'].top > WINDOWHEIGHT:
                baddies.remove(b)

        #platform apparition
        for p in platforms: 
            p['rect'].move_ip(0, p['speed'])

        for p in platforms: 
            if p['rect'].top > WINDOWHEIGHT:
                platforms.remove(p)

        # Draw the game world on the window.
        windowSurface.fill(BACKGROUNDCOLOR)

        # Draw the score and top score.
        drawText('Score: %s' % (score), font, windowSurface, 10, 0)
        drawText('Top Score: %s' % (topScore), font, windowSurface, 10, 40)

        # Draw the player's rectangle.
        windowSurface.blit(playerImage, playerRect)

        # Draw each baddie.
        for b in baddies:
            windowSurface.blit(b['surface'], b['rect'])

        # Draw each platform.
        for p in platforms: 
            windowSurface.blit(p['surface'], p['rect'])

        pygame.display.update()

        # Check if any of the baddies have hit the player.
        if playerHasHitBaddie(playerRect, baddies):
            if score > topScore:
                topScore = score # set new top score
            break

        mainClock.tick(FPS)

    # Stop the game and show the "Game Over" screen.
    pygame.mixer.music.stop()
    gameOverSound.play()

    drawText('GAME OVER', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
    drawText('Press a key to play again.', font, windowSurface, (WINDOWWIDTH / 3) - 80, (WINDOWHEIGHT / 3) + 50)
    pygame.display.update()
    waitForPlayerToPressKey()

    gameOverSound.stop()
