import pygame

# TODO: change this
THROW_START = (479, 2014)


class Animation:
    def __init__(self, frameData, sprites, tetherFile, game, char):
        self.activeframe = int(frameData[0])  # when the hitbox comes out
        self.inactiveframe = int(frameData[1])  # when the hitbox goes away
        self.endframe = int(frameData[2])  # when the endlag stops

        self.game = game  # the game object
        self.char = char  # the character the move belongs to

        # sprites of the character when the move is active, in order of when they appear
        self.sprites = sprites
        # print(spriteFile)
        if tetherFile:
            self.spriteFile = char.tetherFile
        else:
            self.spriteFile = char.spriteFile
        self.spriteSheet = pygame.image.load(self.spriteFile).convert()
        self.spriteSheet.set_colorkey((255, 0, 255))

        self.active = False

        self.spriteIndex = 0

        self.frame = -1  # how many frames the move has been out (starting at 1)
        self.frameWait = (self.inactiveframe - self.activeframe) / len(self.sprites)
        if self.frameWait % 1 != 0:
            raise ValueError('Number of frames move is active is not divisible by number of sprites ')

        self.frameWait = int(self.frameWait)

        self.paused = False

    def update(self):
        # print('tether updating')
        if self.frame > -1:
            # print('tether advancing frames')
            if not self.paused:
                # print('tether not paused')
                self.frame += 1

                if self.frame >= self.endframe:
                    self.end()
                elif self.activeframe <= self.frame < self.inactiveframe:
                    if self.frame != self.activeframe:
                        if (self.frame - self.activeframe) % self.frameWait == 0:
                            self.spriteIndex += 1
                            # print('Frame: %d, sprite index: %d' % (self.frame, self.spriteIndex))
                    else:
                        self.active = True
                    self.act()

            else:
                self.act()

    def start(self):
        # print("tether starting")
        self.frame = 0
        self.char.currMove = self
        self.char.canAct = False

    def end(self):
        self.frame = -1
        self.spriteIndex = 0

        self.char.currMove = None
        self.char.currSprite = self.char.defaultSprite
        self.char.canAct = True

        self.active = False
        self.paused = False

    def deactivate(self):
        print('deactivating')
        self.active = False

    def act(self):
        pass


class Attack(Animation):
    def __init__(self, frameData, damage, knockback, angle, hitboxes, sprites, throw, throwLocation, game, char):
        super().__init__(frameData, sprites, throw, game, char)
        # other attributes can be added later including multiple hitboxes, etc.

        # if self.spriteFile == self.char.tetherFile:
        #     print('Knockback: %d, Angle: %d, Damage: %d' % (knockback, angle, damage))

        self.damage = damage  # amount of damage the move deals
        self.knockback = knockback  # how far the move sends the other character
        self.angle = angle  # what angle the other character is sent at

        # location of the hitboxes of the move (relative to the character's position), in order of when they appear
        self.hitboxes = hitboxes

        self.throw = throw  # whether the move is a throw
        self.throwLocation = throwLocation

    def act(self):
        # print(self.spriteIndex)
        self.char.currSprite = self.sprites[self.spriteIndex]

        if self.active:
            # hitbox location, aligned with the character's location
            loc = self.hitboxes[self.spriteIndex]

            # create a hitbox with the relevant properties and add it to the character's list of active hitboxes
            self.char.hitboxes.append(
                Hitbox(loc, self.damage, self.knockback, self.angle, self.char.lookingLeft, self.throw, self.throwLocation, self))

            # if self.throw:
            #     print('Adding throw hitbox at ' + str(loc))


class Tether(Animation):
    def __init__(self, frameData, startPos, grabBoxes, sprites, game, char):
        super().__init__(frameData, sprites, True, game, char)
        self.grabBoxes = grabBoxes
        self.startPos = startPos

    def act(self):
        self.char.currSprite = self.sprites[self.spriteIndex]

        # print('Active: ' + str(self.active))

        if self.active:
            # print('Index: ' + str(self.spriteIndex))

            # hitbox location (later becomes aligned with the character's location)
            loc = self.grabBoxes[self.spriteIndex]

            # create a hitbox with the relevant properties and add it to the character's list of active hitboxes
            self.char.hitboxes.append(GrabBox(loc, self.startPos, self.char.lookingLeft, self))

    def pause(self):
        self.paused = True

    def deactivate(self):
        self.pause()

    def end(self):
        super().end()

        if self.char.grabbing is not None:
            # print("On wall: " + str(self.char.grabbing.onWall))
            self.char.frozen = False
            self.char.grabbing.frozen = False
            self.char.grabbing.leaveWall()
            self.char.grabbing = None

# shield class?

class Hitbox(pygame.sprite.Sprite):
    def __init__(self, shape, damage, knockback, angle, flipped, throw, throwLocation, move):
        pygame.sprite.Sprite.__init__(self)

        self.shape = shape
        self.damage = damage
        self.knockback = knockback
        self.angle = angle  # knockback angle
        self.move = move
        self.char = self.move.char
        self.spriteSheet = self.move.spriteSheet

        print("Throw location: " + str(throwLocation))

        if not throw:
            if not flipped:
                xOffset = self.shape.x - self.char.currSprite[0]
                yOffset = self.shape.y - self.char.currSprite[1]
            else:
                xOffset = self.char.currSprite[0] + self.char.currSprite[2] - (self.shape.x + self.shape.width)
                yOffset = self.shape.y - self.char.currSprite[1]
        else:
            xOffset = throwLocation[0] - self.char.currSprite[0]
            yOffset = throwLocation[1] - self.char.currSprite[1]

        xPos = self.char.pos[0] + xOffset
        yPos = self.char.pos[1] + yOffset

        # print("Shape.x: %d\nCurrsprite.x: %d" % (self.shape.x, self.char.currSprite[0]))
        # print("Char pos: %d\nHitbox pos: %d" % (self.char.pos[0], xPos))

        self.rect = pygame.Rect(xPos, yPos, self.shape.width, self.shape.height)
        # print(self.shape)
        self.image = self.spriteSheet.subsurface(self.shape).copy()

        print('Self.rect: ' + str(self.rect))
        print('currSprite location: (%d,%d)' % (self.char.currSprite[0], self.char.currSprite[1]))

        if flipped:
            self.image = pygame.transform.flip(self.image, True, False)

        self.mask = pygame.mask.from_surface(self.image)

    def hit(self, char):
        if self.move.throw:
            print('throw lands')
        # print('hitbox hit')
        char.hit(self)

    # for tethers and projectiles
    def draw(self):
        pass


class GrabBox(Hitbox):
    def __init__(self, rect, startPos, flipped, move):
        super().__init__(rect, None, None, None, flipped, False, [], move)

        if not flipped:
            xOffset = startPos[0]
        else:
            xOffset = self.char.dims[0] - startPos[0]

        self.rect = self.rect.move((self.char.pos[0] + xOffset - self.rect.x,
                                    self.char.pos[1] + startPos[1] - self.rect.y))

    # both characters are stopped in place, self.char gets to throw opposing char
    def hit(self, char):
        if self.move.active and not self.move.paused:
            # print('tether hit')
            char.xVelocity = 0
            char.yVelocity = 0
            char.canAct = False
            char.frozen = True

            char.moveOffWall()

            self.char.xVelocity = 0
            self.char.yVelocity = 0
            self.char.canAct = False
            self.char.frozen = True
            self.char.grabbing = char

    def draw(self):
        self.move.game.screen.blit(self.image, (self.rect.x, self.rect.y))


class Projectile(Hitbox):
    def __init__(self, image):
        pass
        # init the hitbox

        # self.image =
        # self.velocity = (x,y)

    def update(self):
        pass
        # move based on velocity

    def draw(self):
        pass
