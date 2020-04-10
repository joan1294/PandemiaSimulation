import configparser
from datetime import datetime

config = configparser.ConfigParser()
config.read('../Config/Constants.cfg')

RANDOM_SEED = int(config['General']['random_seed'])
SIMULATION_DURATION_DAYS = int(config['General']['simulation_duration_days'])
FPS_SIMULATION = int(config['General']['fps_simulation'])
FPS_DISPLAY = int(config['General']['fps_display'])
N_FRAMES = FPS_SIMULATION*SIMULATION_DURATION_DAYS*24*60*60
SCALE_MPP = float(config['General']['scale'])
RESOLUTION = (int(config['General']['resolution_x']), int(config['General']['resolution_x']))
START_DATETIME = datetime.strptime(config['General']['start_datetime'], '%d/%m/%Y %H:%M:%S')

INITIAL_POPULATION = int(config['Population']['initial_population'])
ACTIVE_POPULATION_EMPLOYMENT_PROB = float(config['Population']['active_population_employment_prob'])
SPEED_MS = float(config['Population']['speed_ms'])
CRITICAL_RADIUS = int(config['Population']['critical_radius'])

AGE_PYRAMID_WEIGHTS = [float(config['Age pyramid']['prob_0_9']),
                       float(config['Age pyramid']['prob_10_19']),
                       float(config['Age pyramid']['prob_20_29']),
                       float(config['Age pyramid']['prob_30_39']),
                       float(config['Age pyramid']['prob_40_49']),
                       float(config['Age pyramid']['prob_50_59']),
                       float(config['Age pyramid']['prob_60_69']),
                       float(config['Age pyramid']['prob_70_79']),
                       float(config['Age pyramid']['prob_80_89']),
                       float(config['Age pyramid']['prob_90_99']),
                       float(config['Age pyramid']['prob_100_110'])
                       ]

DISTANCE_PER_FRAME = SPEED_MS/FPS_SIMULATION/SCALE_MPP
BLACK = (0, 0, 0)