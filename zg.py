# TODO LIST:
#          Implement tether, shield, and midair boost
#          Switch from using pixel arrays to just masks for hitboxes
#          Allow characters to move out of corners more easily
#          Look into flipping characters' direction
#          Character and stage select screen

# TODO FUTURE:
#          Add new stages
#          Comment
#          Make sure characters collide with each other correctly
#          Implement other characters
#          Re-implement keyboard movement
#          Death, jumping, etc animation

import pygame.key
import os

from Char import *
from Stage import Stage

WIDTH = 1000  # screen width
HEIGHT = 500  # screen height
START_COLOR = (255, 255, 255)  # start screen is white
GAME_COLOR = (255, 255, 255)  # game screen is white -- possible to make this stage-dependent
START_TEXT = "Zero Gravity"  # text on the start screen
START_TEXT_POS = (WIDTH / 2 - 300, 2.0 / 7 * HEIGHT)  # top left corner of start text
START_TEXT_SIZE = 100  # start screen text will be this big
START_TEXT_RECT_DIMS = (600, 100)  # somewhat arbitrary
FPS = 60  # 60 frames per second
BUTTON_TEXT_SIZE = 67  # text on the button will be this big
BUTTON_CORNER = (5 / 18.0 * WIDTH, 4.3 / 7 * HEIGHT)  # top left corner of start button
BUTTON_DIMS = (4 / 9.0 * WIDTH, 1 / 10.0 * HEIGHT)  # length and width of start button
WALL_WIDTH = 40  # how wide the wall is
WINDOW_OFFSET_X = 5
WINDOW_OFFSET_Y = 30  # no idea why but this works
# LEFT_PLAT = (WIDTH / 3 - WIDTH / 14, HEIGHT / 2 - HEIGHT / 8, WIDTH / 7, HEIGHT / 4)
# position and dimensions of a left platform (will be stage dependent in the future)
# RIGHT_PLAT = (WIDTH * 2 / 3 - WIDTH / 14, HEIGHT / 2 - HEIGHT / 8, WIDTH / 7, HEIGHT / 4)
# position and dimensions of a right platform (will be stage dependent in the future)

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
        self.status = "start screen"  # whether the game is at the start screen, character select screen, or in a game
        self.playChars = []  # list of characters currently playing
        self.clock = pygame.time.Clock()

        self.running = False  # whether the program is running
        self.fps = 0  # frames per second
        # (both of these will be set in the mainloop function)

        # TODO: initButtons, initCharacters, etc. functions?
        rect = pygame.Rect(BUTTON_CORNER, BUTTON_DIMS)
        self.startButton = Button("Start!", BUTTON_TEXT_SIZE, (0, 0, 0), rect, self)

        self.wallWidth = WALL_WIDTH
        walls = [pygame.Rect(0, 0, WALL_WIDTH, self.h), pygame.Rect(0, 0, self.w, WALL_WIDTH),
                 pygame.Rect(self.w - WALL_WIDTH, 0, WALL_WIDTH, self.h),
                 pygame.Rect(0, self.h - WALL_WIDTH, self.w, WALL_WIDTH)]

        # put in stage select screen
        self.stage = Stage(walls, self)

        # self.walls.append(pygame.Rect(LEFT_PLAT))
        # self.walls.append(pygame.Rect(RIGHT_PLAT))

        # self.screen.fill(pygame.Color('Red'), pygame.Rect(0,0,50,50))

        self.controls = "joystick"

        pygame.joystick.init()
        joysticks = []

        for i in range(pygame.joystick.get_count()):
            joysticks.append(pygame.joystick.Joystick(i))

        self.controller = joysticks[4]
        self.controller.init()
        print("Controller name: %s" % (self.controller.get_name()))
        print("Number of axes: %d" % (self.controller.get_numaxes()))

    def mainLoop(self, fps):
        self.running = True
        self.fps = fps

        while self.running:
            self.loop(fps)

        pygame.quit()

    def draw(self):
        if self.status == 'start screen':
            self.screen.fill(START_COLOR)
            rect = pygame.Rect(START_TEXT_POS, START_TEXT_RECT_DIMS)
            self.displayText(START_TEXT, START_TEXT_SIZE, rect)
            self.startButton.draw()
            # start screen

        # (character select screen)
        elif self.status == 'char select':
            pass
        elif self.status == 'stage select':
            pass
        else:
            self.screen.fill(GAME_COLOR)
            for char in self.playChars:
                char.draw()
            self.stage.draw()
            # add in stage-specific stuff here

    def loop(self, fps):
        pygame.display.set_caption("Zero Gravity")  # text at the top of the window
        self.handleEvents()  # detect inputs
        self.update()  # update the screen to the next frame
        self.draw()  # display everything on the screen for the next frame
        pygame.display.flip()
        self.clock.tick(fps)

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # when you click x, exit the program
                self.running = False
            elif event.type == pygame.KEYDOWN:
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

                # if control_x > 0.1 or control_x < -0.1 or control_y > 0.1 or control_y < -0.1:
                    # print("Control stick values: (%f, %f)" % (control_x, control_y))

                self.joystickMoved(control_x, control_y, c_x, c_y)

                # print("joystick moved")
            elif event.type == pygame.JOYBUTTONUP:
                self.buttonPressed(event.button)

    def joystickMoved(self, controlX, controlY, cStickX, cStickY):
        if self.status == 'in game' and self.controls == "joystick":  # if a game is being played
            # print("c stick angle: %d" % joystickAngle(cStickX, cStickY))
            walls = self.playChars[0].onWall  # the wall(s) player 1's character is on
            if walls:
                # if player 1's character is on a wall and a direction is inputted,
                if self.stage.checkWalls(joystickAngle(controlX, controlY), walls, self.playChars[0]):
                    # print("Joystick angle: " + str(joystickAngle(controlX, controlY)))
                    self.playChars[0].jump(joystickAngle(controlX, controlY))
                    # if the player angles away from the wall, that character jumps off the wall

            if not self.playChars[0].onWall:
                if cStickX < -DEAD_ZONE:  # if left was inputted
                    print("back A performed")
                    self.playChars[0].backA()  # do a back a; if the character is able to turn around, change this
                elif cStickY < -DEAD_ZONE:  # if up was inputted
                    print("up A performed")
                    self.playChars[0].upA()  # do an up a
                elif cStickY > DEAD_ZONE:  # if down was inputted
                    print("down A performed")
                    self.playChars[0].downA()  # do a down a
                elif cStickX > DEAD_ZONE:  # if right was inputted
                    print("forward A performed")
                    self.playChars[0].forwardA()  # do a forward a; if the character is able to turn around, change this

    # determines what happens when a button is pressed
    def buttonPressed(self, button):
        # for i in range(4):
        #     print("Controller axis %d: %d" % (i, self.controller.get_axis(i)))

        # Player 1: directions--WASD, jump--joystick, A attack--a, B attack--b.
        # Player 2: directions--p, l, ;, and ', jump--right alt, A attack--right shift, B attack--right enter.)
        if self.status == 'in game':  # if a game is being played
            if button == A_BUTTON and not self.playChars[0].onWall:
                direction = joystickDirection(self.controller.get_axis(CONTROL_STICK_HORIZONTAL),
                                              self.controller.get_axis(CONTROL_STICK_VERTICAL))

                # if a was pressed and player 1's character is not on a wall
                if direction == 'left':  # if left was inputted
                    print("back A performed")
                    self.playChars[0].backA()  # do a back a; if the character is able to turn around, change this
                elif direction == 'up':  # if up was inputted
                    print("up A performed")
                    self.playChars[0].upA()  # do an up a
                elif direction == 'down':  # if down was inputted
                    print("down A performed")
                    self.playChars[0].downA()  # do a down a
                elif direction == 'right':  # if right was inputted
                    print("forward A performed")
                    self.playChars[0].forwardA()  # do a forward a; if the character is able to turn around, change this
                else:  # if no directions were inputted with the a
                    print("neutral A performed")
                    self.playChars[0].neutralA()  # do a neutral a

    def keyUp(self, keys):  # determines what happens when a key is released
        pass

    def keyDown(self, keys):
        # determines what happens when a key is pressed
        # Player 1: directions--WASD, jump--space, A attack--n, B attack--b.
        # Player 2: directions--p, l, ;, and ', jump--right alt, A attack--5, B attack--4.)
        if self.status == 'in game':  # if a game is being played
            if keys[pygame.K_RALT]:  # if enter was pressed
                walls = self.playChars[1].onWall  # the wall player 2's character is on
                if (keys[pygame.K_p] or keys[pygame.K_l] or keys[pygame.K_SEMICOLON] or
                    keys[
                        pygame.K_QUOTE]) and walls != []:  # if player 2's character is on the wall and a direction is inputted,
                    if self.stage.checkWalls(keyAngle(keys), walls, self.playChars[1]):
                        self.playChars[1].jump(keyAngle(keys))
                        # if the player angles away from the wall, that character jumps off the wall

            if keys[pygame.K_RSHIFT] and self.playChars[1].onWall == []:
                # if right shift was pressed and player 2's character is not on a wall
                if keys[pygame.K_l]:  # if left was inputted
                    self.playChars[1].forwardA()  # do a forward a; if the character is able to turn around, change this
                elif keys[pygame.K_p]:  # if up was inputted
                    self.playChars[1].upA()  # do an up a
                elif keys[pygame.K_SEMICOLON]:  # if down was inputted
                    self.playChars[1].downA()  # do a down a
                elif keys[pygame.K_QUOTE]:  # if right was inputted
                    self.playChars[1].backA()  # do a back a; if the character is able to turn around, change this
                else:  # if no directions were inputted with the a
                    self.playChars[1].neutralA()  # do a neutral a

    def keyHeld(self, keys):
        if self.status == "in game":  # if a game is being played
            if self.controls == "keyboard":
                # if player 1's character is not on a wall and a direction is inputted,
                if (keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]) \
                        and self.playChars[0].onWall == []:
                    self.playChars[0].drift(keyAngle(keys))  # player 1's character drifts
                    # print("drift: %f" % (keyAngle(keys)))

            # if player 2's character is not on a wall and a direction is inputted,
            if (keys[pygame.K_p] or keys[pygame.K_l] or keys[pygame.K_SEMICOLON] or keys[pygame.K_QUOTE]) and \
                    self.playChars[1].onWall == []:
                self.playChars[1].drift(keyAngle(keys))  # player 2's character drifts

    def joystickHeld(self, xAxis, yAxis):
        if self.status == "in game":  # if a game is being played
            if self.controls == "joystick":
                angle = joystickAngle(xAxis, yAxis)
                if self.playChars[0].onWall == [] and angle != -1:
                    # if player 1's character is not on a wall and a direction is inputted,
                    self.playChars[0].drift(angle)  # player 1's character drifts
                    # print("drift: %f" % angle)

    # TODO: implement joystick for both players

    def mouseUp(self, button, pos):
        if self.status == 'start screen':
            if self.startButton.clicked(pos) and button == 1:
                self.status = 'in game'  # change to character select screen, then stage select screen
                self.playChars = []
                self.playChars.append(Char('Swordsman', self, 0))  # change obviously
                self.playChars.append(Char('Swordsman', self, 1))
            # other buttons

    def update(self):  # update the screen to the next frame
        self.keyHeld(pygame.key.get_pressed())  # perform actions based on keys held down
        self.joystickHeld(self.controller.get_axis(0), self.controller.get_axis(1))

        self.detectCollisions()  # see if characters have collided with objects, walls, hitboxes, or other characters

        for char in self.playChars:  # update each character
            char.update()

        self.detectCollisions()  # again to improve precision

    def detectCollisions(self):  # see if a character has collided with a wall (other character)
        for char in self.playChars:  # for every character playing,
            # TODO: use mask to check if
            collided = char.rect.collidelist(self.stage.walls)
            # if char == self.playChars[0] and collided == 2:
            #     print("collided with right wall")
            sides = self.stage.wallSide(char, index=collided)
            if collided != -1:
                if char.onWall != self.stage.walls[collided]:
                    # if that character collides with a wall (and is not already on the wall),
                    # if the character is not moving away from the wall
                    # (this prevents characters "colliding" with the wall as they jump off it)
                    if (('right' in sides and char.xVelocity <= 0) or ('down' in sides and char.yVelocity <= 0) or
                            ('left' in sides and char.xVelocity >= 0) or ('up' in sides and char.yVelocity >= 0)):
                        # if char == self.playChars[0] and collided == 2:
                        #     print("hit right wall")

                        char.xVelocity = 0
                        char.yVelocity = 0  # the character stops moving
                        char.hitWall(self.stage.walls[collided])
                        # if char == self.playChars[0]:
                        #   print("x: %d, y:%d" % (char.pos[0], char.pos[1]))

            for c2 in self.playChars:
                if c2 is not char:
                    for hitbox in char.hitboxes:
                        if pygame.sprite.collide_mask(hitbox, c2):
                            c2.hit(hitbox)  # the character gets hit
                            char.currMove.deactivate()  # deactivate the hitbox so it doesn't keep hitting

                    # TODO: handle collison
                    # if pygame.sprite.collide_mask(char, c2):
                        # print("character collision")

    def end(self, loser):
        print("Player %d wins!" % ((loser.player + 1) % 2 + 1))
        self.status = "start screen"

    # show text on the screen
    def displayText(self, message, textSize, rect, bkgColor=(255, 255, 255), textColor=(0, 0, 0)):
        font = pygame.font.Font(None, textSize)
        text = font.render(message, 1, textColor)
        textpos = text.get_rect()
        textpos.centerx = rect.centerx
        textpos.centery = rect.centery
        pygame.draw.rect(self.screen, bkgColor, textpos)
        self.screen.blit(text, textpos)

# # return a tuple giving the direction of the joystick given its position
# def joystickDirection(x, y):
#     if x > JOYSTICK_DIAG - DEAD_ZONE:
#         if y > JOYSTICK_DIAG - DEAD_ZONE:
#             return 0, 1, 0, 1
#         if y < - JOYSTICK_DIAG - DEAD_ZONE:
#             return 0, 1, 1, 0
#     if x < - JOYSTICK_DIAG - DEAD_ZONE:
#         if y > JOYSTICK_DIAG - DEAD_ZONE:
#             return 1, 0, 0, 1
#         if y < - JOYSTICK_DIAG - DEAD_ZONE:
#             return 1, 0, 1, 0

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


z = ZeroGravity()  # instantiate the game object
z.mainLoop(FPS)  # start the game
