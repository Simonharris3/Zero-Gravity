from Move import *
import math
import pygame

# HEALTH_BAR_OFFSET = 10  # could be used but display is fine without it
HEALTH_BAR_WIDTH = 5
HEALTH_BAR_COLOR = (30, 60, 140)

HITSTUN_CONSTANT = 5

IMAGE_BUTTON_SPACE = 5
SELECT_TEXT_Y = .78

MOVE_OFF_WALL = (15, 25)
MOVE_OFF_DOWN_WALL = 35

LEAVING_WALL_FRAMES = 25
LEAVING_WALL_DISTANCE = 15

START_COLOR = (60, 100, 140)
TEXT_COLOR = (0, 0, 0)

SAME_BOOST_CONSTANT = 0.5
OPPOSITE_BOOST_CONSTANT = 0.8 / 0.5

NUM_SHIELD_POSITIONS = 8

END_FRAMES = 10

class Char(pygame.sprite.Sprite):
    def __init__(self, name, game, player):
        pygame.sprite.Sprite.__init__(self)

        self.player = player  # player number
        self.game = game
        self.stage = self.game.stage
        self.screen = self.game.screen
        self.name = name  # use this to find the character datasheet, which determines all other character attributes

        self.canAct = True  # whether the character is in move lag or hitstun
        self.frozen = False  # if a character is frozen, it cannot drift or jump

        self.unfreezing = False  # so that the character doesn't immediately freeze after unfreezing
        self.shielding = False
        self.shieldAngle = 0  # angle of the shield relative to the character

        self.leavingWall = []
        self.leavingCounter = -1

        self.fallingToDeath = False
        self.endTimer = -1

        self.datasheet = open('Files/' + self.name + '.txt')  # get data from the datasheet

        self.jumpSpeed = int(self.datasheet.readline()[7:])  # regular movement speed
        self.mass = float(self.datasheet.readline()[6:])
        self.startingHealth = int(self.datasheet.readline()[8:])  # starting health
        self.driftSpeed = float(self.datasheet.readline()[11:])  # how fast the character drifts

        self.spriteFile = self.datasheet.readline()[9:].strip()  # get the file with all the sprites
        self.spriteSheet = pygame.image.load('imgs/' + self.spriteFile).convert()
        self.spriteSheet.set_colorkey((255, 0, 255))  # remove background color

        next(self.datasheet)
        # sprite to be displayed when the character is in the air in a neutral position
        defSprite = self.datasheet.readline().split()
        self.defaultSprite = (int(defSprite[0]), int(defSprite[1]), int(defSprite[2]), int(defSprite[3]))

        next(self.datasheet)
        # sprite to be displayed whenever the character is on a wall
        wallSprite = self.datasheet.readline().split()
        self.wallSprite = (int(wallSprite[0]), int(wallSprite[1]), int(wallSprite[2]), int(wallSprite[3]))

        self.currSprite = self.wallSprite  # sprite to be displayed currently (points to a position on the spriteSheet)

        self.dims = (self.currSprite[2], self.currSprite[3])  # width and height
        # image of the character from sprite sheet
        self.image = self.spriteSheet.subsurface(self.currSprite).copy()
        self.lookingLeft = False  # whether the sprite has to be lookingLeft to face the opposite direction

        # start of left wall if you're player 1, right wall if you're player 2
        if self.player == 0:
            self.pos = (self.stage.p1start[0], self.stage.p1start[1] - self.dims[1] / 2)
            # start in the middle of the side wall
        if self.player == 1:
            self.pos = (self.stage.p2start[0] - self.dims[0] + 1, self.stage.p2start[1] - self.dims[1] / 2)

        self.moves = {}
        self.animations = {}

        moveNames = ['neutralA', 'forwardA', 'backA', 'upA', 'downA', 'downB']
        throwNames = ['forwardThrow', 'backThrow', 'upThrow', 'downThrow']

        self.tetherFile = 'simonbelmont.png'
        self.shieldFile = 'alucardfinal.png'

        # for each move, read in the data from the file and create its move object
        for i in range(len(moveNames)):
            for k in range(3):
                next(self.datasheet)

            frames = self.datasheet.readline().split()
            damage = int(self.datasheet.readline()[7:])
            knockback = int(self.datasheet.readline()[10:])
            angle = int(self.datasheet.readline()[5:])
            numHitboxes = int(self.datasheet.readline()[10:12])

            hitboxes = []
            for k in range(numHitboxes):
                data = self.datasheet.readline().split()
                hitbox = []

                for c in range(4):
                    hitbox.append(int(data[c]))

                # if data[-1] == "True":
                #     color = self.datasheet.readline().split()
                #     hitbox.append((int(color[0]), int(color[1]), int(color[2])))

                # else:
                #     hitbox.append(None)

                hitboxes.append(pygame.Rect(hitbox))

            next(self.datasheet)

            sprites = []
            for k in range(numHitboxes):
                data = self.datasheet.readline().split()
                sprite = []
                for datum in data:
                    sprite.append(int(datum))

                sprites.append(pygame.Rect(sprite))

            # print('%s sprite file: %s' % (moveNames[i], spriteFile))
            # create a move object with all the data read from the file
            self.moves[moveNames[i]] = \
                Attack(frames, damage, knockback, angle, hitboxes, sprites, self.game, self)

        for i in range(len(throwNames)):
            for k in range(3):
                next(self.datasheet)

            frames = self.datasheet.readline().split()
            damage = int(self.datasheet.readline()[7:])
            knockback = int(self.datasheet.readline()[10:])
            angle = int(self.datasheet.readline()[5:])
            numSprites = int(self.datasheet.readline()[9:11])

            sprites = []
            for k in range(numSprites):
                data = self.datasheet.readline().split()
                sprite = []
                for datum in data:
                    sprite.append(int(datum))

                sprites.append(pygame.Rect(sprite))

            # print('%s sprite file: %s' % (moveNames[i], spriteFile))
            # create a move object with all the data read from the file
            self.moves[throwNames[i]] = \
                Throw(frames, damage, knockback, angle, sprites, self.game, self)

        for i in range(3):
            next(self.datasheet)

        # tether info
        frames = self.datasheet.readline().split()
        next(self.datasheet)
        startPosText = self.datasheet.readline().split()
        startPos = (int(startPosText[0]), int(startPosText[1]))
        numGrabBoxes = int(self.datasheet.readline()[12:])

        grabBoxes = []
        for k in range(numGrabBoxes):
            data = self.datasheet.readline().split()
            grabBox = []

            for datum in data:
                grabBox.append(int(datum))

            grabBoxes.append(pygame.Rect(grabBox))

        next(self.datasheet)

        sprites = []
        for k in range(numGrabBoxes):
            data = self.datasheet.readline().split()
            sprite = []
            for datum in data:
                sprite.append(int(datum))

            sprites.append(pygame.Rect(sprite))

        # create a tether object with all the data read from the file
        self.tetherAnimation = Tether(frames, startPos, grabBoxes, sprites, self.game, self)

        for i in range(3):
            next(self.datasheet)

        # shield info
        startPositions = []
        for i in range(NUM_SHIELD_POSITIONS):
            startPosText = self.datasheet.readline().split()
            startPos = (int(startPosText[0]), int(startPosText[1]))
            startPositions.append(startPos)

        next(self.datasheet)

        rectText = self.datasheet.readline().split()
        rectData = []

        for datum in rectText:
            rectData.append(int(datum))

        rect = pygame.Rect(rectData)
        self.shieldAnimation = Shield(startPositions, rect, self)

        next(self.datasheet)
        next(self.datasheet)

        frames = self.datasheet.readline().split()
        numJumpSprites = int(self.datasheet.readline()[9:])

        sprites = []
        for k in range(numJumpSprites):
            data = self.datasheet.readline().split()
            sprite = []
            for datum in data:
                sprite.append(int(datum))

            sprites.append(pygame.Rect(sprite))

        self.jumpAnimation = Jump(frames, sprites, None, self.game, self)

        next(self.datasheet)
        next(self.datasheet)

        frames = self.datasheet.readline().split()
        numDeathSprites = int(self.datasheet.readline()[9:])

        sprites = []
        for k in range(numDeathSprites):
            data = self.datasheet.readline().split()
            sprite = []
            for datum in data:
                sprite.append(int(datum))

            sprites.append(pygame.Rect(sprite))

        self.deathAnimation = Death(frames, sprites, None, self.game, self)

        next(self.datasheet)

        data = self.datasheet.readline().split()
        self.finalSprite = []
        for datum in data:
            self.finalSprite.append(int(datum))

        self.hitstun = -1  # frames of hitstun remaining
        self.health = self.startingHealth  # starting health
        self.healthBar = pygame.Rect(0, 0, self.dims[0], HEALTH_BAR_WIDTH)

        self.effectBoxes = []  # current active effect boxes (shields, hitboxes, grab boxes)
        self.currMove = None  # the character's active move, if any
        self.grabbing = None  # whether the character is currently grabbing another character

        # a rectangle around the character, used to speed up collision detection
        self.rect = pygame.Rect(self.pos, self.dims)
        self.xVelocity = 0  # velocity in the x direction at any given time
        self.yVelocity = 0  # velocity in the y direction at any given time

        # orient the character based on which side of the field it is on
        if self.player == 0:
            self.side = 'right'
            self.orientation = 270  # angle the sprite has to be rotated
            self.onWall = [self.stage.leftWall]  # which wall(s) the character is on, if any

        if self.player == 1:
            self.side = 'left'
            self.orientation = 90
            self.onWall = [self.stage.rightWall]  # which wall(s) the character is on, if any

    def startJump(self, angle):
        if self.canAct and not self.shielding:
            self.jumpAnimation.angle = angle
            self.jumpAnimation.orientation = self.orientation
            self.jumpAnimation.start()

    def jump(self, angle):  # character jumps off the wall based on input
        self.xVelocity = round(math.cos(math.radians(angle)), 2) * self.jumpSpeed
        self.yVelocity = round(-1 * math.sin(math.radians(angle)), 2) * self.jumpSpeed
        self.leaveWall()

        if 90 < angle < 270:
            self.lookingLeft = True

        if angle > 270 or angle < 90:
            self.lookingLeft = False

        # print('start')

    def drift(self, angle):  # move through the air in the direction being held
        if not self.frozen and not self.shielding:
            x = math.cos(math.radians(angle)) * self.driftSpeed  # movement in the x direction
            y = -1 * math.sin(math.radians(angle)) * self.driftSpeed  # y direction
            self.move(x, y)

    def draw(self):  # displays itself on the screen
        sprite = self.image

        # sprite.fill(pygame.Color('White'), pygame.Rect(0,0,self.dims[0],HEALTH_BAR_WIDTH))
        sprite.fill(HEALTH_BAR_COLOR, self.healthBar)

        if self.lookingLeft:
            sprite = pygame.transform.flip(sprite, True, False)  # horizontally flip the sprite if necessary

        sprite = pygame.transform.rotate(sprite, self.orientation)  # rotate sprite depending on orientation

        # color = None
        # if self.hitstun != -1:
        #     color = (200, 255, 200)
        # elif not self.canAct:
        #     if self.hitboxes:
        #         if self.hitboxes[0].shape.x > 0:
        #             color = (255, 200, 200)
        #         else:
        #             color = (255, 230, 200)
        #     else:
        #         color = (255, 230, 200)

        # if color is not None:
        # pygame.draw.rect(self.screen, color, self.rect)  # draw the rectangle
        # draw the sprite--rect is used because rect is already in the correct location
        # if self.pos was used, sprite would appear hovering on right wall
        self.screen.blit(sprite, (self.rect.x, self.rect.y))

        for effectBox in self.effectBoxes:  # draw the outline of the hitboxes
            # draw tethers and projectiles
            effectBox.draw()
            # pygame.draw.rect(self.screen, pygame.Color('Red'), hitbox.rect)

            outline = effectBox.mask.outline()
            # print('Outline exists: ' + str(len(outline) > 0))
            for point in outline:
                pygame.draw.circle(self.screen, pygame.Color('Red'),
                                   (point[0] + effectBox.rect.x, point[1] + effectBox.rect.y), 0)

    def update(self):  # operations that must be done every frame
        self.updateDeath()
        self.updateOrientation()
        if not self.frozen:
            self.move(self.xVelocity, self.yVelocity)
        self.updateCanAct()
        self.updateSprite()
        self.updateHurtbox()
        self.updateMoves()
        self.updateLeavingWall()

    def updateLeavingWall(self):
        if self.leavingCounter > -1:
            self.leavingCounter += 1

            if self.leavingCounter >= LEAVING_WALL_FRAMES:
                print('no longer leaving wall')
                self.leavingWall = []
                self.leavingCounter = -1

    def updateDeath(self):
        # if self.currMove == self.deathAnimation:
        #     print('current frame: ' + str(self.currMove.frame))

        if self.health <= 0 and not self.fallingToDeath and \
                not self.currMove == self.deathAnimation and not self.endTimer > -1:
            self.die()

        if -1 < self.endTimer < END_FRAMES:
            self.endTimer += 1
        elif self.endTimer > -1:
            self.game.end(self)

    def updateMoves(self):
        # clear hitboxes so they can be updated on the next frame
        self.effectBoxes = []

        for key, value in self.moves.items():
            value.update()

        self.tetherAnimation.update()
        self.shieldAnimation.update()
        self.jumpAnimation.update()
        self.deathAnimation.update()

    def updateCanAct(self):  # updates whether or not the character can act
        if self.hitstun != -1:
            self.hitstun -= 1

        if self.hitstun == 0:
            self.canAct = True
            self.hitstun = -1

    def updateHurtbox(self):  # makes sure the hurtbox matches the character's position
        self.rect = pygame.Rect(self.pos, self.dims)
        x = self.rect.x
        y = self.rect.y
        h = self.rect.h
        w = self.rect.w
        if self.orientation == 90:
            newDims = (h, w)
            newPos = (x + w - h, y - (w - h) / 2)
            self.rect = pygame.Rect(newPos, newDims)
        if self.orientation == 270:
            newDims = (h, w)
            newPos = (x, y + (h - w) / 2)
            self.rect = pygame.Rect(newPos, newDims)

    def updateOrientation(self):  # rotates the character so that it makes sense given its position
        if self.side == 'right':
            self.orientation = 270
        if self.side == 'down':
            self.orientation = 180
        if self.side == 'left':
            self.orientation = 90
        if self.side == 'up':
            self.orientation = 0
        if not self.onWall:
            self.orientation = 0

        # if self.onWall == [] and self.player == 1:
        #     self.lookingLeft = True
        # else:
        #     self.lookingLeft = False

    def updateSprite(self):
        if self.fallingToDeath:
            self.currSprite = self.deathAnimation.sprites[-1]
        elif self.health <= 0 and not self.currMove == self.deathAnimation:
            # print('lying dead')
            self.currSprite = self.finalSprite
        elif self.currMove is None:
            if self.onWall:
                self.currSprite = self.wallSprite
            else:  # **could change
                self.currSprite = self.defaultSprite
        self.dims = (self.currSprite[2], self.currSprite[3])
        self.image = self.spriteSheet.subsurface(self.currSprite).copy()

    def hitWall(self, wall):
        if wall == self.stage.bottomWall:
            print('collided with bottom wall')
            print('already on bottom wall: ' + str(wall in self.onWall))
        if wall not in self.onWall and not self.frozen:
            if self.health <= 0:
                print('hit wall with 0 health')
                print(self.onWall)
                if wall == self.stage.bottomWall:
                    print('bottom wall hit')
                    self.currSprite = self.finalSprite
                    self.fallingToDeath = False
                    self.endTimer = 0
                else:
                    return

            self.xVelocity = 0
            self.yVelocity = 0  # the character stops moving
            if wall == self.stage.bottomWall:
                print('hit bottom wall and stopped moving')
            self.canAct = True

            if self.currMove is not None and not isinstance(self.currMove, Jump):
                self.currMove.end()

            self.effectBoxes = []
            self.onWall.append(wall)
            self.updateSprite()

            sides = self.stage.wallSide(self, walls=self.onWall)

            # print('Sides: ' + str(sides))
            # print('Position: ' + str(self.pos))
            # print('Wall: ' + str(self.stage.walls[1]))

            for i in range(len(sides)):
                self.side = sides[i]
                wall = self.onWall[i]
                # make sure character is completely on the wall
                if self.side == 'right':
                    # noinspection PyUnresolvedReferences
                    self.pos = (wall.x + wall.w, self.pos[1])
                    # self.lookingLeft = False
                    # print('right')
                elif self.side == 'down':
                    self.pos = (self.pos[0], wall.y + wall.h)
                    # print('down')
                elif self.side == 'left':
                    self.pos = (wall.x - self.dims[0], self.pos[1])
                    # self.lookingLeft = True
                    # print('left')
                elif self.side == 'up':
                    self.pos = (self.pos[0], wall.y - self.dims[1])
                    # print('up')

            for wall in self.onWall:
                if wall == self.stage.walls[0]:
                    print('On left wall')
                if wall == self.stage.walls[1]:
                    print('On up wall')
                if wall == self.stage.walls[2]:
                    print('On right wall')
                if wall == self.stage.walls[3]:
                    print('On down wall')

    def leaveWall(self):
        self.leavingWall = self.onWall

        # for characters getting stuck in the corner
        for wall in self.stage.walls:
            if distance(self.rect, wall) < LEAVING_WALL_DISTANCE:
                self.leavingWall.append(wall)

        self.leavingCounter = 0
        self.onWall = []
        print('leaving wall')

    def moveOffWall(self):
        if self.onWall:
            for side in self.stage.wallSide(self, walls=self.onWall):
                if side == 'left':
                    self.move(-1 * MOVE_OFF_WALL[0], 0)
                if side == 'right':
                    self.move(MOVE_OFF_WALL[0], 0)
                if side == 'up':
                    self.move(0, -1 * MOVE_OFF_DOWN_WALL)
                if side == 'down':
                    self.move(0, MOVE_OFF_WALL[1])

            self.leaveWall()

    def hit(self, hitbox):  # get hit
        if self.health <= 0:
            print('no hitting should be occurring')
        self.health -= hitbox.damage  # take the appropriate amount of damage

        # update the health bar
        self.healthBar = pygame.Rect(0, 0, self.dims[0] * self.health / self.startingHealth, HEALTH_BAR_WIDTH)

        # Maybe change to: use the centers of each rectangle to determine the general direction the character will be sent in
        #  (i.e. the sign of the x and y velocity)
        #  the character will be sent in the opposite direction of the hurtbox
        #  the magnitude of the x and y velocity will be determined by the knockback and knockback angle of the hitbox
        # TODO: change how mass affects knockback
        if not self.onWall:
            if hitbox.char.lookingLeft:
                self.xVelocity = -1 * math.cos(math.radians(hitbox.angle)) * hitbox.knockback * self.mass
            else:
                self.xVelocity = math.cos(math.radians(hitbox.angle)) * hitbox.knockback * self.mass
            self.yVelocity = -1 * math.sin(math.radians(hitbox.angle)) * hitbox.knockback * self.mass

        # if hitbox.angle == 45:
        #     print('looking left: ' + str(hitbox.char.lookingLeft))
        #     print('cosine: ' + str(math.cos(math.radians(hitbox.angle))))
        #     print('x velocity: ' + str(self.xVelocity))

        if self.hitstun != -1:
            print('Combo!')
            # print('Hitstun: %d' % self.hitstun)

        self.canAct = False
        self.hitstun = int(hitbox.knockback * HITSTUN_CONSTANT)

        if self.currMove is not None:
            self.currMove.end()

        # print('Knockback: %d, Angle: %d, Damage: %d' % (hitbox.knockback, hitbox.angle, hitbox.damage))
        # print('Is currmove: ' + str(hitbox.move == self.game.playChars[0].currMove))

    def move(self, x, y):
        self.pos = (self.pos[0] + x, self.pos[1] + y)

    def forwardA(self):
        if self.canAct:
            print('forward A performed')
            self.moves['forwardA'].start()

    def upA(self):
        if self.canAct:
            print('up A performed')
            self.moves['upA'].start()

    def backA(self):
        if self.canAct:
            print('back A performed')
            self.moves['backA'].start()

    def downA(self):
        if self.canAct:
            print('down A performed')
            self.moves['downA'].start()

    def neutralA(self):
        if self.canAct:
            print('neutral A performed')
            self.moves['neutralA'].start()

    def upB(self):
        pass

    def downB(self):
        if self.canAct:
            print('down B performed')
            self.moves['downB'].start()

    def forwardB(self):
        pass

    def backB(self):
        pass

    def neutralB(self):
        pass

    def tether(self):
        if self.canAct:
            self.tetherAnimation.start()

    def throw(self, direction):
        if direction == 'right':
            print('Grabbing: ' + str(self.grabbing))
            self.tetherAnimation.end()

            if self.lookingLeft:
                print('back throw performed')
                self.moves['backThrow'].start()
                print('Grabbing: ' + str(self.grabbing))
            else:
                print('forward throw performed')
                self.moves['forwardThrow'].start()

        if direction == 'left':
            print('Grabbing: ' + str(self.grabbing))
            self.tetherAnimation.end()

            if self.lookingLeft:
                print('forward throw performed')
                self.moves['forwardThrow'].start()
            else:
                print('back throw performed')
                self.moves['backThrow'].start()
                print('Grabbing: ' + str(self.grabbing))

        if direction == 'up':
            self.tetherAnimation.end()

            print('up throw performed')
            self.moves['upThrow'].start()

        if direction == 'down':
            self.tetherAnimation.end()

            print('down throw performed')
            self.moves['downThrow'].start()

    def shield(self, angle):
        if self.canAct:
            if angle != -1:
                self.shieldAngle = angle
            else:
                self.shieldAngle = 0
            self.shieldAnimation.start()

    def boost(self, angle):
        xBoost = math.cos(math.radians(angle)) * self.jumpSpeed * SAME_BOOST_CONSTANT
        yBoost = -1 * math.sin(math.radians(angle)) * self.jumpSpeed * SAME_BOOST_CONSTANT

        # print('xBoost: ' + str(xBoost))
        # print('yBoost: ' + str(yBoost))
        #
        # print('x velocity: ' + str(self.xVelocity))
        # print('y velocity: ' + str(self.yVelocity))

        if math.copysign(1, xBoost) != math.copysign(1, self.xVelocity):
            print('x opposite')
            self.xVelocity = 0
            xBoost *= OPPOSITE_BOOST_CONSTANT

        if math.copysign(1, yBoost) != math.copysign(1, self.yVelocity):
            print('y opposite')
            self.yVelocity = 0
            yBoost *= OPPOSITE_BOOST_CONSTANT

        self.xVelocity += xBoost
        self.yVelocity += yBoost

        self.unfreeze()

    def freeze(self):
        print('frozen')
        self.frozen = True
        # self.xVelocity = 0
        # self.yVelocity = 0

    def unfreeze(self):
        print('unfrozen')
        self.frozen = False
        self.unfreezing = True

    def die(self):
        self.deathAnimation.start()

def distance(rect1, rect2):
    right1 = rect1.x + rect1.w
    right2 = rect2.x + rect2.w
    bottom1 = rect1.y + rect1.h
    bottom2 = rect2.y + rect2.h

    xDist = 0
    yDist = 0

    if right1 < rect2.x:
        xDist = rect2.x - right1

    if right2 < rect1.x:
        xDist = rect1.x - right2

    if bottom1 < rect2.y:
        yDist = rect2.y - bottom1

    if bottom2 < rect1.y:
        yDist = rect1.y - bottom2

    return min(xDist, yDist)

class TextButton:
    def __init__(self, text, size, textColor, rect, game):
        self.words = text
        self.textSize = size
        self.rect = rect
        self.game = game
        self.textColor = textColor

    def draw(self):
        pygame.draw.rect(self.game.screen, (0, 0, 0), self.rect, 2)
        self.game.displayText(self.words, self.textSize, self.rect, self.textColor)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


class ImageButton:
    def __init__(self, image, rect, text, textSize, game):
        self.image = image
        self.game = game
        self.rect = rect
        self.text = text
        self.textSize = textSize
        if self.text == 'Default':
            print('Button rect: ' + str(self.rect))
            print(IMAGE_BUTTON_SPACE)

    def draw(self):
        pygame.draw.rect(self.game.screen, (0, 0, 0), self.rect, 2)
        self.game.screen.blit(self.image, (self.rect[0] + IMAGE_BUTTON_SPACE, self.rect[1] + IMAGE_BUTTON_SPACE))

        xPos = self.rect.x
        yPos = self.rect.y + SELECT_TEXT_Y * self.rect.height
        length = self.rect.width
        height = self.rect.height - SELECT_TEXT_Y * self.rect.height
        self.game.displayText(self.text, self.textSize, pygame.Rect(xPos, yPos, length, height), TEXT_COLOR)

    def clicked(self, pos):
        # if self.text == 'Default':
        #     if self.rect.collidepoint(pos):
        #         print('click in range')
        #     else:
        #         print('Position: ' + str(pos))
        #         print('Rect: ' + str(self.rect))
        return self.rect.collidepoint(pos)
