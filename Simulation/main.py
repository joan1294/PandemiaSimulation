from multiprocessing import Process, Queue
from Graph import Dashboard, RealTime
from Simulation import Simulation
from Constants import *
import time

def main():
    q_dashboard = Queue()
    q_real_time = Queue(maxsize=3)
    simulation_p = Process(target=start_simulation, args=(q_dashboard, q_real_time))
    simulation_p.start()
    if SHOW_POPULATION_MOVEMENTS:
        real_time_p = Process(target=start_real_time, args=(q_real_time,))
        real_time_p.start()
    dashboard_p = Process(target=start_dashboard, args=(q_dashboard,))
    dashboard_p.start()
    simulation_p.join()
    if SHOW_POPULATION_MOVEMENTS:
        real_time_p.join()
    dashboard_p.join()

def start_simulation(q_dashboard, q_real_time):
    simulation = Simulation(q_dashboard, q_real_time)
    simulation.start()

def start_real_time(q_real_time):
    real_time = RealTime(q_real_time)
    real_time.start()

def start_dashboard(q_dashboard):
    dashboard = Dashboard(q_dashboard)
    dashboard.start()

if __name__ == '__main__':
    main()