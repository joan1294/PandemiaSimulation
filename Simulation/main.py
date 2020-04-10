import pandas as pd
import numpy as np
from Constants import *
from Person import Person
import pygame
import time
import sys
import datetime
population = []


def main():
    healthy_population, infected_population, position = create_population()
    # for frame_id in range(n_frames):
    #     save_frame()
    #     move_
    simulation = Simulation(healthy_population, infected_population, position)
    simulation.start_simulation()
    print('END')

class Simulation:
    def __init__(self, healthy_population, infected_population, position):
        self.population = population
        self.screen = pygame.display.set_mode(RESOLUTION)
        self.screen.fill(BLACK)
        pygame.init()
        self.clock = pygame.time.Clock()
        self.simulation_time = START_DATETIME
        self.healthy_population = healthy_population
        self.infected_population = infected_population
        self.position = position
        self.index = np.array(range(INITIAL_POPULATION))

    def start_simulation(self):
        counter = 0
        for frame_id in range(N_FRAMES):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            self.population_moves()
            self.population_gets_infected()
            self.screen.fill(BLACK)
            self.draw_population()
            pygame.display.flip()
            self.simulation_time += datetime.timedelta(seconds=1/FPS_SIMULATION)
            self.clock.tick(FPS_DISPLAY)
            counter += 1
            if counter == 30:
                print(self.clock.get_fps())
                counter = 0
        print('end simulation')


    def draw_population(self):
        for person in population:
            if person.health_status == 'infected':
                # pygame.draw.circle(self.screen, (255, 150, 150), person.pos, CRITICAL_RADIUS, 1)
                pygame.draw.circle(self.screen, (255, 0, 0), person.pos, 3)
            elif person.health_status == 'healthy':
                # pygame.draw.circle(self.screen, (100, 100, 200), person.pos, CRITICAL_RADIUS, 1)
                pygame.draw.circle(self.screen, (255, 255, 255), person.pos, 3)

    def population_gets_infected(self):
        for healthy_person in self.index[self.healthy_population]:
            if np.max(np.linalg.norm(self.position[healthy_person] - self.position[self.infected_population], axis=1) < 2 * CRITICAL_RADIUS):
                population[healthy_person].gets_infected()
                self.healthy_population[healthy_person] = 0
                self.infected_population[healthy_person] = 1

    def population_moves(self):
        for person in population:
            person.persistent_move()
            self.position[person.id] = person.pos

def create_population():
    healthy_population = []
    infected_population = []
    position = []
    for person_id in range(INITIAL_POPULATION):
        population.append(Person(person_id))
        healthy_population.append(True if population[-1].health_status == 'healthy' else False)
        infected_population.append(True if population[-1].health_status == 'infected' else False)
        position.append(population[-1].pos)
    return np.array(healthy_population, dtype=np.bool),\
           np.array(infected_population, dtype=np.bool),\
           np.array(position, dtype=np.int32)

def population_moves():
    for person in population:
        person.persistent_move()

# def population_gets_infected():
#     for healthy_person in self.index[self.healthy_population]:
#         for infected_person in population:
#             if infected_person.health_status == 'infected':
#                 if healthy_person.distance(infected_person) < 2*CRITICAL_RADIUS:
#                     healthy_person.gets_infected()
#                     break


if __name__ == '__main__':
    main()