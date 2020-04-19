import numpy as np
from Constants import *
from Person import Person
import time
import datetime
import random
import pandas as pd

class Simulation:
    def __init__(self,queue_dashboard, queue_realtime):
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
        self.policy_time = datetime.datetime.strptime('03/03/2020 00:00:00', '%d/%m/%Y %H:%M:%S')
        self.detected_cases = np.zeros(INITIAL_POPULATION, dtype=np.bool)
        self.weak_confinement = False
        self.strong_confinement = False

    def start(self):
        counter = 0
        for frame_id in range(N_FRAMES):
            self.population_moves()
            self.population_gets_infected()
            self.population_recovers_dies()
            self.simulation_time += datetime.timedelta(seconds=1 / FPS_SIMULATION)
            self.send_frame_data(frame_id)
        print('end simulation')


    def population_gets_infected(self):
        population_at_risk = self.healthy_population & ~self.immune_population
        h = np.transpose(np.expand_dims(self.position[population_at_risk], axis=0), axes=(1, 0, 2))
        i = np.expand_dims(self.position[self.infected_population], axis=0)
        a = np.max(np.linalg.norm(h - i, axis=2) < 2 * CRITICAL_RADIUS, axis=1)
        infected_ids = self.index[population_at_risk][a]
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
            self.detected_cases[infected_mask] = random.choices((True, False), (DETECTION_PROB, 1-DETECTION_PROB), k=np.count_nonzero(infected_mask))
            self.infected_population[infected_mask] = True

    def population_recovers_dies(self):
        not_infected = (self.infected_population) & (self.simulation_time >= self.recovery_death_datetime)
        recovered_mask = not_infected & ~self.dead_if_infected_population
        dead_mask = not_infected & self.dead_if_infected_population
        self.infected_population[not_infected] = False
        self.detected_cases[not_infected] = False
        self.infected_population[recovered_mask] = False
        self.healthy_population[recovered_mask] = True
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
        total_detected_cases = self.detected_cases.sum()
        if not self.weak_confinement and not self.strong_confinement and total_detected_cases >= START_WEAK_CONFINEMENT_VALUE:
            self.weak_confinement = True
        elif not self.strong_confinement and total_detected_cases >= START_STRONG_CONFINEMENT_VALUE:
            self.strong_confinement = True
        elif self.weak_confinement and total_detected_cases <= RELEASE_WEAK_CONFINEMENT_VALUE:
            self.weak_confinement = False
        elif self.strong_confinement and total_detected_cases <= RELEASE_STRONG_CONFINEMENT_VALUE:
            self.strong_confinement = False
            self.weak_confinement = True

        for person in self.population:
            person.persistent_move(self.detected_cases[person.id], self.weak_confinement, self.strong_confinement)
            self.position[person.id] = person.pos

    def send_frame_data(self, frame_id):
        frame_data = pd.DataFrame({'pos_x': self.position[:, 0],
                                   'pos_y': self.position[:, 1],
                                   'healthy': self.healthy_population,
                                   'infected': self.infected_population,
                                   'detected': self.detected_cases,
                                   'immune': self.immune_population,
                                   'dead': self.dead_population
                                   })
        # self.queue_realtime.put((frame_data, self.simulation_time))
        if frame_id % 10 == 0:
            self.queue_dashboard.put((frame_data, self.simulation_time, self.weak_confinement, self.strong_confinement))