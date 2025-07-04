from math import exp
from .config import *
from .dataclasses import *
from .compute_driver import *
from .compute_team import *
from .helpers import *

def compute_ratings(seasons, drivers, teams, qualis, sprints, statuses):
    for driver in drivers:
        driver.ratings.append((BASE_DRIVER_RATING, None))
    if not RESET_TEAM_RATINGS_SEASON or not RERATE_TEAM_RATINGS_SEASON:
        for team in teams:
            team.ratings.append((BASE_TEAM_RATING, None))

    most_races_in_season = 0
    for season in seasons:
        if len(season.races) > most_races_in_season:
            most_races_in_season = len(season.races)

    for season in seasons:
        print(f"Computing ratings for season {season.year}...")
        if RESET_TEAM_RATINGS_SEASON:
            for team in teams:
                team.ratings.append((BASE_TEAM_RATING, None)) # reset team ratings at the start of each season
        if RERATE_TEAM_RATINGS_SEASON:
            teams = rerate_teams(season, teams)

        if RESET_TEAM_REENTRY_RATINGS:
            teams = reset_team_reentry_ratings(seasons, season, teams)

        season_len = len(season.races)
        if season.year == datetime.now().year:
            season_len = CURRENT_SEASON_LENGTH
        num_races_weight = most_races_in_season / season_len
        num_races_weight_scaled = influence_function(num_races_weight, a=2.9, b=0.6, c=0.19)

        for race in season.races:
            print(f"\tComputing ratings for race {race.name}...")
            numDrivers = len(race.results)
            teams_positions_races = {}
            teams_positions_qualis = {}
            teams_positions_sprints = {}
            drivers_decays = compute_drivers_rating_decay(drivers, DRIVER_RATING_DECAY_NUM_RACES, num_races_weight)
            for driver_result in race.results:
                diff_teammates = compute_teammate_place_diff(drivers, statuses,
                                                             driver_result[0], driver_result[1], driver_result[2], driver_result[3],
                                                             race.results, numDrivers)
                penalty = False
                if driver_result[3] is not None and is_driver_fault(driver_result[3], statuses):
                    penalty = True

                race_starting_pos = next((pos for pos in race.starting_positions if pos[0] == driver_result[0]), None)

                race_quali = next((quali for quali in qualis if quali.race_id == race.id ), None)
                if race_quali is None:
                    quali_result = None
                else:
                    quali_result = next((result for result in race_quali.results if result[0] == driver_result[0]), None)

                race_sprint = next((sprint for sprint in sprints if sprint.race_id == race.id), None)
                if race_sprint is None:
                    sprint_result = None
                    sprint_starting_pos = None
                else:
                    sprint_result = next((result for result in race_sprint.results if result[0] == driver_result[0]), None)
                    sprint_starting_pos = next((pos for pos in race_sprint.starting_positions if pos[0] == driver_result[0]), None)

                race_bonus = distribution_function(driver_result[2], numDrivers, 5) if driver_result else 0
                quali_bonus = distribution_function(quali_result[2], numDrivers, 5) if quali_result else 0
                sprint_bonus = distribution_function(sprint_result[2], numDrivers, 5) if sprint_result else 0

                race_bonus*=num_races_weight
                quali_bonus*=num_races_weight

                try:
                    diff_race = race_starting_pos[1] - int(driver_result[2]) if race_starting_pos else 0
                except (ValueError, TypeError):
                    diff_race = 0
                try:
                    diff_sprint = sprint_starting_pos[1] - int(sprint_result[2]) if sprint_starting_pos else 0
                except (ValueError, TypeError):
                    diff_sprint = 0

                sign = 1
                if diff_race < 0:
                    sign = -1
                diff_race = distribution_function(abs(diff_race), numDrivers - 1, 5) * sign
                sign = 1
                if diff_sprint < 0:
                    sign = -1
                diff_sprint = distribution_function(abs(diff_sprint), numDrivers - 1, 5) * sign

                diff_race*=num_races_weight

                driver_team_rating = next((t for t in teams if t.id == driver_result[1]), None)
                driver_team_rating = driver_team_rating.ratings[-1][0] if driver_team_rating else BASE_TEAM_RATING
                diff_team_performance = driver_team_rating - BASE_TEAM_RATING

                if driver_result[1] not in teams_positions_races:
                    teams_positions_races[driver_result[1]] = []
                try:
                    race_pos = int(driver_result[2])
                except (ValueError, TypeError):
                    race_pos = numDrivers
                teams_positions_races[driver_result[1]].append((driver_result[0], race_pos))

                if driver_result[1] not in teams_positions_qualis:
                    teams_positions_qualis[driver_result[1]] = []
                if quali_result:
                    try:
                        quali_pos = int(quali_result[2])
                    except (ValueError, TypeError):
                        quali_pos = numDrivers
                    teams_positions_qualis[driver_result[1]].append((driver_result[0], quali_pos))

                if driver_result[1] not in teams_positions_sprints:
                    teams_positions_sprints[driver_result[1]] = []
                if sprint_result:
                    try:
                        sprint_pos = int(sprint_result[2])
                    except (ValueError, TypeError):
                        sprint_pos = numDrivers
                    teams_positions_sprints[driver_result[1]].append((driver_result[0], sprint_pos))

                rookie_rating_count_scaled = ROOKIE_RATING_COUNT / num_races_weight_scaled
                if rookie_rating_count_scaled < 2:
                    rookie_rating_count_scaled = 2

                driver = next((d for d in drivers if d.id == driver_result[0]), None)
                if driver:
                    driver_rating = driver.ratings[-1][0]
                    if len(driver.ratings) < rookie_rating_count_scaled and len(driver.ratings) < ROOKIE_RATING_COUNT:
                        rookie_multiplier = 1 + ROOKIE_MODIFIER * (1 / (ROOKIE_RATING_COUNT - len(driver.ratings)))
                    else:
                        rookie_multiplier = 1
                    rating_penalty = 0
                    if penalty and len(driver.ratings) >= rookie_rating_count_scaled:
                        rating_penalty = driver_rating*PENALTY_FACTOR

                    diff_team_multiplier_growth = exp(-DIFF_TEAM_GROWTH_WEIGHT * diff_team_performance / BASE_TEAM_RATING)
                    diff_team_multiplier_dumper = exp(DIFF_TEAM_DUMPER_WEIGHT * diff_team_performance / BASE_TEAM_RATING)

                    if diff_team_multiplier_growth < 0.5:
                        diff_team_multiplier_growth = 0.5
                    if diff_team_multiplier_dumper < 0.5:
                        diff_team_multiplier_dumper = 0.5

                    if diff_team_multiplier_growth > 1.5:
                        diff_team_multiplier_growth = 1.5
                    if diff_team_multiplier_dumper > 1.5:
                        diff_team_multiplier_dumper = 1.5

                    if race_bonus < 0:
                        race_bonus *= diff_team_multiplier_dumper
                    else:
                        race_bonus *= diff_team_multiplier_growth
                    if quali_bonus < 0:
                        quali_bonus *= diff_team_multiplier_dumper
                    else:
                        quali_bonus *= diff_team_multiplier_growth
                    if sprint_bonus < 0:
                        sprint_bonus *= diff_team_multiplier_dumper
                    else:
                        sprint_bonus *= diff_team_multiplier_growth

                    if diff_teammates < 0:
                        rookie_multiplier_diff_teammates = 1
                    else:
                        rookie_multiplier_diff_teammates = rookie_multiplier
                    if race_bonus < 0:
                        rookie_multiplier_race = 1
                    else:
                        rookie_multiplier_race = rookie_multiplier
                    if quali_bonus < 0:
                        rookie_multiplier_quali = 1
                    else:
                        rookie_multiplier_quali = rookie_multiplier
                    if sprint_bonus < 0:
                        rookie_multiplier_sprint = 1
                    else:
                        rookie_multiplier_sprint = rookie_multiplier
                    if diff_race < 0:
                        rookie_multiplier_diff_race = 1
                    else:
                        rookie_multiplier_diff_race = rookie_multiplier
                    if diff_sprint < 0:
                        rookie_multiplier_diff_sprint = 1
                    else:
                        rookie_multiplier_diff_sprint = rookie_multiplier

                    if driver_result[0] in drivers_decays:
                        decay = drivers_decays[driver_result[0]]
                    else:
                        decay = 0

                    rating_change = (
                                    + diff_teammates*DIFF_TEAMMATES * rookie_multiplier_diff_teammates
                                    + race_bonus*RACE_BONUS * rookie_multiplier_race
                                    + quali_bonus*QUALI_BONUS * rookie_multiplier_quali
                                    + sprint_bonus*SPRINT_BONUS * rookie_multiplier_sprint
                                    + diff_race*DIFF_RACE * rookie_multiplier_diff_race
                                    + diff_sprint*DIFF_SPRINT * rookie_multiplier_diff_sprint
                                ) * SWING_MULTIPLIER * num_races_weight_scaled - rating_penalty
                    new_driver_rating = driver_rating + rating_change - decay

                    driver.ratings.append((new_driver_rating, race.date))

            teams_weighted_pos = []
            team_decays = compute_teams_rating_decay(teams, TEAM_RATING_DECAY_NUM_RACES, num_races_weight)
            for team_id, team_positions_race in teams_positions_races.items():
                team = next((t for t in teams if t.id == team_id), None)
                if team:
                    race_avg = 0
                    for position in team_positions_race:
                        driver_rating = get_driver_by_id(drivers, position[0]).ratings[-1][0]
                        driver_rating_deviation = driver_rating - BASE_DRIVER_RATING
                        driver_rating_deviation *= DRIVER_RATING_DEVIATION_MULTIPLIER
                        scaling_factor = (BASE_DRIVER_RATING + driver_rating_deviation) / BASE_DRIVER_RATING
                        race_avg += position[1] * scaling_factor
                    if len(team_positions_race) != 0:
                        race_avg /= len(team_positions_race)
                    quali_avg = 0
                    if team_id in teams_positions_qualis:
                        for position in teams_positions_qualis[team_id]:
                            driver_rating = get_driver_by_id(drivers, position[0]).ratings[-1][0]
                            driver_rating_deviation = driver_rating - BASE_DRIVER_RATING
                            driver_rating_deviation *= DRIVER_RATING_DEVIATION_MULTIPLIER
                            scaling_factor = (BASE_DRIVER_RATING + driver_rating_deviation) / BASE_DRIVER_RATING
                            quali_avg += position[1] * scaling_factor
                        if len(teams_positions_qualis[team_id]) != 0:
                            quali_avg /= len(teams_positions_qualis[team_id])
                    sprint_avg = 0
                    if team_id in teams_positions_sprints:
                        for position in teams_positions_sprints[team_id]:
                            driver_rating = get_driver_by_id(drivers, position[0]).ratings[-1][0]
                            driver_rating_deviation = driver_rating - BASE_DRIVER_RATING
                            driver_rating_deviation *= DRIVER_RATING_DEVIATION_MULTIPLIER
                            scaling_factor = (BASE_DRIVER_RATING + driver_rating_deviation) / BASE_DRIVER_RATING
                            sprint_avg = position[1] * scaling_factor
                        if len(teams_positions_sprints[team_id]) != 0:
                            sprint_avg /= len(teams_positions_sprints[team_id])
                    team_weighted_pos = (
                                      + race_avg*TEAM_RACE_WEIGHT*num_races_weight
                                      + quali_avg*TEAM_QUALI_WEIGHT*num_races_weight
                                      + sprint_avg*TEAM_SPRINT_WEIGHT
                                  )
                    teams_weighted_pos.append((team.id, team_weighted_pos))

            teams_copy = teams.copy()
            for team_id, _ in teams_weighted_pos:
                team = next((t for t in teams if t.id == team_id), None)
                rating_change = compute_team_rating_change(teams_copy, team_id, teams_weighted_pos)
                if team:
                    team_rating = team.ratings[-1][0]
                    if team.id in team_decays:
                        decay = team_decays[team.id]
                    else:
                        decay = 0
                    new_team_rating = team_rating + rating_change * SWING_MULTIPLIER_TEAM * num_races_weight_scaled - decay
                    team.ratings.append((new_team_rating, race.date))

    return drivers, teams
