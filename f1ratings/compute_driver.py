from .dataclasses import *
from .config import *
from .helpers import *

def compute_teammate_place_diff(drivers, statuses, driver_id, team_id, position, status, results, lastPossiblePosition):
    try:
        position = int(position)
    except ValueError:
        if not is_driver_fault(status, statuses):
            return 0
        else:
            position = lastPossiblePosition

    teammate_ids = [res[0] for res in results if res[1] == team_id and res[0] != driver_id]
    if not teammate_ids:
        return 0
    teammate_positions = [res[2] for res in results if res[0] in teammate_ids]

    diffs = []
    for teammate_position in teammate_positions:
        try:
            teammate_position = int(teammate_position)
        except ValueError:
            teammate_position = lastPossiblePosition
        diffs.append(teammate_position - position)

    expectedScores = [] # elo rating expected scores Ea = 1 / (1 + 10 ** ((teammate_rating - driver_rating) / 400))
    for teammate_id in teammate_ids:
        teammate = next((d for d in drivers if d.id == teammate_id), None)
        if teammate and teammate.ratings:
            teammate_rating = teammate.ratings[-1][0]
            driver_rating = next((d for d in drivers if d.id == driver_id), None).ratings[-1][0]
            expected_score = 1 / (1 + 10 ** ((teammate_rating - driver_rating) / 400))
            expectedScores.append(expected_score)
    if not expectedScores:
        return 0

    diffs_distributed = []
    for diff in diffs:
        if diff < 0:
            sign = -1
        else:
            sign = 1
        distributed_diff = distribution_function(abs(diff), lastPossiblePosition - 1, 5) * sign
        diffs_distributed.append(distributed_diff)

    diffs_adjusted = [diff * 2 * expected_score for diff, expected_score in zip(diffs_distributed, expectedScores)]

    return sum(diffs_adjusted) / len(diffs_adjusted) if diffs_adjusted else 0

def compute_drivers_rating_decay(drivers, decay_full_num_races, num_races_weight):
    decays = {}
    for driver in drivers:
        diff = driver.ratings[-1][0] - BASE_DRIVER_RATING
        if diff == 0:
            continue
        decay = diff / (decay_full_num_races/num_races_weight)
        decays[driver.id] = decay
    return decays
