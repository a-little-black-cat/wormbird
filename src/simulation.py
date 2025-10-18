import os
from datetime import datetime
import math
import random
from typing import List, Dict, Union
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import pandas as pd



class Entity:
    def __init__(self, x: float, y: float, speed: float, name: str = "Entity"):
        self.x = x
        self.y = y
        self.speed = speed
        self.name = name

    def distance_to(self, target_x: float, target_y: float) -> float:

        return math.sqrt((target_x - self.x) ** 2 + (target_y - self.y) ** 2)

    def move_towards(self, target_x: float, target_y: float, delta_time: float):

        dx = target_x - self.x
        dy = target_y - self.y

        distance = math.sqrt(dx ** 2 + dy ** 2)

        # Entity is already at target
        if distance == 0:
            return

        # Calculate unit vector components (normalized direction)
        ux = dx / distance
        uy = dy / distance

        # Calculate distance to move in this time step
        max_movement = self.speed * delta_time

        if distance < max_movement:
            # Prevent overshooting: move exactly to the target
            self.x = target_x
            self.y = target_y
        else:
            # Move along the unit vector scaled by the maximum movement
            self.x += ux * max_movement
            # FIX: Ensure uy is used for the y-component update
            self.y += uy * max_movement


class Bird(Entity):
    #hunts worm

    def __init__(self, x: float, y: float, speed: float, catch_radius: float):
        #pass name to the super constructor
        super().__init__(x, y, speed, name="Bird")
        self.catch_radius = catch_radius

    def hunt(self, worm: 'Worm', delta_time: float):
        #chase worm
        self.move_towards(worm.x, worm.y, delta_time)


class Worm(Entity):
    #tries to escape bird

    def __init__(self, x: float, y: float, speed: float):
        #pass name to the super constructor
        super().__init__(x, y, speed, name="Worm")

    def seek_safety(self, safe_zone_pos: tuple, delta_time: float):
        #target safe zone
        self.move_towards(safe_zone_pos[0], safe_zone_pos[1], delta_time)



def run_simulation(attempt_id: int) -> Dict[str, Union[int, str, float]]:
    #single simulation

    worm_start_x = random.uniform(0, 10)
    worm_start_y = random.uniform(0, 10)

    worm = Worm(x=worm_start_x, y=worm_start_y, speed=WORM_SPEED)

    # Initialize bird close to the worm
    bird = Bird(x=worm.x + random.uniform(-5, 5), y=worm.y + random.uniform(-5, 5),
                speed=BIRD_SPEED, catch_radius=CATCH_RADIUS)

    time_elapsed = 0.0
    # Safety limit calculation ensures we don't run forever
    max_steps = int(FIELD_SIZE / WORM_SPEED / STEP_TIME * 2)

    for step in range(max_steps):

        bird.hunt(worm, STEP_TIME)

        worm.seek_safety(SAFE_ZONE_POS, STEP_TIME)

        # 4. Check for outcomes
        bird_worm_dist = bird.distance_to(worm.x, worm.y)
        worm_safe_dist = worm.distance_to(SAFE_ZONE_POS[0], SAFE_ZONE_POS[1])

        time_elapsed += STEP_TIME

        # Outcome 1: Bird Catches Worm
        if bird_worm_dist <= CATCH_RADIUS:
            return {
                "attempt_id": attempt_id,
                "outcome": "Caught",
                "time_s": round(time_elapsed, 2),
                "worm_x": round(worm.x, 2),
                "worm_y": round(worm.y, 2)
            }

        # Outcome 2: Worm Reaches Safety
        if worm_safe_dist <= CATCH_RADIUS / 2:
            return {
                "attempt_id": attempt_id,
                "outcome": "Safe",
                "time_s": round(time_elapsed, 2),
                "worm_x": round(worm.x, 2),
                "worm_y": round(worm.y, 2)
            }

    # Outcome 3: Timeout (if simulation runs too long)
    return {
        "attempt_id": attempt_id,
        "outcome": "Timeout",
        "time_s": round(time_elapsed, 2),
        "worm_x": round(worm.x, 2),
        "worm_y": round(worm.y, 2)
    }


def run_trials(num_trials: int = 100):
    # run and print simulation stats
    results: List[Dict] = []
    print(f"--- Starting {num_trials} Trials of Bird vs. Worm ---")

    for i in range(1, num_trials + 1):
        result = run_simulation(i)
        results.append(result)
        #Extracting data into a .csv file for each trial



    safe_count = sum(1 for r in results if r['outcome'] == 'Safe')
    caught_count = sum(1 for r in results if r['outcome'] == 'Caught')

    print("\n--- Summary Statistics ---")
    print(f"Total Trials: {num_trials}")
    print(f"Worm Escapes (Safe): {safe_count} ({safe_count / num_trials:.1%})")
    print(f"Bird Wins (Caught): {caught_count} ({caught_count / num_trials:.1%})")
    print(f"Timeouts: {num_trials - safe_count - caught_count}")

    # Calculate average time for successful escapes
    safe_times = [r['time_s'] for r in results if r['outcome'] == 'Safe']
    if safe_times:
        print(f"Average Escape Time: {sum(safe_times) / len(safe_times):.2f} seconds")

    print("\n--- First 5 Detailed Results ---")
    for i, r in enumerate(results[:5]):
        print(
            f"Attempt {r['attempt_id']}: {r['outcome']} in {r['time_s']}s (Final Pos: ({r['worm_x']}, {r['worm_y']}))")
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    #i = str('num_trials'+ '{current_time}')
    df = pd.DataFrame(results)
    df.to_csv(f"simulation_results-{num_trials}-{current_time}.csv", index=False)


def adjust_parameters():
    # config
    global FIELD_SIZE  # The field is 100x100 units
    global SAFE_ZONE_POS  # Target coordinates for the worm
    # input asks for x and y seperately , then formats it

    global BIRD_SPEED
    global CATCH_RADIUS  # Distance at which the bird catches the worm
    global WORM_SPEED
    global STEP_TIME  # Time passed in one simulation step (for finer control)

    field_size = input("Enter field size: ")
    FIELD_SIZE = float(field_size)
    safe_zone_pos_x_str = input("Enter safe zone position x value: ")
    safe_zone_pos_x = float(safe_zone_pos_x_str)
    safe_zone_pos_y_str = input("Enter safe zone position y value: ")
    safe_zone_pos_y = float(safe_zone_pos_y_str)

    SAFE_ZONE_POS = (safe_zone_pos_x, safe_zone_pos_y)

    bird_speed_str = input("Enter bird speed: ")
    BIRD_SPEED = float(bird_speed_str)

    catch_radius = input("Enter catch radius: ")
    CATCH_RADIUS = float(catch_radius)

    worm_speed_str = input("Enter worm speed: ")
    WORM_SPEED = float(worm_speed_str)

    step_time_str = input("Enter step_time: ")
    STEP_TIME = float(step_time_str)

    trial_count_str = input("Enter number of trials to run: ")
    trial_count = int(trial_count_str)

    run_trials(trial_count)




if __name__ == "__main__":
    adjust_parameters()
