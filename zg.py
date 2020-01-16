# TODO LIST:
#          Implement shield
#          Death, jumping, etc animation

# TODO FUTURE:
#          Add new characters
#          Allow tethers to be angled and to snap to the wall
#          Allow characters to move out of corners more easily
#          Allow characters to change direction at will
#          Landing lag
#          When a character in hitstun hits a wall, make it bounce off
#          Character stunned when tether collides with an attack
#          Comment
#          Handle character collision
#          Add new stages
#          Re-implement keyboard movement

import time
import pygame.key
import os

from Char import *
from Stage import Stage

WIDTH = 1000  # screen width
HEIGHT = 500  # screen height
WINDOW_OFFSET_X = 5
WINDOW_OFFSET_Y = 30  # no idea why but this works
START_COLOR = (60, 100, 140)  # start screen color
START_TEXT_COLOR = (0, 0, 0)
GAME_COLOR = (0, 50, 100)  # game screen color -- possible to make this stage-dependent
FPS = 60  # 60 frames per second

START_TEXT = 'ZERO GRAVITY'  # text on the start screen
START_TEXT_POS = (WIDTH / 2 - 300, 2.0 / 7 * HEIGHT)  # top left corner of start text
START_TEXT_SIZE = 100  # start screen text will be this big
START_TEXT_RECT_DIMS = (600, 100)  # somewhat arbitrary
BUTTON_TEXT_SIZE = 60  # text on the button will be this big
BUTTON_CORNER = (0.278 * WIDTH, 0.614 * HEIGHT)  # top left corner of start button
BUTTON_DIMS = (0.444 * WIDTH, 0.1 * HEIGHT)  # length and width of start button

SELECT_SCREEN_SPACE = (5, 5)  # distance in between each character/stage on the select screen
SELECT_TEXT_SIZE = 25

NUM_STAGES = 1
STAGE_SELECT_DIMS = (int(0.2 * WIDTH), int(0.26 * HEIGHT))  # length and width of stage select buttons
STAGE_SELECT_WIDTH = STAGE_SELECT_DIMS[0] + SELECT_SCREEN_SPACE[0]
STAGE_SELECT_LEN = STAGE_SELECT_DIMS[1] + SELECT_SCREEN_SPACE[1]
STAGE_IMAGE_SPACE = 5

NUM_CHARS = 1
CHAR_SELECT_DIMS = (0.13 * WIDTH, 0.26 * HEIGHT)  # length and width of character select buttons
CHAR_SELECT_WIDTH = CHAR_SELECT_DIMS[0] + SELECT_SCREEN_SPACE[0]
CHAR_SELECT_LEN = CHAR_SELECT_DIMS[1] + SELECT_SCREEN_SPACE[1]

WALL_WIDTH = 40  # how wide the wall is

X_BUTTON = 0
A_BUTTON = 1
B_BUTTON = 2
Y_BUTTON = 3
L_BUTTON = 4
R_BUTTON = 5
Z_BUTTON = 7
START_BUTTON = 9

CONTROL_STICK_HORIZONTAL = 0
CONTROL_STICK_VERTICAL = 1
C_STICK_VERTICAL = 2
C_STICK_HORIZONTAL = 3

DEAD_ZONE = 0.3
DIAG_DEAD_ZONE = 0.15


# JOYSTICK_DIAG = 0.707

class ZeroGravity:
    def __init__(self):
        self.w = WIDTH
        self.h = HEIGHT

        # there was a variable here called self.def, I'm not sure what it was

        pygame.init()  # start pygame

        # screen is in top left corner
        os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (WINDOW_OFFSET_X, WINDOW_OFFSET_Y)
        self.screen = pygame.display.set_mode((self.w, self.h))  # create the screen
        # self.screen.fill(START_COLOR)  # fill the screen with white
        pygame.display.flip()  # open the screen

        self.chars = []  # list of playable characters
        self.status = 'start screen'  # whether the game is at the start screen, character select screen, or in a game
        self.playChars = []  # list of characters currently playing
        self.clock = pygame.time.Clock()

        self.running = False  # whether the program is running
        self.fps = 0  # frames per second
        # (both of these will be set in the mainloop function)

        rect = pygame.Rect(BUTTON_CORNER, BUTTON_DIMS)
        self.startButton = TextButton('START', BUTTON_TEXT_SIZE, START_TEXT_COLOR, rect, self)

        self.wallWidth = WALL_WIDTH
        # TODO: config file?
        self.walls = [[pygame.Rect(0, 0, WALL_WIDTH, self.h), pygame.Rect(0, 0, self.w, WALL_WIDTH),
                       pygame.Rect(self.w - WALL_WIDTH, 0, WALL_WIDTH, self.h),
                       pygame.Rect(0, self.h - WALL_WIDTH, self.w, WALL_WIDTH)]]
        self.stage = Stage(self.walls[0], self)

        self.chars = ['Alucard']
        self.charButtons = []
        start_x = 0.5 * WIDTH - 0.5 * CHAR_SELECT_DIMS[0] - CHAR_SELECT_WIDTH * int(0.5 * NUM_CHARS)
        start_y = 0.5 * HEIGHT - CHAR_SELECT_DIMS[0] * 0.5
        for i in range(NUM_CHARS):
            xPos = start_x + i * (SELECT_SCREEN_SPACE[0])
            rect = pygame.Rect(xPos, start_y, CHAR_SELECT_DIMS[0], CHAR_SELECT_DIMS[1])

            char = Char(self.chars[i], self, 1)
            charImage = char.spriteSheet.subsurface(char.defaultSprite).copy()
            self.charButtons.append(ImageButton(charImage, rect, self.chars[i], SELECT_TEXT_SIZE, self))

        self.stages = ['Default']
        self.stageButtons = []
        start_x = 0.5 * WIDTH - 0.5 * STAGE_SELECT_DIMS[0] - STAGE_SELECT_WIDTH * int(0.5 * NUM_CHARS)
        start_y = 0.5 * HEIGHT - STAGE_SELECT_DIMS[0] * 0.5
        for i in range(NUM_STAGES):
            xPos = start_x + i * (SELECT_SCREEN_SPACE[0])
            rect = pygame.Rect(xPos, start_y, STAGE_SELECT_DIMS[0], STAGE_SELECT_DIMS[1])

            stage = Stage(self.walls[i], self)
            stageImage = stage.image(STAGE_SELECT_DIMS[0] - 2*STAGE_IMAGE_SPACE,
                                     STAGE_SELECT_DIMS[1] - 2*STAGE_IMAGE_SPACE - 16)
            self.stageButtons.append(ImageButton(stageImage, rect, self.stages[i], SELECT_TEXT_SIZE, self))

        # self.walls.append(pygame.Rect(LEFT_PLAT))
        # self.walls.append(pygame.Rect(RIGHT_PLAT))

        # self.screen.fill(pygame.Color('Red'), pygame.Rect(0,0,50,50))

        self.controls = 'joystick'

        pygame.joystick.init()
        joysticks = []

        for i in range(pygame.joystick.get_count()):
            joysticks.append(pygame.joystick.Joystick(i))

        self.controller = joysticks[4]
        self.controller.init()
        print('Controller name: %s' % (self.controller.get_name()))
        print('Number of axes: %d' % (self.controller.get_numaxes()))

    def mainLoop(self, fps):
        self.running = True
        self.fps = fps

        while self.running:
            self.loop(fps)

        pygame.quit()

    def loop(self, fps):
        pygame.display.set_caption('Zero Gravity')  # text at the top of the window
        self.handleEvents()  # detect inputs
        self.update()  # update the screen to the next frame
        self.draw()  # display everything on the screen for the next frame
        pygame.display.flip()
        self.clock.tick(fps)

    def draw(self):
        # start screen
        if self.status == 'start screen':
            self.screen.fill(START_COLOR)
            rect = pygame.Rect(START_TEXT_POS, START_TEXT_RECT_DIMS)
            self.displayText(START_TEXT, START_TEXT_SIZE, rect, START_COLOR, START_TEXT_COLOR)
            self.startButton.draw()
        elif self.status == 'stage select':
            self.screen.fill(START_COLOR)
            for button in self.stageButtons:
                button.draw()
        elif self.status == 'char select':
            self.screen.fill(START_COLOR)
            for button in self.charButtons:
                button.draw()
        elif self.status == 'in game':
            self.screen.fill(GAME_COLOR)
            for char in self.playChars:
                char.draw()
            self.stage.draw()

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # when you click x, exit the program
                self.running = False
            elif event.type == pygame.KEYDOWN:
                print('key pressed')
                self.keyDown(pygame.key.get_pressed())  # if a key was pressed, do the associated action
            # elif event.type == pygame.KEYUP:
            #   self.keyUp(pygame.key.get_pressed())  # if a key was released, do the associated action
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouseUp(event.button, event.pos)  # if the mouse was clicked, do the associated action
            # elif event.type == pygame.MOUSEBUTTONDOWN:
            # self.mouseDown(event.button, event.pos)  #if the mouse button was released, do the associated action
            # elif event.type == pygame.MOUSEMOTION:
            # self.mouseMotion(event.buttons, event.pos, event.rel) #if the mouse was moved, do the associated action
            elif event.type == pygame.JOYAXISMOTION:
                control_x = self.controller.get_axis(CONTROL_STICK_HORIZONTAL)
                control_y = self.controller.get_axis(CONTROL_STICK_VERTICAL)
                c_x = self.controller.get_axis(C_STICK_HORIZONTAL)
                c_y = self.controller.get_axis(C_STICK_VERTICAL)
                self.joystickMoved(control_x, control_y, c_x, c_y)
                # if control_x > 0.1 or control_x < -0.1 or control_y > 0.1 or control_y < -0.1:
                #     print('Control stick values: (%f, %f)' % (control_x, control_y))
            elif event.type == pygame.JOYBUTTONUP:
                # print('button pressed')
                self.buttonUp(event.button)

    def joystickMoved(self, controlX, controlY, cStickX, cStickY):
        # print('Status: ' + self.status)
        # print('Controls: ' + self.controls)
        if self.status == 'in game' and self.controls == 'joystick':  # if a game is being played
            char1 = self.playChars[0]
            # print('control stick angle: %d' % joystickAngle(controlX, controlY))
            walls = char1.onWall  # the wall(s) player 1's character is on
            cDirection = joystickDirection(cStickX, cStickY)
            controlDirection = joystickDirection(controlX, controlY)
            angle = joystickAngle(controlX, controlY)

            if walls:  # if player 1's character is on a wall and a direction is inputted,
                # if the player angles away from the wall, that character jumps off the wall
                if self.stage.checkWalls(angle, walls, char1):
                    # print('Joystick angle: ' + str(joystickAngle(controlX, controlY)))
                    char1.jump(angle)

            else:
                if cDirection == 'left':  # if left was inputted
                    if char1.lookingLeft:
                        char1.forwardA()
                    else:
                        char1.backA()
                elif cDirection == 'up':  # if up was inputted
                    char1.upA()  # do an up a
                elif cDirection == 'down':  # if down was inputted
                    char1.downA()  # do a down a
                elif cDirection == 'right':  # if right was inputted
                    if char1.lookingLeft:
                        char1.backA()  # do a back a
                    else:
                        char1.forwardA()  # do a forward a

            if char1.grabbing is not None:
                char1.throw(controlDirection)
            elif char1.frozen and angle != -1:
                char1.boost(angle)

    # determines what happens when a button is pressed
    def buttonUp(self, button):
        # for i in range(4):
        #     print('Controller axis %d: %d' % (i, self.controller.get_axis(i)))

        # Player 1: directions--WASD, jump--joystick, A attack--a, B attack--b.
        # Player 2: directions--p, l, ;, and ', jump--right alt, A attack--right shift, B attack--right enter.)
        if self.status == 'in game':  # if a game is being played
            char1 = self.playChars[0]
            if button == X_BUTTON:
                print('can be frozen')
                char1.unfreezing = False
            if not char1.onWall:
                direction = joystickDirection(self.controller.get_axis(CONTROL_STICK_HORIZONTAL),
                                              self.controller.get_axis(CONTROL_STICK_VERTICAL))

                if button == A_BUTTON:
                    # if a was pressed and player 1's character is not on a wall
                    if direction == 'left':  # if left was inputted
                        if char1.lookingLeft:
                            char1.forwardA()
                        else:
                            char1.backA()
                    elif direction == 'up':  # if up was inputted
                        char1.upA()  # do an up a
                    elif direction == 'down':  # if down was inputted
                        char1.downA()  # do a down a
                    elif direction == 'right':  # if right was inputted
                        if char1.lookingLeft:
                            char1.backA()  # do a back a
                        else:
                            char1.forwardA()  # do a forward a
                    else:  # if no directions were inputted with the a
                        char1.neutralA()  # do a neutral a

                if button == B_BUTTON:
                    # if b was pressed and player 1's character is not on a wall
                    if direction == 'left':  # if left was inputted
                        if char1.lookingLeft:
                            char1.forwardB()
                        else:
                            char1.backB()
                    elif direction == 'up':  # if up was inputted
                        char1.upB()  # do an up b
                    elif direction == 'down':  # if down was inputted
                        char1.downB()  # do a down b
                    elif direction == 'right':  # if right was inputted
                        if char1.lookingLeft:
                            char1.backB()  # do a back b
                        else:
                            char1.forwardB()  # do a forward b
                    else:  # if no directions were inputted with the b
                        char1.neutralB()  # do a neutral b

                if button == X_BUTTON and self.playChars[0].frozen:
                    self.playChars[0].frozen = False

                if button == Z_BUTTON:
                    print('tether performed')
                    char1.tether()

    def keyUp(self, keys):  # determines what happens when a key is released
        pass

    def keyDown(self, keys):
        # determines what happens when a key is pressed
        if self.status == 'in game':  # if a game is being played
            char2 = self.playChars[1]
            walls = char2.onWall  # the wall player 2's character is on
            if keys[pygame.K_RALT]:  # if right alt was pressed
                # if player 2's character is on a wall and a direction is inputted,
                if (keys[pygame.K_p] or keys[pygame.K_l] or keys[pygame.K_SEMICOLON] or
                    keys[pygame.K_QUOTE]) and walls:
                    if self.stage.checkWalls(keyAngle(keys), walls, char2):
                        char2.jump(keyAngle(keys))
                        # if the player angles away from the wall, that character jumps off the wall

            if keys[pygame.K_RSHIFT] and not walls:
                # if right shift was pressed and player 2's character is not on a wall
                if keys[pygame.K_l]:  # if left was inputted
                    char2.forwardA()  # do a forward a; if the character is able to turn around, change this
                elif keys[pygame.K_p]:  # if up was inputted
                    char2.upA()  # do an up a
                elif keys[pygame.K_SEMICOLON]:  # if down was inputted
                    char2.downA()  # do a down a
                elif keys[pygame.K_QUOTE]:  # if right was inputted
                    char2.backA()  # do a back a; if the character is able to turn around, change this
                else:  # if no directions were inputted with the a
                    char2.neutralA()  # do a neutral a

            if char2.grabbing:
                char2.throw(keyDirection(keys))

    def keyHeld(self, keys):
        if self.status == 'in game':  # if a game is being played
            if self.controls == 'keyboard':
                # if player 1's character is not on a wall and a direction is inputted,
                if (keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]) \
                        and self.playChars[0].onWall == []:
                    self.playChars[0].drift(keyAngle(keys))  # player 1's character drifts
                    # print('drift: %f' % (keyAngle(keys)))

            # if player 2's character is not on a wall and a direction is inputted,
            if (keys[pygame.K_p] or keys[pygame.K_l] or keys[pygame.K_SEMICOLON] or keys[pygame.K_QUOTE]) and \
                    self.playChars[1].onWall == []:
                self.playChars[1].drift(keyAngle(keys))  # player 2's character drifts

    def joystickHeld(self, xAxis, yAxis):
        if self.status == 'in game':  # if a game is being played
            if self.controls == 'joystick':
                angle = joystickAngle(xAxis, yAxis)
                if self.playChars[0].onWall == [] and angle != -1:
                    # if player 1's character is not on a wall and a direction is inputted,
                    self.playChars[0].drift(angle)  # player 1's character drifts
                    # print('drift: %f' % angle)

    def buttonHeld(self):
        for i in range(self.controller.get_numbuttons()):
            if self.status == 'in game':  # if a game is being played
                char1 = self.playChars[0]
                # if self.controller.get_button(i) and i == X_BUTTON:
                #     print('unfreezing: ' + str(char1.unfreezing))
                if not char1.onWall and i == X_BUTTON and self.controller.get_button(i) and not char1.unfreezing:
                    char1.freeze()

    # TODO: implement joystick for both players

    def mouseUp(self, button, pos):
        if self.status == 'start screen':
            if self.startButton.clicked(pos) and button == 1:
                self.status = 'stage select'

        elif self.status == 'stage select':
            for i in range(NUM_STAGES):
                if self.charButtons[i].clicked(pos) and button == 1:
                    self.status = 'char select'
                    self.stage = Stage(self.walls[i], self)

        elif self.status == 'char select':
            for i in range(NUM_CHARS):
                if self.charButtons[i].clicked(pos) and button == 1:
                    self.status = 'in game'
                    p1 = Char(self.chars[i], self, 0)
                    p2 = Char('Alucard', self, 1)
                    p1.opponent = p2
                    p2.opponent = p1
                    self.playChars.append(p1)
                    self.playChars.append(p2)

    def update(self):  # update the screen to the next frame
        self.keyHeld(pygame.key.get_pressed())  # perform actions based on keys held down
        self.buttonHeld()
        self.joystickHeld(self.controller.get_axis(0), self.controller.get_axis(1))

        for char in self.playChars:  # update each character
            char.update()

        self.detectCollisions()  # see if characters have collided with objects, walls, hitboxes, or other characters

    def detectCollisions(self):  # see if a character has collided with a wall (other character)
        for char in self.playChars:  # for every character playing,
            # TODO: use mask to check if char collides with wall
            collided = char.rect.collidelist(self.stage.walls)
            # if char == self.playChars[0] and collided == 2:
            #     print('collided with right wall')
            sides = self.stage.wallSide(char, index=collided)
            if collided != -1:
                if char.onWall != self.stage.walls[collided]:
                    # if that character collides with a wall (and is not already on the wall),
                    # if the character is not moving away from the wall
                    # (this prevents characters 'colliding' with the wall as they jump off it)
                    if (('right' in sides and char.xVelocity <= 0) or ('down' in sides and char.yVelocity <= 0) or
                            ('left' in sides and char.xVelocity >= 0) or ('up' in sides and char.yVelocity >= 0)):
                        # if char == self.playChars[0] and collided == 2:
                        #     print('hit right wall')

                        char.xVelocity = 0
                        char.yVelocity = 0  # the character stops moving
                        char.hitWall(self.stage.walls[collided])
                        # if char == self.playChars[0]:
                        #   print('x: %d, y:%d' % (char.pos[0], char.pos[1]))

            for c2 in self.playChars:
                if c2 is not char:
                    for hitbox in char.hitboxes:
                        if pygame.sprite.collide_mask(hitbox, c2):
                            hitbox.hit(c2)  # the character gets hit
                            if char.currMove is not None:
                                char.currMove.deactivate()  # deactivate the hitbox so it doesn't keep hitting

                    # TODO: handle character collision
                    # if pygame.sprite.collide_mask(char, c2):
                    # print('character collision')

    def end(self, loser):
        print('Player %d wins!' % ((loser.player + 1) % 2 + 1))
        self.draw()
        time.sleep(1)
        self.playChars = []
        self.status = 'char select'

    # show text on the screen
    def displayText(self, message, textSize, rect, bkgColor=(255, 255, 255), textColor=(0, 0, 0)):
        # TODO: change font
        font = pygame.font.Font(None, textSize)
        text = font.render(message, 1, textColor)
        textpos = text.get_rect()
        textpos.centerx = rect.centerx
        textpos.centery = rect.centery
        # pygame.draw.rect(self.screen, bkgColor, textpos)
        self.screen.blit(text, textpos)

# given a set of joystick inputs, return the angle that corresponds to those inputs
def joystickAngle(xAxis, yAxis):
    if yAxis < -1 + DEAD_ZONE:
        return 90
    if xAxis < -1 + DEAD_ZONE:
        return 180
    if yAxis > 1 - DEAD_ZONE:
        return 270
    if xAxis > 1 - DEAD_ZONE:
        return 0

    right = False
    left = False
    up = False
    down = False

    right_diag = False
    left_diag = False
    up_diag = False
    down_diag = False

    if yAxis < - DEAD_ZONE:
        up = True

    if yAxis < - DIAG_DEAD_ZONE:
        up_diag = True

    if xAxis < - DEAD_ZONE:
        left = True

    if xAxis < - DIAG_DEAD_ZONE:
        left_diag = True

    if yAxis > DEAD_ZONE:
        down = True

    if yAxis > DIAG_DEAD_ZONE:
        down_diag = True

    if xAxis > DEAD_ZONE:
        right = True

    if xAxis > DIAG_DEAD_ZONE:
        right_diag = True

    if right_diag and up_diag:
        return 45
    elif left_diag and up_diag:
        return 135
    elif up:
        return 90
    elif down_diag and left_diag:
        return 225
    elif left:
        return 180
    elif down_diag and right_diag:
        return 315
    elif right:
        return 0
    elif down:
        return 270
    else:
        return -1

def joystickDirection(xAxis, yAxis):
    if abs(xAxis) < DEAD_ZONE and abs(yAxis) < DEAD_ZONE:
        return None

    if abs(xAxis) > abs(yAxis):
        if xAxis > 0:
            return 'right'
        else:
            return 'left'
    else:
        if yAxis > 0:
            return 'down'
        else:
            return 'up'

def keyAngle(keys):  # given a set of inputs, return the angle that corresponds to those inputs
    right = False
    left = False
    up = False
    down = False

    if keys[pygame.K_w] or keys[pygame.K_p]:
        up = True

    if keys[pygame.K_a] or keys[pygame.K_l]:
        left = True

    if keys[pygame.K_s] or keys[pygame.K_SEMICOLON]:
        down = True

    if keys[pygame.K_d] or keys[pygame.K_QUOTE]:
        right = True

    if right and up:
        return 45
    elif left and up:
        return 135
    elif up:
        return 90
    elif down and left:
        return 225
    elif left:
        return 180
    elif down and right:
        return 315
    elif right:
        return 0
    elif down:
        return 270

def keyDirection(keys):
    if keys[pygame.K_w] or keys[pygame.K_p]:
        return 'up'

    if keys[pygame.K_a] or keys[pygame.K_l]:
        return 'left'

    if keys[pygame.K_s] or keys[pygame.K_SEMICOLON]:
        return 'down'

    if keys[pygame.K_d] or keys[pygame.K_QUOTE]:
        return 'right'


z = ZeroGravity()  # instantiate the game object
z.mainLoop(FPS)  # start the game
