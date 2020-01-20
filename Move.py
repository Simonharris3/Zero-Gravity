import pygame

# THROW_WIDTH = 1000
# THROW_HEIGHT = 1000

SHIELD_MULTIPLE = 45
SHIELD_KNOCKBACK = 3


class Animation:
    def __init__(self, frameData, sprites, specialFile, game, char):
        self.activeframe = int(frameData[0])  # when the hitbox comes out
        self.inactiveframe = int(frameData[1])  # when the hitbox goes away
        self.endframe = int(frameData[2])  # when the endlag stops

        self.game = game  # the game object
        self.char = char  # the character the move belongs to

        # sprites of the character when the move is active, in order of when they appear
        self.sprites = sprites
        # print(spriteFile)
        if specialFile is not None:
            if specialFile == 'tether':
                self.spriteFile = char.tetherFile
            if specialFile == 'shield':
                self.spriteFile = char.shieldFile
        else:
            self.spriteFile = char.spriteFile
        self.spriteSheet = pygame.image.load(self.spriteFile).convert()
        self.spriteSheet.set_colorkey((255, 0, 255))

        self.active = False

        self.spriteIndex = 0

        self.frame = -1  # how many frames the move has been out (starting at 1)
        # how many frames each sprite lasts for
        self.frameWait = (self.inactiveframe - self.activeframe) / len(self.sprites)
        if self.frameWait % 1 != 0:
            raise ValueError('Number of frames move is active is not divisible by number of sprites ')

        self.frameWait = int(self.frameWait)

        self.paused = False

    def update(self):
        # if isinstance(self, Shield):
        #     print('shield updating, frame ' + str(self.frame))
        if self.frame > -1:
            # if isinstance(self, Shield):
            #     print('shield advancing frames')
            if not self.paused:
                # if isinstance(self, Shield):
                #     print('shield not paused')
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
        # if isinstance(self, Shield):
        #     print('shield starting')
        self.frame = 0
        self.char.currMove = self
        self.char.canAct = False
        # print('frame: ' + str(self.frame))

    def end(self):
        # print('shield ending')
        self.frame = -1
        self.spriteIndex = 0

        self.char.currMove = None
        self.char.currSprite = self.char.defaultSprite
        self.char.canAct = True

        self.active = False
        self.paused = False

    def deactivate(self):
        # print('deactivating')
        self.active = False

    def act(self):
        pass


class Attack(Animation):
    def __init__(self, frameData, damage, knockback, angle, hitboxes, sprites, game, char):
        super().__init__(frameData, sprites, None, game, char)
        # other attributes can be added later including multiple hitboxes, etc.

        # if self.spriteFile == self.char.tetherFile:
        #     print('Knockback: %d, Angle: %d, Damage: %d' % (knockback, angle, damage))

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

            # create a hitbox with the relevant properties and add it to the character's list of active hitboxes
            self.char.effectBoxes.append(Hitbox(loc, self.damage, self.knockback, self.angle, self.char.lookingLeft, self))

            # if self.throw:
            #     print('Adding throw hitbox at ' + str(loc))


class Throw(Attack):
    def __init__(self, frames, damage, knockback, angle, hitboxes, sprites, game, char):
        super().__init__(frames, damage, knockback, angle, hitboxes, sprites, game, char)

    def act(self):
        self.char.currSprite = self.sprites[self.spriteIndex]

        if self.active:
            self.char.opponent.hit(ThrowHitbox(self.damage, self.knockback, self.angle, self))
            self.char.xVelocity = -1 * self.char.opponent.xVelocity
            self.char.yVelocity = -1 * self.char.opponent.yVelocity
            self.deactivate()


class Tether(Animation):
    def __init__(self, frameData, startPos, grabBoxes, sprites, game, char):
        super().__init__(frameData, sprites, 'tether', game, char)
        self.grabBoxes = grabBoxes
        self.startPos = startPos

    def act(self):
        self.char.currSprite = self.sprites[self.spriteIndex]

        # print('Active: ' + str(self.active))

        if self.active:
            # print('Index: ' + str(self.spriteIndex))

            # hitbox location for the sprite (later becomes aligned with the character's location)
            rect = self.grabBoxes[self.spriteIndex]

            # create a hitbox with the relevant properties and add it to the character's list of active hitboxes
            self.char.effectBoxes.append(GrabBox(rect, self.startPos, self.char.lookingLeft, self))

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


class Shield(Animation):
    def __init__(self, startPositions, rect, char):
        self.startPositions = startPositions
        self.rect = rect
        super().__init__([1, 2, 2], [char.defaultSprite], 'shield', char.game, char)

    def act(self):
        # print('shield active: ' + str(self.active))
        if self.active:
            # angle = (self.char.shieldAngle + 180) % 360
            self.char.effectBoxes.append(ShieldBox(self.rect, self.startPositions, self.char.shieldAngle, self))


class EffectBox(pygame.sprite.Sprite):
    def __init__(self, shape, flipped, move):
        pygame.sprite.Sprite.__init__(self)

        self.shape = shape
        self.move = move
        self.char = self.move.char
        self.spriteSheet = self.move.spriteSheet

        if not flipped:
            xOffset = self.shape.x - self.char.currSprite[0]
        else:
            xOffset = self.char.currSprite[0] + self.char.currSprite[2] - (self.shape.x + self.shape.width)
        yOffset = self.shape.y - self.char.currSprite[1]

        xPos = self.char.pos[0] + xOffset
        yPos = self.char.pos[1] + yOffset

        self.rect = pygame.Rect(xPos, yPos, self.shape.width, self.shape.height)

        self.image = self.spriteSheet.subsurface(self.shape).copy()

        if flipped:
            self.image = pygame.transform.flip(self.image, True, False)

        self.mask = pygame.mask.from_surface(self.image)

    def hit(self, obj):
        pass

    def draw(self):
        pass


class Hitbox(EffectBox):
    def __init__(self, shape, damage, knockback, angle, flipped, move):
        super().__init__(shape, flipped, move)

        self.damage = damage
        self.knockback = knockback
        self.angle = angle  # knockback angle

    def hit(self, char):
        # print('hitbox hit')
        char.hit(self)


class ShieldBox(EffectBox):
    def __init__(self, rect, startPositions, angle, move):
        super().__init__(rect, False, move)
        print('angle: ' + str(angle))

        self.angle = angle
        startPos = startPositions[int(angle / SHIELD_MULTIPLE)]
        self.image = pygame.transform.rotate(self.image, angle + 90)
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.rect.move((self.char.pos[0] + startPos[0] - self.rect.x,
                                    self.char.pos[1] + startPos[1] - self.rect.y))

    def hit(self, hitbox):
        if self.char.lookingLeft:
            angle = flip(self.angle)
        else:
            angle = self.angle
        hitbox.char.hit(Hitbox(pygame.Rect(0, 0, 0, 0), 0, SHIELD_KNOCKBACK, angle, False, self.move))
        # self.char.hitstun = shield stun

    def draw(self):
        # print('draw shield at: ' + str((self.rect.x, self.rect.y)))
        self.move.game.screen.blit(self.image, (self.rect.x, self.rect.y))


class GrabBox(EffectBox):
    def __init__(self, rect, startPos, flipped, move):
        super().__init__(rect, flipped, move)

        if not flipped:
            xOffset = startPos[0]
        else:
            xOffset = self.char.dims[0] - startPos[0] - self.rect.width

        self.rect = self.rect.move((self.char.pos[0] + xOffset - self.rect.x,
                                    self.char.pos[1] + startPos[1] - self.rect.y))

    # both characters are stopped in place, self.char gets to throw opposing char
    def hit(self, char):
        if self.move.active and not self.move.paused:
            # print('tether hit')
            char.canAct = False
            char.frozen = True

            char.moveOffWall()

            self.char.canAct = False
            self.char.frozen = True
            self.char.grabbing = char

    def draw(self):
        # self.image = pygame.transform.rotate(self.image, 45)
        self.move.game.screen.blit(self.image, (self.rect.x, self.rect.y))


class ThrowHitbox(Hitbox):
    def __init__(self, damage, knockback, angle, move):
        super().__init__(pygame.Rect(0, 0, 0, 0), damage, knockback, angle, False, move)

# class Projectile(Hitbox):
# def __init__(self, image):
#   pass
# init the hitbox

# self.image =
# self.velocity = (x,y)

# def update(self):
#     pass
#     # move based on velocity
#
# def draw(self):
#     pass

def flip(angle):
    if angle == 0:
        return 180
    if angle == 45 or angle == 225:
        return angle + 90
    if angle == 315 or angle == 135:
        return angle - 90
    if angle == 180:
        return 0
