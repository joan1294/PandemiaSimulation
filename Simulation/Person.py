from Constants import *
import math
import random
random.seed(RANDOM_SEED)

class Person:
    def __init__(self, id):
        self.id = id
        self.health_status = 'healthy' if random.random() >= 0.02 else 'infected'
        self.employed = None
        self.work_loc = None
        self.home_loc = None
        self.age = None
        self.food_loc = None
        self.angle = 0
        self.generate_attributes()

    def generate_attributes(self):
        """
        Generates all the attributes based on the config.
        """
        self.age = random.choices(range(0, 110, 10), AGE_PYRAMID_WEIGHTS)[0] + random.randrange(0, 10)
        self.employed = True if random.random() < ACTIVE_POPULATION_EMPLOYMENT_PROB else False
        self.pos = [random.randint(5, RESOLUTION[0]-5), random.randint(5, RESOLUTION[1]-5)]

    def persistent_move(self):
        new_pos = [-1, -1]
        while new_pos[0] < 0 or new_pos[0] > RESOLUTION[0] or new_pos[1] < 0 or new_pos[1] > RESOLUTION[1]:
            # Calculate angle of the movement vector
            self.angle += random.uniform(-0.5, 0.5) + random.choices([0,2*math.pi], [80, 20])[0]
            # Calculate movement coordinates
            x_move = int(math.cos(self.angle) * DISTANCE_PER_FRAME)
            y_move = int(math.sin(self.angle) * DISTANCE_PER_FRAME)
            new_pos[0] = self.pos[0] + x_move
            new_pos[1] = self.pos[1] + y_move
        self.pos = new_pos

    def random_move(self):
        new_pos = [-1, -1]
        while new_pos[0] < 0 or new_pos[0] > RESOLUTION[0] or new_pos[1] < 0 or new_pos[1] > RESOLUTION[1]:
            # Calculate angle of the movement vector
            self.angle = random.random()*2*math.pi
            # Calculate movement coordinates
            x_move = int(math.cos(self.angle)*DISTANCE_PER_FRAME)
            y_move = int(math.sin(self.angle)*DISTANCE_PER_FRAME)
            new_pos[0] = self.pos[0] + x_move
            new_pos[1] = self.pos[1] + y_move
        self.pos = new_pos

    def gets_infected(self):
        self.health_status = 'infected'

    def distance(self, person):
        return math.sqrt((self.pos[0] - person.pos[0])**2 + (self.pos[1] - person.pos[1])**2)