import random
import sys
import os
import pygame
from pygame.locals import *

# Global Variables
FPS = 45
SCREENWIDTH = 289
SCREENHEIGHT = 511
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
FPSCLOCK = pygame.time.Clock()

GAME_SPRITES = {}
GAME_SOUNDS = {}

# File Paths
PLAYER = 'gallery/sprites/bird.png'
BACKGROUND = 'gallery/sprites/background.png'
PIPE = 'gallery/sprites/pipe.png'
MESSAGE = 'gallery/sprites/message.png'
BASE = 'gallery/sprites/base.png'
GAME_OVER = 'gallery/sprites/gameover.png'  # Added Game Over image

# Audio Paths
HIT_SOUND = 'gallery/audio/hit.wav'
WING_SOUND = 'gallery/audio/wing.wav'


def load_image(path):
    """Load image safely and handle missing files."""
    if not os.path.exists(path):
        print(f"Error: File {path} not found!")
        sys.exit()
    return pygame.image.load(path).convert_alpha()


def load_sound(path):
    """Load sound safely and handle missing files."""
    if not os.path.exists(path):
        print(f"Warning: Sound file {path} not found! Sound will be disabled.")
        return None
    return pygame.mixer.Sound(path)


def welcomeScreen():
    """Display the welcome screen before starting the game."""
    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.13)
    basex = 0

    while True:
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return
        FPSCLOCK.tick(FPS)


def mainGame():
    """Main game loop."""
    score = 0
    font = pygame.font.Font(None, 36)  # Font for score display
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENWIDTH / 2)
    basex = 0

    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    upperPipes = [{'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
                  {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']}]

    lowerPipes = [{'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
                  {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']}]

    pipeVelX = -4
    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1
    playerFlapAccv = -8
    playerFlapped = False

    while True:
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    if GAME_SOUNDS['wing']:
                        GAME_SOUNDS['wing'].play()

        if isCollide(playerx, playery, upperPipes, lowerPipes):
            gameOverScreen(score)
            return

        playerVelY = min(playerVelY + playerAccY, playerMaxVelY) if not playerFlapped else playerVelY
        playerFlapped = False
        playery = min(playery + playerVelY, GROUNDY - GAME_SPRITES['player'].get_height())

        for pipe in upperPipes + lowerPipes:
            pipe['x'] += pipeVelX

        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])
            score += 1  # Increment score when passing pipes

        for pipe in upperPipes + lowerPipes:
            SCREEN.blit(GAME_SPRITES['pipe'][0 if pipe in upperPipes else 1], (pipe['x'], pipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))

        # Display score
        score_surface = font.render(str(score), True, (255, 255, 255))
        SCREEN.blit(score_surface, (SCREENWIDTH / 2, 50))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def isCollide(playerx, playery, upperPipes, lowerPipes):
    """Check if the player collides with a pipe or the ground."""
    if playery > GROUNDY - 25 or playery < 0:
        return True

    for pipe in upperPipes + lowerPipes:
        if (playerx + GAME_SPRITES['player'].get_width() > pipe['x']) and \
           (playerx < pipe['x'] + GAME_SPRITES['pipe'][0].get_width()) and \
           ((pipe in upperPipes and playery < pipe['y'] + GAME_SPRITES['pipe'][0].get_height()) or 
            (pipe in lowerPipes and playery + GAME_SPRITES['player'].get_height() > pipe['y'])):
            return True
    return False


def getRandomPipe():
    """Generate positions of upper and lower pipes."""
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    return [{'x': pipeX, 'y': -y1}, {'x': pipeX, 'y': y2}]


def gameOverScreen(score):
    """Display Game Over screen."""
    SCREEN.blit(GAME_SPRITES['gameover'], (50, 150))
    font = pygame.font.Font(None, 40)
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    SCREEN.blit(text, (100, 250))
    pygame.display.update()
    pygame.time.delay(2000)
    welcomeScreen()


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption('Flappy Bird')

    GAME_SPRITES['player'] = load_image(PLAYER)
    GAME_SPRITES['background'] = load_image(BACKGROUND)
    GAME_SPRITES['pipe'] = (pygame.transform.rotate(load_image(PIPE), 180), load_image(PIPE))
    GAME_SPRITES['message'] = load_image(MESSAGE)
    GAME_SPRITES['base'] = load_image(BASE)
    GAME_SPRITES['gameover'] = load_image(GAME_OVER)

    GAME_SOUNDS['hit'] = load_sound(HIT_SOUND)
    GAME_SOUNDS['wing'] = load_sound(WING_SOUND)

    while True:
        welcomeScreen()
        mainGame()
