import matplotlib as plt
from Constants import *
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys
import time

class Dashboard:
    def __init__(self, queue):
        self.population = None

    def start(self):
        pass



class RealTime:
    def __init__(self, queue):
        self.queue = queue
        pygame.init()
        self.screen = pygame.display.set_mode(RESOLUTION)
        self.clock = pygame.time.Clock()
        self.screen.fill(BLACK)

    def start(self):
        counter = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            self.screen.fill(BLACK)
            df, current_time = self.queue.get()
            self.draw_population(df)
            self.draw_info(current_time)
            pygame.display.update()
            self.clock.tick(FPS_DISPLAY)
            # counter += 1
            # if counter == 30:
            #     print(self.clock.get_fps())
            #     counter = 0

    def draw_population(self, df):
        size = int(0.5/SCALE_MPP)
        for _, row in df[df['infected']][['pos_x', 'pos_y']].iterrows():
            pygame.draw.circle(self.screen, (255, 0, 0), (row.pos_x, row.pos_y), size)
        for _, row in df[df['immune']][['pos_x', 'pos_y']].iterrows():
            pygame.draw.circle(self.screen, (255, 255, 255), (row.pos_x, row.pos_y), size)
        for _, row in df[(df['healthy']) & (~df['immune'])][['pos_x', 'pos_y']].iterrows():
            pygame.draw.circle(self.screen, (0, 255, 0), (row.pos_x, row.pos_y), size)

    def draw_info(self, current_time):
        font = pygame.font.SysFont(None, 24)
        img = font.render(current_time.strftime('%d/%m/%Y %H:%M:%S'), True, (0, 255, 0))
        self.screen.blit(img, (20, 20))