# TODO List:
#          Make game work on wii
#          Default sprite when move becomes inactive
#          "Active frame" for throws
#          Allow characters to change direction at will
#          Landing lag
#          When a character in hitstun hits a wall, make it bounce off
#          Character get stunned when their tether collides with an attack
#          Comment
#          Re-implement keyboard movement
#          Allow any port for controller

# TODO future:
#       Wall attack and wall walking
#       Allow tethers to be angled and to snap to the wall
#       Prevent attacks while frozen from boost
#       Relax jumping constraints
#       Select stage + character with controller
#       Make characters bigger?
#       Make it look prettier, including images
#       Add new characters
#

# TODO stretch:
#       Handle character collision
#       Add new stages
#       Better wall collision detection

# TODO: bugs
#       If a character hits a wall before the throw is over, the throw doesn't happen
#       If robotnik dies on the bottom wall, the final sprite doesn't show up

import time
import pygame.key
import os
import gc

from Char import *
from Stage import Stage

WIDTH = 1280
HEIGHT = 800
WINDOW_OFFSET_X = 5
WINDOW_OFFSET_Y = 30  # no idea why but this works
START_COLOR = (60, 100, 140)  # start screen color
START_TEXT_COLOR = (0, 0, 0)
GAME_COLOR = (50, 100, 150)  # game screen color -- possible to make this stage-dependent
FPS = 60  # 60 frames per second

START_TEXT = 'ZERO GRAVITY'  # text on the start screen
START_TEXT_POS = (WIDTH / 2 - 300, .371 * HEIGHT)  # top left corner of start text
START_TEXT_SIZE = 120  # start screen text will be this big
START_TEXT_RECT_DIMS = (600, 100)  # somewhat arbitrary
BUTTON_TEXT_SIZE = 50  # text on the button will be this big
BUTTON_CORNER = (0.278 * WIDTH, 0.614 * HEIGHT)  # top left corner of start button
BUTTON_DIMS = (0.444 * WIDTH, 0.1 * HEIGHT)  # length and width of start button

SELECT_SCREEN_SPACE = (10, 10)  # distance in between each character/stage on the select screen
SELECT_TEXT_SIZE = 18

NUM_STAGES = 1
STAGE_SELECT_DIMS = (int(0.2 * WIDTH), int(0.25 * HEIGHT))  # length and width of stage select buttons
STAGE_SELECT_WIDTH = STAGE_SELECT_DIMS[0] + SELECT_SCREEN_SPACE[0]
STAGE_SELECT_LEN = STAGE_SELECT_DIMS[1] + SELECT_SCREEN_SPACE[1]
STAGE_IMAGE_SPACE = 5
STAGE_IMAGE_BUFFER = 33

NUM_CHARS = 2
CHAR_SELECT_DIMS = (0.17 * WIDTH, 0.30 * HEIGHT)  # length and width of character select buttons
CHAR_SELECT_WIDTH = CHAR_SELECT_DIMS[0] + SELECT_SCREEN_SPACE[0]
CHAR_SELECT_LEN = CHAR_SELECT_DIMS[1] + SELECT_SCREEN_SPACE[1]
CHAR_IMAGE_SCALE = 1.7

WALL_WIDTH = 20  # how wide the wall is

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
SINGLE_DIRECTION_BUFFER = 0.2

BOOST_PAUSE = 30

class ZeroGravity:
    def __init__(self):
        pygame.init()
        self.w = WIDTH
        self.h = HEIGHT

        # screen is in top left corner
        os.environ['SDL_VIDEO_WINDOW_POS'] = '%i,%i' % (WINDOW_OFFSET_X, WINDOW_OFFSET_Y)
        self.screen = pygame.display.set_mode((self.w, self.h), pygame.FULLSCREEN)  # create the screen
        # self.screen.fill(START_COLOR)  # fill the screen with white
        pygame.display.flip()  # open the screen

        self.background = pygame.image.load('imgs/background.jpg')
        self.background = pygame.transform.scale(self.background, (self.w, self.h))

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

        self.chars = ['ALUCARD', 'DR ROBOTNIK']
        self.charButtons = []
        start_x = 0.5 * WIDTH - 0.5 * CHAR_SELECT_DIMS[0] - CHAR_SELECT_WIDTH * 0.5 * (NUM_CHARS - 1)
        start_y = 0.5 * HEIGHT - CHAR_SELECT_DIMS[0] * 0.5
        for i in range(NUM_CHARS):
            xPos = start_x + i * (SELECT_SCREEN_SPACE[0] + CHAR_SELECT_DIMS[0])
            rect = pygame.Rect(xPos, start_y, CHAR_SELECT_DIMS[0], CHAR_SELECT_DIMS[1])

            char = Char(self.chars[i], self, 1)
            charImage = char.spriteSheet.subsurface(char.defaultSprite).copy()
            charImage = pygame.transform.scale(charImage, (int(charImage.get_width() * CHAR_IMAGE_SCALE),
                                                           int(charImage.get_height() * CHAR_IMAGE_SCALE)))
            self.charButtons.append(ImageButton(charImage, rect, self.chars[i], SELECT_TEXT_SIZE, self))

        self.stages = ['DEFAULT']
        self.stageButtons = []
        start_x = 0.5 * WIDTH - 0.5 * STAGE_SELECT_DIMS[0] - STAGE_SELECT_WIDTH * 0.5 * (NUM_STAGES - 1)
        start_y = 0.5 * HEIGHT - STAGE_SELECT_DIMS[0] * 0.5
        for i in range(NUM_STAGES):
            xPos = start_x + i * (SELECT_SCREEN_SPACE[0] + STAGE_SELECT_DIMS[0])
            rect = pygame.Rect(xPos, start_y, STAGE_SELECT_DIMS[0], STAGE_SELECT_DIMS[1])

            stage = Stage(self.walls[i], self)
            stageImage = stage.image(STAGE_SELECT_DIMS[0] - 2 * STAGE_IMAGE_SPACE,
                                     STAGE_SELECT_DIMS[1] - 2 * STAGE_IMAGE_SPACE - STAGE_IMAGE_BUFFER)
            self.stageButtons.append(ImageButton(stageImage, rect, self.stages[i], SELECT_TEXT_SIZE, self))

        # self.walls.append(pygame.Rect(LEFT_PLAT))
        # self.walls.append(pygame.Rect(RIGHT_PLAT))

        # self.screen.fill(pygame.Color('Red'), pygame.Rect(0,0,50,50))

        #self.controls = 'joystick'
        self.controls = 'keyboard'

        pygame.joystick.init()
        self.controllers = []

        for i in range(pygame.joystick.get_count()):
            self.controllers.append(pygame.joystick.Joystick(i))

        #self.p1controls = self.controllers[1]
        #self.p2controls = self.controllers[0]
        #self.p1controls.init()
        #self.p2controls.init()
        # self.controllers[4].init()
        # self.controllers[2].init()
        # self.controllers[3].init()
        # print('Controller name: %s' % (self.p1controls.get_name()))
        # print('Number of axes: %d' % (self.p1controls.get_numaxes()))

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
            self.displayText(START_TEXT, START_TEXT_SIZE, rect, START_TEXT_COLOR)
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
            self.screen.blit(self.background, (0, 0))
            for char in self.playChars:
                char.draw()
            self.stage.draw()

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # when you click x, exit the program
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # print('key pressed')
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
                controller = self.controllers[event.joy]
                control_x = controller.get_axis(CONTROL_STICK_HORIZONTAL)
                control_y = controller.get_axis(CONTROL_STICK_VERTICAL)
                c_x = controller.get_axis(C_STICK_HORIZONTAL)
                c_y = controller.get_axis(C_STICK_VERTICAL)
                self.joystickMoved(controller, control_x, control_y, c_x, c_y)
                # if control_x > 0.1 or control_x < -0.1 or control_y > 0.1 or control_y < -0.1:
                #     print('Control stick values: (%f, %f)' % (control_x, control_y))
            elif event.type == pygame.JOYBUTTONUP:
                # print('button pressed')
                print('controller: ' + str(event.joy))
                controller = self.controllers[event.joy]
                self.buttonUp(controller, event.button)

    def joystickMoved(self, controller, controlX, controlY, cStickX, cStickY):
        # print('Status: ' + self.status)
        # print('Controls: ' + self.controls)
        if self.status == 'in game' and self.controls == 'joystick':  # if a game is being played
            if controller == self.p1controls:
                char = self.playChars[0]
            else:
                char = self.playChars[1]
            # print('control stick angle: %d' % joystickAngle(controlX, controlY))
            walls = char.onWall  # the wall(s) player 1's character is on
            cDirection = joystickDirection(cStickX, cStickY)
            controlDirection = joystickDirection(controlX, controlY)
            angle = joystickAngle(controlX, controlY)

            if walls:  # if player 1's character is on a wall and a direction is inputted,
                # if the player angles away from the wall, that character jumps off the wall
                if self.stage.checkWalls(angle, walls, char):
                    # print('Joystick angle: ' + str(joystickAngle(controlX, controlY)))
                    char.startJump(angle)

            else:
                if cDirection == 'left':  # if left was inputted
                    if char.lookingLeft:
                        char.forwardA()
                    else:
                        char.backA()
                elif cDirection == 'up':  # if up was inputted
                    char.upA()  # do an up a
                elif cDirection == 'down':  # if down was inputted
                    char.downA()  # do a down a
                elif cDirection == 'right':  # if right was inputted
                    if char.lookingLeft:
                        char.backA()  # do a back a
                    else:
                        char.forwardA()  # do a forward a

            if char.grabbing is not None:
                char.throw(controlDirection)
            elif char.frozen and angle != -1:
                char.boost(angle)

    # determines what happens when a button is pressed
    def buttonUp(self, controller, button):
        # for i in range(4):
        #     print('Controller axis %d: %d' % (i, self.p1controls.get_axis(i)))
        # Player 1: directions--WASD, jump--joystick, A attack--a, B attack--b.
        # Player 2: directions--p, l, ;, and ', jump--right alt, A attack--right shift, B attack--right enter.
        if self.status == 'in game':  # if a game is being played
            if controller == self.p1controls:
                char = self.playChars[0]
            else:
                char = self.playChars[1]
            if button == X_BUTTON:
                # print('can be frozen')
                char.unfreezing = False
            if button == L_BUTTON or button == R_BUTTON:
                char.shielding = False
            if not char.onWall:
                direction = joystickDirection(controller.get_axis(CONTROL_STICK_HORIZONTAL),
                                              controller.get_axis(CONTROL_STICK_VERTICAL))

                if button == A_BUTTON:
                    # if a was pressed and player 1's character is not on a wall
                    if direction == 'left':  # if left was inputted
                        if char.lookingLeft:
                            char.forwardA()
                        else:
                            char.backA()
                    elif direction == 'up':  # if up was inputted
                        char.upA()  # do an up a
                    elif direction == 'down':  # if down was inputted
                        char.downA()  # do a down a
                    elif direction == 'right':  # if right was inputted
                        if char.lookingLeft:
                            char.backA()  # do a back a
                        else:
                            char.forwardA()  # do a forward a
                    else:  # if no directions were inputted with the a
                        char.neutralA()  # do a neutral a

                if button == B_BUTTON:
                    # if b was pressed and player 1's character is not on a wall
                    if direction == 'left':  # if left was inputted
                        if char.lookingLeft:
                            char.forwardB()
                        else:
                            char.backB()
                    elif direction == 'up':  # if up was inputted
                        char.upB()  # do an up b
                    elif direction == 'down':  # if down was inputted
                        char.downB()  # do a down b
                    elif direction == 'right':  # if right was inputted
                        if char.lookingLeft:
                            char.backB()  # do a back b
                        else:
                            char.forwardB()  # do a forward b
                    else:  # if no directions were inputted with the b
                        char.neutralB()  # do a neutral b

                if button == X_BUTTON and self.playChars[0].frozen:
                    self.playChars[0].frozen = False

                if button == Z_BUTTON:
                    print('tether performed')
                    char.tether()

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
                        char2.startJump(keyAngle(keys))
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
        for i in range(self.p1controls.get_numbuttons()):
            if self.status == 'in game':  # if a game is being played
                char1 = self.playChars[0]
                # if self.p1controls.get_button(i) and i == X_BUTTON:
                #     print('unfreezing: ' + str(char1.unfreezing))
                if not char1.onWall and i == X_BUTTON and self.p1controls.get_button(i) and not char1.unfreezing:
                    if char1.boostCount > 0:
                        if not char1.frozen:
                            char1.freeze()
                            char1.freezeTimer = BOOST_PAUSE

                if (i == L_BUTTON and self.p1controls.get_button(i)) or \
                        (i == R_BUTTON and self.p1controls.get_button(i)):
                    angle = joystickAngle(self.p1controls.get_axis(CONTROL_STICK_HORIZONTAL),
                                          self.p1controls.get_axis(CONTROL_STICK_VERTICAL))
                    char1.shield(angle)
                    char1.shielding = True

        for i in range(self.p2controls.get_numbuttons()):
            if self.status == 'in game':  # if a game is being played
                char2 = self.playChars[1]
                # if self.p1controls.get_button(i) and i == X_BUTTON:
                #     print('unfreezing: ' + str(char1.unfreezing))
                if not char2.onWall and i == X_BUTTON and self.p2controls.get_button(i) and not char2.unfreezing:
                    if char2.boostCount > 0:
                        if not char2.frozen:
                            char2.freeze()
                            char2.freezeTimer = BOOST_PAUSE

                if (i == L_BUTTON and self.p2controls.get_button(i)) or \
                        (i == R_BUTTON and self.p2controls.get_button(i)):
                    angle = joystickAngle(self.p2controls.get_axis(CONTROL_STICK_HORIZONTAL),
                                          self.p2controls.get_axis(CONTROL_STICK_VERTICAL))
                    char2.shield(angle)
                    char2.shielding = True

    # TODO: implement joystick for both players

    def mouseUp(self, button, pos):
        if self.status == 'start screen':
            if self.startButton.clicked(pos) and button == 1:
                self.status = 'stage select'

        elif self.status == 'stage select':
            print('click')
            for i in range(NUM_STAGES):
                if self.stageButtons[i].clicked(pos) and button == 1:
                    self.status = 'char select'
                    self.stage = Stage(self.walls[i], self)

        elif self.status == 'char select':
            for i in range(NUM_CHARS):
                if self.charButtons[i].clicked(pos) and button == 1:
                    self.status = 'in game'
                    p1 = Char(self.chars[i], self, 0)
                    p2 = Char('ALUCARD', self, 1)
                    p1.opponent = p2
                    p2.opponent = p1
                    self.playChars.append(p1)
                    self.playChars.append(p2)

    def update(self):  # update the screen to the next frame
        self.keyHeld(pygame.key.get_pressed())  # perform actions based on keys held down
        #self.buttonHeld()
        #self.joystickHeld(self.p1controls.get_axis(0), self.p1controls.get_axis(1))
        #self.joystickHeld(self.p2controls.get_axis(0), self.p2controls.get_axis(1))

        for char in self.playChars:  # update each character
            char.update()

        self.detectCollisions()  # see if characters have collided with objects, walls, hitboxes, or other characters

    def detectCollisions(self):  # see if a character has collided with a wall, effect box, or other character
        if self.status == 'in game':
            for char in self.playChars:  # for every character playing,
                # TODO: change this
                walls = []

                for wall in self.stage.walls:
                    if char.collidesWith(wall):
                        walls.append(wall)

                # if char == self.playChars[0] and collided == 2:
                #     print('collided with right wall')
                for wall in walls:
                    # if char == self.playChars[0]:
                    #     print('Collided: ' + str(collided))
                    #     print('Rect: ' + str(char.rect))
                    if wall not in char.onWall and wall not in char.leavingWall and not isinstance(char.currMove, Jump):
                        # if that character collides with a wall (and is not already on the wall),
                        # if the character is not moving away from the wall
                        # (this prevents characters 'colliding' with the wall as they jump off it)
                        # if (('right' in sides and char.xVelocity <= 0) or ('down' in sides and char.yVelocity <= 0) or
                        #         ('left' in sides and char.xVelocity >= 0) or ('up' in sides and char.yVelocity >= 0)):
                        char.hitWall(wall)
                        # if char == self.playChars[0]:
                        #   print('x: %d, y:%d' % (char.pos[0], char.pos[1]))

                for c2 in self.playChars:
                    if c2 != char:
                        shieldCollision(char, c2)
                        boxCollision(char, c2)

                # TODO: handle character collision
                # if pygame.sprite.collide_mask(char, c2):
                # print('character collision')

    def end(self, loser):
        print('Player %d wins!' % ((loser.player + 1) % 2 + 1))
        # self.draw()
        time.sleep(1)
        self.playChars = []
        self.status = 'char select'
        gc.collect()

    # show text on the screen
    def displayText(self, message, textSize, rect, textColor=(0, 0, 0)):
        font = pygame.font.Font('Fonts/Elianto-Regular.ttf', textSize)
        text = font.render(message, False, textColor)
        textpos = text.get_rect()
        textpos.centerx = rect.centerx
        textpos.centery = rect.centery
        # pygame.draw.rect(self.screen, bkgColor, textpos)
        self.screen.blit(text, textpos)


def shieldCollision(c1: Char, c2: Char):
    for box in c1.effectBoxes:
        if isinstance(box, ShieldBox):
            for box2 in c2.effectBoxes:
                if isinstance(box2, Hitbox) and pygame.sprite.collide_mask(box, box2):
                    box.hit(box2)


def boxCollision(c1: Char, c2: Char):
    for box in c1.effectBoxes:
        if not isinstance(box, ShieldBox):
            if pygame.sprite.collide_mask(box, c2):
                box.hit(c2)  # the character gets hit
                if c1.currMove is not None:
                    c1.currMove.deactivate()  # deactivate the hitbox so it doesn't keep hitting


# given a set of joystick inputs, return the angle that corresponds to those inputs
def joystickAngle(xAxis, yAxis):
    if yAxis < -1 + SINGLE_DIRECTION_BUFFER:
        return 90
    if xAxis < -1 + SINGLE_DIRECTION_BUFFER:
        return 180
    if yAxis > 1 - SINGLE_DIRECTION_BUFFER:
        return 270
    if xAxis > 1 - SINGLE_DIRECTION_BUFFER:
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
