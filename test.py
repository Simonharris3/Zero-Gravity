# import pygame
# import time
#
# pygame.init()  # start pygame
# screen = pygame.display.set_mode((700, 300))  # create the screen
# # screen.fill(pygame.Color('Blue'))  # fill the screen with blue
# #
# # rect = pygame.Rect(0, 0, 100, 50)
# # screen.fill(pygame.Color('Red'), rect)
# # pygame.display.flip()  # open the screen
# # time.sleep(4)
# #
# # rect = pygame.Rect(0, 0, 50, 100)
# # screen.fill(pygame.Color('Red'), rect)
# # pygame.display.flip()
# # time.sleep(4)
#
# outline = []
#
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#     spriteSheet = pygame.image.load("simonbelmont.png").convert()
#     spriteSheet.set_colorkey((255, 0, 255))  # remove background color
#     image = spriteSheet.subsurface(239, 4464, 180, 20).copy()
#     # pixelArray = pygame.PixelArray(image)
#     # pixelArray = pixelArray.extract((230, 230, 230))
#     # mask_surface = pixelArray.make_surface()
#     # mask_surface.set_colorkey((0, 0, 0))
#     # mask = pygame.mask.from_surface(mask_surface)
#     # pixelArray.close()
#     # outline = mask.outline()
#     screen.blit(image, (460, 231))
#     screen.blit(image, (0, 0))
#     for point in outline:
#         pygame.draw.circle(screen, pygame.Color("Red"), point, 0)
#     pygame.display.flip()
#
# print("Outline length: %d" % len(outline))
# pygame.quit()