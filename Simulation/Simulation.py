import numpy as np
from Constants import *
from Person import Person
import time
import datetime
import random
import pandas as pd

class Simulation:
    def __init__(self, queue_realtime, queue_dashboard):
        self.population = []
        self.queue_realtime = queue_realtime
        self.queue_dashboard = queue_dashboard
        healthy_population, infected_population, position = self.create_population()
        self.simulation_time = START_DATETIME
        self.healthy_population = healthy_population
        self.infected_population = infected_population
        self.immune_population = np.zeros(INITIAL_POPULATION, dtype=np.bool)
        self.dead_if_infected_population = np.array(random.choices((True, False), (DEATH_PROB, 1-DEATH_PROB),
                                                                   k=INITIAL_POPULATION), dtype=np.bool)
        self.dead_population = np.zeros(INITIAL_POPULATION)
        self.recovery_death_datetime = np.array([datetime.datetime.now() for _ in range(INITIAL_POPULATION)])
        infected_to_death = self.infected_population & ~self.dead_if_infected_population
        if np.any(infected_to_death):
            self.recovery_death_datetime[infected_to_death] = \
                [self.simulation_time + datetime.timedelta(days=random.gauss(MEAN_TIME_TO_RECOVER, SIGMA_TIME_TO_RECOVER))
                 for _ in range(np.count_nonzero(infected_to_death))]
        infected_to_recovery = self.infected_population & ~self.dead_if_infected_population
        if np.any(infected_to_recovery):
            self.recovery_death_datetime[infected_to_recovery] = \
                [self.simulation_time + datetime.timedelta(days=random.gauss(MEAN_TIME_TO_DEATH, SIGMA_TIME_TO_DEATH))
                 for _ in range(np.count_nonzero(infected_to_death))]
        self.position = position
        self.index = np.array(range(INITIAL_POPULATION))


    def start(self):
        for frame_id in range(N_FRAMES):
            self.population_moves()
            self.population_gets_infected()
            self.population_recovers_dies()
            self.simulation_time += datetime.timedelta(seconds=1 / FPS_SIMULATION)
            self.send_frame_data()
        print('end simulation')


    def population_gets_infected(self):
        h = np.transpose(np.expand_dims(self.position[self.healthy_population], axis=0), axes=(1, 0, 2))
        i = np.expand_dims(self.position[self.infected_population], axis=0)
        a = np.max(np.linalg.norm(h - i, axis=2) < 2 * CRITICAL_RADIUS, axis=1)
        infected_ids = self.index[self.healthy_population][a]
        infected_mask = np.zeros(INITIAL_POPULATION, dtype=np.bool)
        infected_mask[infected_ids] = True
        if np.any(infected_mask):
            self.healthy_population[infected_mask] = False
            infected_to_recover_mask = infected_mask & ~self.dead_if_infected_population
            infected_to_death_mask = infected_mask & self.dead_if_infected_population
            if np.any(infected_to_recover_mask):
                self.recovery_death_datetime[infected_to_recover_mask] = \
                    [self.simulation_time + datetime.timedelta(days=random.gauss(
                                                            MEAN_TIME_TO_RECOVER, SIGMA_TIME_TO_RECOVER))
                     for _ in range(np.count_nonzero(infected_to_recover_mask))]
            if np.any(infected_to_death_mask):
                self.recovery_death_datetime[infected_to_death_mask] = \
                    [self.simulation_time + datetime.timedelta(days=random.gauss(MEAN_TIME_TO_DEATH, SIGMA_TIME_TO_DEATH))
                     for _ in range(np.count_nonzero(infected_to_death_mask))]
            self.infected_population[(~self.healthy_population & ~self.infected_population)] = True

    def population_recovers_dies(self):
        recovered_mask = (self.infected_population) & (self.simulation_time >= self.recovery_death_datetime) & (
            ~self.dead_if_infected_population)
        dead_mask = (self.infected_population) & (self.simulation_time >= self.recovery_death_datetime) & (
            self.dead_if_infected_population)
        self.infected_population[recovered_mask] = False
        self.healthy_population[recovered_mask] = True
        self.infected_population[dead_mask] = False
        self.dead_population[dead_mask] = True
        self.immune_population[recovered_mask] = random.choices((True, False), (IMMUNITY_PROB, 1-IMMUNITY_PROB),
                                                                 k=np.count_nonzero(recovered_mask))

    def create_population(self):
        healthy_population = []
        infected_population = []
        position = []
        for person_id in range(INITIAL_POPULATION):
            self.population.append(Person(person_id))
            healthy_population.append(True if self.population[-1].health_status == 'healthy' else False)
            infected_population.append(True if self.population[-1].health_status == 'infected' else False)
            position.append(self.population[-1].pos)
        return np.array(healthy_population, dtype=np.bool), \
               np.array(infected_population, dtype=np.bool), \
               np.array(position, dtype=np.int32)

    def population_moves(self):
        for person in self.population:
            person.persistent_move()
            self.position[person.id] = person.pos

    def send_frame_data(self):
        frame_data = pd.DataFrame({'pos_x': self.position[:, 0],
                                   'pos_y': self.position[:, 1],
                                   'healthy': self.healthy_population,
                                   'infected': self.infected_population,
                                   'immune': self.immune_population,
                                   'dead': self.dead_population
                                   })
        self.queue_realtime.put((frame_data, self.simulation_time))
        self.queue_dashboard.put((frame_data, self.simulation_time))