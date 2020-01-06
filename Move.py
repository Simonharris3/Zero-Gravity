import pygame

class Move:
    def __init__(self, frameData, damage, knockback, angle, hitboxes, sprites, game, char):
        # other attributes can be added later including multiple hitboxes, etc.
        # not sure if the hitbox should include a hurtbox as well since if it does, that will lead to lots of trades
        self.activeframe = int(frameData[0])  # when the hitbox comes out
        self.inactiveframe = int(frameData[1])  # when the hitbox goes away
        self.endframe = int(frameData[2])  # when the endlag stops

        # location of the hitboxes of the move (relative to the character's position), in order of when they appear
        self.hitboxes = hitboxes
        # sprites of the character when the move is active, in order of when they appear
        self.sprites = sprites

        self.damage = damage  # amount of damage the move deals
        self.knockback = knockback  # how far the move sends the other character
        self.angle = angle  # what angle the other character is sent at

        self.game = game  # the game object
        self.char = char  # the character the move belongs to

        self.frame = -1  # how many frames the move has been out (starting at 1)
        self.frameWait = int((self.inactiveframe - self.activeframe) / len(self.sprites))
        self.spriteIndex = 0

        self.hitboxActive = False

        # if self.inactiveframe == 25:
        #     print("Frame wait: " + str(self.frameWait))
        #     print("Num sprites: " + str(len(sprites)))

        if self.char.player == 1:
            for i in range(len(self.hitboxes)):
                self.hitboxes[i] = self.hitboxes[i].move(-1 * self.hitboxes[i].x, 0)

    def start(self):
        self.frame = 0
        self.char.currMove = self

    def activate(self):
        self.char.currSprite = self.sprites[self.spriteIndex]

        if self.hitboxActive:
            # hitbox location, aligned with the character's location
            loc = self.hitboxes[self.spriteIndex].move(self.char.pos[0], self.char.pos[1])

            # create a hitbox with the relevant properties and add it to the character's list of active hitboxes
            self.char.hitboxes.append(Hitbox(loc, self.damage, self.knockback, self.angle, self))

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

class Hitbox:
    def __init__(self, points, damage, knockback, angle, move):
        self.shape = points
        self.damage = damage
        self.knockback = knockback
        self.angle = angle  # knockback angle
        self.move = move

    # def move(self, x, y):
    #     self.rect = self.rect.move(x, y)

class Projectile(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)

        # self.image =
        # self.hitbox =
        # self.velocity = (x,y)

    def update(self):
        pass
        # move based on velocity
