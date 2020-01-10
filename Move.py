import pygame

class Animation:
    def __init__(self, frameData, sprites, game, char):
        self.activeframe = int(frameData[0])  # when the hitbox comes out
        self.inactiveframe = int(frameData[1])  # when the hitbox goes away
        self.endframe = int(frameData[2])  # when the endlag stops

        self.game = game  # the game object
        self.char = char  # the character the move belongs to

        # sprites of the character when the move is active, in order of when they appear
        self.sprites = sprites
        self.spriteSheet = self.char.spriteSheet

        self.active = False

        self.spriteIndex = 0

        self.frame = -1  # how many frames the move has been out (starting at 1)
        self.frameWait = (self.inactiveframe - self.activeframe) / len(self.sprites)
        if self.frameWait % 1 != 0:
            raise ValueError('Number of frames move is active is not divisible by number of sprites ')

        self.frameWait = int(self.frameWait)

        self.paused = False

    def update(self):
        if self.frame > -1:
            if not self.paused:
                self.frame += 1

                if self.frame >= self.endframe:
                    self.end()
                elif self.activeframe <= self.frame < self.inactiveframe:
                    if self.frame != self.activeframe:
                        if (self.frame - self.activeframe) % self.frameWait == 0:
                            self.spriteIndex += 1
                    else:
                        self.active = True
                    self.act()

    def start(self):
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
        self.active = False

    def act(self):
        pass

class Attack(Animation):
    def __init__(self, frameData, damage, knockback, angle, hitboxes, sprites, game, char):
        super().__init__(frameData, sprites, game, char)
        # other attributes can be added later including multiple hitboxes, etc.

        self.damage = damage  # amount of damage the move deals
        self.knockback = knockback  # how far the move sends the other character
        self.angle = angle  # what angle the other character is sent at

        # location of the hitboxes of the move (relative to the character's position), in order of when they appear
        self.hitboxes = hitboxes

    def act(self):
        # print(self.spriteIndex)
        self.char.currSprite = self.sprites[self.spriteIndex]

        if self.active:
            # hitbox location, aligned with the character's location
            loc = self.hitboxes[self.spriteIndex]
            # move hitboxes to the left side of the character if it's player 2
            # if self.char.lookingLeft:
            #     print("Moving from %d to %d" % (loc.x, -1 * loc.x))
            #     loc = loc.move(-1 * loc.x, 0)

            # create a hitbox with the relevant properties and add it to the character's list of active hitboxes
            self.char.hitboxes.append(Hitbox(loc, self.damage, self.knockback, self.angle, self.char.lookingLeft, self))

class Tether(Animation):
    def __init__(self, frameData, startPos, grabBoxes, sprites, game, char):
        super().__init__(frameData, sprites, game, char)
        self.grabBoxes = grabBoxes
        self.spriteSheet = char.tetherFile
        self.startPos = startPos

    def act(self):
        # print(self.spriteIndex)
        self.char.currSprite = self.sprites[self.spriteIndex]

        if self.active:
            # hitbox location (later becomes aligned with the character's location)
            loc = self.grabBoxes[self.spriteIndex]

            # create a hitbox with the relevant properties and add it to the character's list of active hitboxes
            self.char.hitboxes.append(GrabBox(loc, self.startPos, self.char.lookingLeft, self))

    def pause(self):
        self.deactivate()
        self.paused = True

#shield class?

class Hitbox(pygame.sprite.Sprite):
    def __init__(self, shape, damage, knockback, angle, flipped, move):
        pygame.sprite.Sprite.__init__(self)

        self.shape = shape
        self.damage = damage
        self.knockback = knockback
        self.angle = angle  # knockback angle
        self.move = move
        self.char = self.move.char
        self.spriteSheet = self.move.spriteSheet

        if not flipped:
            xOffset = self.shape.x - self.char.currSprite[0]
        else:
            xOffset = self.char.currSprite[0] + self.char.currSprite[2] - (self.shape.x + self.shape.width)

        xPos = self.char.pos[0] + xOffset
        yPos = self.char.pos[1] + self.shape.y - self.char.currSprite[1]

        # print("Shape.x: %d\nCurrsprite.x: %d" % (self.shape.x, self.char.currSprite[0]))
        # print("Char pos: %d\nHitbox pos: %d" % (self.char.pos[0], xPos))

        self.rect = pygame.Rect(xPos, yPos, self.shape.width, self.shape.height)
        self.image = self.spriteSheet.subsurface(self.shape).copy()

        # print('Self.shape: ' + str(self.shape))
        # print('currSprite location: (%d,%d)' % (self.char.currSprite[0], self.char.currSprite[1]))

        if flipped:
            self.image = pygame.transform.flip(self.image, True, False)

        self.mask = pygame.mask.from_surface(self.image)

    def hit(self, char):
        char.hit(self)

    # for tethers and projectiles
    def draw(self):
        pass

class GrabBox(Hitbox):
    def __init__(self, rect, startPos, flipped, move):
        super().__init__(rect, None, None, None, flipped, move)
        self.startPos = startPos
        self.rect.move(startPos[0], startPos[1])

    def hit(self, char):
        char.xVelocity = 0
        char.yVelocity = 0
        char.canAct = False
        char.frozen = True
        self.char.grabbing = True
        # opposing character is stopped in place, self.char gets to throw it

    def draw(self):
        print("drawing tether")
        self.move.game.screen.blit(self, self.startPos)

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