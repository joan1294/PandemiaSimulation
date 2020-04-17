import matplotlib.pyplot as plt
import matplotlib.animation as animation
import calendar
from Constants import *
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
# pygame.HWSURFACE = True
pygame.DOUBLEBUF = True
import pandas as pd
import numpy as np
import time
import matplotlib.dates as mdates

months = mdates.MonthLocator()

class Dashboard:
    def __init__(self, queue):
        self.population = INITIAL_POPULATION
        self.queue = queue
        fig, ax = plt.subplots()
        self.fig = fig
        self.ax = ax
        self.ax.autoscale(enable=True, axis='both', tight=None)
        self.time_axis = []
        self.healthy = []
        self.infected_undetected = []
        self.dead = []
        self.immune = []
        self.infected_detected = []
        self.n_labels = 8
        self.measures = {'start_weak_confinement': [], 'start_strong_confinement': [],
                         'release_weak_confinement': [], 'release_strong_confinement': []}
        self.old_weak_confinement = False
        self.old_strong_confinement = False

    def start(self):
        ani = animation.FuncAnimation(self.fig, self.plot_dashboard, interval=1)
        plt.show()

    def plot_dashboard(self, frame):
        df, current_time, weak_confinement, strong_confinement = self.queue.get()
        self.add_new_data(df, current_time, weak_confinement, strong_confinement)
        self.ax.clear()
        self.ax.stackplot(self.time_axis, self.dead, self.infected_detected, self.infected_undetected, self.healthy, self.immune,
                          labels=['dead', 'infected detected', 'infected_undetected', 'healthy', 'immune'],
                          colors=('black', 'red', 'orange', 'green', 'blue'))
        plt.xlabel = 'Time'
        plt.ylabel = 'Population'
        self.build_xtics()
        self.draw_measures_applied()
        self.ax.legend(loc='upper left')

    def add_new_data(self, df, current_time, weak_confinement, strong_confinement):
        self.time_axis.append(current_time)#.strftime('%d/%m/%Y %H:%M:%S'))
        self.healthy.append(df[~df['immune']].healthy.sum())
        self.infected_undetected.append(df[~df['detected']].infected.sum())
        self.infected_detected.append(df.detected.sum())
        self.dead.append(df.dead.sum())
        self.immune.append(df.immune.sum())
        if not self.old_weak_confinement and weak_confinement:
            self.measures['start_weak_confinement'].append(current_time)
        elif not self.old_strong_confinement and strong_confinement:
            self.measures['start_strong_confinement'].append(current_time)
        if self.old_weak_confinement and not weak_confinement:
            self.measures['release_weak_confinement'].append(current_time)
        elif self.old_strong_confinement and not strong_confinement:
            self.measures['release_strong_confinement'].append(current_time)
        self.old_weak_confinement = weak_confinement
        self.old_strong_confinement = strong_confinement
        # print(self.immune[-1], self.healthy[-1], df.infected.sum(), self.infected_undetected[-1], self.infected_detected[-1], self.dead[-1], ' Total: ',
        #       self.immune[-1] + self.healthy[-1] + df.infected.sum() + self.dead[-1])

    def build_xtics(self):
        delta = (self.time_axis[-1] - self.time_axis[0])/self.n_labels
        labels = [self.time_axis[0] + delta * i for i in range(self.n_labels)].append(self.time_axis[-1])
        plt.xticks(labels)
        self.fig.autofmt_xdate()

    def draw_measures_applied(self):
        for time in self.measures['start_weak_confinement']:
            self.ax.axvline(time, 0, self.population, label='start weak confinement', color='cyan')
        for time in self.measures['start_strong_confinement']:
            self.ax.axvline(time, 0, self.population, label='start strong confinement', color='pink')
        for time in self.measures['release_weak_confinement']:
            self.ax.axvline(time, 0, self.population, label='release weak confinement', color='azure')
        for time in self.measures['release_strong_confinement']:
            self.ax.axvline(time, 0, self.population, label='release strong confinement', color='fuchsia')


class RealTime:
    def __init__(self, queue):
        self.queue = queue
        pygame.init()
        self.screen = pygame.display.set_mode(RESOLUTION)
        self.clock = pygame.time.Clock()
        self.screen.fill(BLACK)
        self.font = pygame.font.SysFont(None, 24)

    def start(self):
        counter = 0
        while True:
            start = time.time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            start = time.time()
            self.screen.fill(BLACK)
            df, current_time = self.queue.get()
            self.draw_population(df)
            self.draw_info(current_time)
            pygame.display.update()
            self.clock.tick(FPS_DISPLAY)
            counter += 1
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
        img = self.font.render(current_time.strftime('%d/%m/%Y %H:%M:%S'), True, (0, 255, 0))
        self.screen.blit(img, (20, 20))
