import pygame

class Move:
    def __init__(self, frameData, damage, knockback, angle, hitboxes, sprites, game, char):
        # other attributes can be added later including multiple hitboxes, etc.
        # not sure if the hitbox should include a hurtbox as well since if it does, that will lead to lots of trades
        self.activeframe = int(frameData[0])  # when the hitbox comes out
        self.inactiveframe = int(frameData[1])  # when the hitbox goes away
        self.endframe = int(frameData[2])  # when the endlag stops

        self.game = game  # the game object
        self.char = char  # the character the move belongs to

        # location of the hitboxes of the move (relative to the character's position), in order of when they appear
        self.hitboxes = hitboxes
        # sprites of the character when the move is active, in order of when they appear
        self.sprites = sprites
        self.spriteSheet = self.char.spriteSheet

        self.damage = damage  # amount of damage the move deals
        self.knockback = knockback  # how far the move sends the other character
        self.angle = angle  # what angle the other character is sent at

        self.frame = -1  # how many frames the move has been out (starting at 1)
        self.frameWait = (self.inactiveframe - self.activeframe) / len(self.sprites)
        if self.frameWait % 1 != 0:
            raise ValueError("Number of frames move is active is not divisible by number of sprites ")

        self.frameWait = int(self.frameWait)

        self.spriteIndex = 0

        self.hitboxActive = False

        # if self.inactiveframe == 25:
        #     print("Frame wait: " + str(self.frameWait))
        #     print("Num sprites: " + str(len(sprites)))

        # move hitboxes to the left side of the character if it's player 2
        if self.char.player == 1:
            for i in range(len(self.hitboxes)):
                self.hitboxes[i][0] = self.hitboxes[i][0].move(-1 * self.hitboxes[i][0].x, 0)

    def start(self):
        self.frame = 0
        self.char.currMove = self

    def activate(self):
        print(self.spriteIndex)
        self.char.currSprite = self.sprites[self.spriteIndex]

        if self.hitboxActive:
            # hitbox location, aligned with the character's location
            hitboxData = self.hitboxes[self.spriteIndex]
            loc = hitboxData[0]
            isolateHitbox = True

            if hitboxData[-1] is None:
                isolateHitbox = False

            # create a hitbox with the relevant properties and add it to the character's list of active hitboxes
            self.char.hitboxes.append(Hitbox(loc, self.damage, self.knockback, self.angle,
                                             isolateHitbox, hitboxData[1], self))

    def update(self):
        if self.frame > -1:
            self.frame += 1

            if self.frame >= self.endframe:
                self.end()
            elif self.activeframe <= self.frame < self.inactiveframe:
                if self.frame != self.activeframe:
                    if (self.frame - self.activeframe) % self.frameWait == 0:
                        self.spriteIndex += 1
                else:
                    self.hitboxActive = True
                self.activate()
            elif self.frame >= self.inactiveframe:
                self.char.hitboxes = []
                # this means all hitboxes are removed when one goes away--not sure if that's what i want (but good enough for now)

    def end(self):
        self.frame = -1
        self.spriteIndex = 0

        self.char.currMove = None
        self.char.currSprite = self.char.defaultSprite
        self.char.canAct = True

        self.hitboxActive = False

    def deactivate(self):
        self.hitboxActive = False


class Hitbox(pygame.sprite.Sprite):
    def __init__(self, points, damage, knockback, angle, isolateHitbox, color, move):
        pygame.sprite.Sprite.__init__(self)

        self.shape = points
        self.damage = damage
        self.knockback = knockback
        self.angle = angle  # knockback angle
        self.move = move
        self.char = self.move.char
        self.spriteSheet = self.move.spriteSheet

        xPos = self.char.pos[0] + self.shape.x - self.char.currSprite[0]
        yPos = self.char.pos[1] + self.shape.y - self.char.currSprite[1]
        self.rect = pygame.Rect(xPos, yPos, self.shape.width, self.shape.height)

        # print("Self.shape: " + str(self.shape))
        # print("currSprite location: (%d,%d)" % (self.char.currSprite[0], self.char.currSprite[1]))

        self.image = self.spriteSheet.subsurface(self.shape).copy()
        if isolateHitbox:
            self.color = color
            self.mask = self.isolateHitbox()
        else:
            self.mask = pygame.mask.from_surface(self.image)

    # def move(self, x, y):
    #     self.rect = self.rect.move(x, y)

    def isolateHitbox(self):
        pixelArray = pygame.PixelArray(self.image)
        pixelArray = pixelArray.extract(self.color)
        mask_surface = pixelArray.make_surface()
        mask_surface.set_colorkey((0, 0, 0))
        mask = pygame.mask.from_surface(mask_surface)
        pixelArray.close()
        return mask


class Projectile(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)

        # self.image =
        # self.hitbox =
        # self.velocity = (x,y)

    def update(self):
        pass
        # move based on velocity
