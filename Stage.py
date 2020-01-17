import pygame

WALL_COLOR = (0, 0, 0)

class Stage:
    def __init__(self, walls, game):
        self.walls = walls
        self.leftWall = self.walls[0]
        self.rightWall = self.walls[2]
        self.game = game
        self.p1start = (self.game.wallWidth - 1, self.game.h / 2)
        self.p2start = (self.game.w - self.game.wallWidth, self.game.h / 2)

    def checkWalls(self, angle, walls, char):
        # check if a character that is on the given walls can jump off at the given angle
        # when different stages are added, this will become a stage method

        # pass in position of the character. use that to determine which side of a middle wall the character is on (in another method)
        left = False
        up = False
        right = False
        down = False  # whether the character is on each wall

        sides = self.wallSide(char, walls=walls)

        if 'left' in sides:
            left = True
        if 'up' in sides:
            up = True
        if 'right' in sides:
            right = True
        if 'down' in sides:
            down = True

        if right:
            if down:
                return 270 < angle < 360
            elif up:
                return 0 < angle < 90
            else:
                return 270 < angle < 360 or 0 <= angle < 90

        elif down:
            if left:
                return 180 < angle < 270
            else:
                return 180 < angle < 360

        elif left:
            if up:
                return 90 < angle < 180
            else:
                return 90 < angle < 270

        elif up:
            return 0 < angle < 180

        return False

    def wallSide(self, char, index=None, walls=None):
        # determines what side(s) of a wall a character is on given a wall index or
        # list of walls (this will be a stage method)
        if index is not None:
            walls = [self.walls[index]]

        # print(walls)
        # print(index)

        sides = []

        i = 0
        for wall in walls:
            # if char == self.playChars[0] and len(walls) > 1:
            #     if wall == self.walls[0]:
            #         print('Wall %d: left wall' % i)
            #     if wall == self.walls[1]:
            #         print('Wall %d: up wall' % i)
            #     if wall == self.walls[2]:
            #         print('Wall %d: right wall' % i)
            #     if wall == self.walls[3]:
            #         print('Wall %d: down wall' % i)

            if wall.x + wall.w - 1 <= char.pos[0]:
                sides.append('right')  # character is on the right side of the wall
            elif wall.x <= char.pos[0] < wall.x + wall.w - 1:
                if wall.y + wall.h - 1 <= char.pos[1]:
                    sides.append('down')  # character is below the wall
                elif char.pos[1] < wall.y:
                    sides.append('up')  # character is above the wall
                else:
                    char.center = ((char.pos[0] + char.dims[0]) / 2, (char.pos[1] + char.dims[1]) / 2)
                    r = wall.x + wall.w - 1 - char.center[0]  # how close a character is to the right side of the wall
                    l = char.center[0] - wall.x  # ' ' left side
                    t = char.center[1] - wall.y  # ' ' top
                    b = wall.y + wall.h - 1 - char.center[1]  # ' ' bottom

                    if min(r, l, t, b) == r:
                        sides.append('right')
                    elif min(r, l, t, b) == b:
                        sides.append('down')
                    elif min(r, l, t, b) == l:
                        sides.append('left')
                    else:
                        sides.append('up')

            else:  # char.pos[0] < wall.x
                sides.append('left')  # character is on the left side of the wall

            # print('Side: ' + sides[i])
            # print('i: ' + str(i))
            i += 1

        return sides

    def draw(self):
        for wall in self.walls:
            pygame.draw.rect(self.game.screen, WALL_COLOR, wall)

    def image(self, width, height):
        img = pygame.Surface((width, height))
        img.fill(pygame.Color('White'))

        for wall in self.walls:
            print('Wall: ' + str(wall))
            xPos = wall.x / self.game.w * width
            yPos = wall.y / self.game.h * height
            miniWidth = wall.width / self.game.w * width
            miniHeight = wall.height / self.game.h * height
            miniWall = pygame.Rect(xPos, yPos, miniWidth, miniHeight)
            img.fill(pygame.Color('Grey'), miniWall)

        return img
