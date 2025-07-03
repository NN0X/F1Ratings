import kagglehub
from kagglehub import KaggleDatasetAdapter
from datetime import datetime
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib as mpl
from math import exp

mpl.rcParams['lines.linewidth'] = 0.5
mpl.rcParams['lines.markersize'] = 2

KAGGLE_PATH = "jtrotman/formula-1-race-data"
FILES = ["constructor_results.csv",
         "constructor_standings.csv",
         "constructors.csv",
         "driver_standings.csv",
         "drivers.csv",
         "qualifying.csv",
         "races.csv",
         "results.csv",
         "sprint_results.csv",
         "status.csv"]

PLOT_COLORMAP = "nipy_spectral"

BASE_DRIVER_RATING = 1200
BASE_TEAM_RATING = 1200

PENALTY_FACTOR = 0.1

DIFF_TEAMMATES = 0.5
RACE_BONUS = 0.4
QUALI_BONUS = 0.3
SPRINT_BONUS = 0.05
DIFF_RACE = 0.15
DIFF_SPRINT = 0.025

TEAM_RACE_WEIGHT = 0.6
TEAM_QUALI_WEIGHT = 0.3
TEAM_SPRINT_WEIGHT = 0.1

ROOKIE_RATING_COUNT = 7
ROOKIE_MODIFIER = 1.5

DIFF_TEAM_GROWTH_WEIGHT = 3
DIFF_TEAM_DUMPER_WEIGHT = 2

SWING_MULTIPLIER = 10
SWING_MULTIPLIER_TEAM = 300

RESET_TEAM_RATINGS_SEASON = False
RERATE_TEAM_RATINGS_SEASON = False
RESET_TEAM_REENTRY_RATINGS = True

TEAM_RATING_DECAY_NUM_RACES = 5 # 0.2 * ~25
DRIVER_RATING_DECAY_NUM_RACES = 100 # 4 * ~25

def load_data():
    print("Loading data from Kaggle dataset...")
    data = {}
    for file in FILES:
        file_name = file.split('.')[0]
        data[file_name] = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            KAGGLE_PATH,
            file
        )
    return data

@dataclass
class Driver:
    id: int
    forename: str
    surname: str
    ratings: list # (rating, date)
    first_race_date: datetime.date = None
    last_race_date: datetime.date = None
    def __str__(self):
        if self.ratings is None:
            return f"{self.forename} {self.surname} (ID: {self.id}) | Rating: N/A"
        return  f"{(self.forename + " " + self.surname):<40} | {round(self.ratings[-1][0]):>5} " \
                f"Peak: {round(max(self.ratings, key=lambda y: y[0])[0]):>5} " \
                f"{max(self.ratings, key=lambda y: y[0])[1] if max(self.ratings, key=lambda y: y[0])[1] else 'N/A'}"
    def __hash__(self):
        return hash(self.id)

@dataclass
class Team:
    id: int
    name: str
    ratings: list # (rating, date)
    first_race_date: datetime.date = None
    last_race_date: datetime.date = None
    def __str__(self):
        if self.ratings is None:
            return f"{self.name} (ID: {self.id}) | Rating: N/A"
        return  f"{self.name:<40} | {round(self.ratings[-1][0]):>5} " \
                f"Peak: {round(max(self.ratings, key=lambda y: y[0])[0]):>5} " \
                f"{max(self.ratings, key=lambda y: y[0])[1] if max(self.ratings, key=lambda y: y[0])[1] else 'N/A'}"
    def __hash__(self):
        return hash(self.id)

@dataclass
class Race:
    id: int
    name: str
    date: datetime.date
    circuit_id: int
    results: list # (driver_id, team_id, position, additional_info)
    starting_positions: list # (driver_id, starting_position)
    total_time: float = None
    def __str__(self):
        return f"{self.name} (ID: {self.id}) | Date: {self.date} | Circuit ID: {self.circuit_id}"

@dataclass
class Qualifying:
    race_id: int
    results: list # (driver_id, team_id, position)
    def __str__(self):
        sorted_results = sorted(self.results, key=lambda x: x[1])
        return f"Qualifying to race ID: {self.race_id} | Pole driver ID: {sorted_results[0][0]}"

@dataclass
class Sprint:
    race_id: int
    results: list # (driver_id, team_id, position, additional_info)
    starting_positions: list # (driver_id, starting_position)
    total_time: float = None
    def __str__(self):
        sorted_results = sorted(self.results, key=lambda x: x[2])
        return f"Sprint to race ID: {self.race_id} | Winner driver ID: {sorted_results[0][0]}"

@dataclass
class Season:
    year: int
    races: list # sorted by date
    def __str__(self):
        return f"Season: {self.year} with {len(self.races)} races"

def get_drivers(data):
    drivers = data["drivers"]
    driver_list = []
    for _, row in drivers.iterrows():
        driver = Driver(
            id=row['driverId'],
            forename=row['forename'],
            surname=row['surname'],
            ratings=[]
        )
        driver_list.append(driver)
    return driver_list

def get_teams(data):
    teams = data["constructors"]
    team_list = []
    for _, row in teams.iterrows():
        team = Team(
            id=row['constructorId'],
            name=row['name'],
            ratings=[]
        )
        team_list.append(team)
    return team_list

def get_races(data):
    races = data["races"]
    results = data["results"]

    races_dict = {}
    for _, row in races.iterrows():
        race = Race(
            id=row['raceId'],
            name=row['name'],
            date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
            circuit_id=row['circuitId'],
            results=[],
            starting_positions=[],
        )
        races_dict[race.id] = race

    for _, row in results.iterrows():
        race_id = row['raceId']
        driver_id = row['driverId']
        constructor_id = row['constructorId']
        position = row['position']
        additional_info = row['statusId']
        starting_position = row['grid']
        time = row['time']

        if time and time != '\\N' and '-' not in time and '+' not in time and ':' in time:
            time_parts = time.split(':')
            if len(time_parts) == 3:
                time_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])
            elif len(time_parts) == 2:
                time_seconds = int(time_parts[0]) * 60 + float(time_parts[1])
            else:
                time_seconds = float(time_parts[0])
            races_dict[race_id].total_time = time_seconds

        races_dict[race_id].results.append((driver_id, constructor_id, position, additional_info))
        races_dict[race_id].starting_positions.append((driver_id, starting_position))

    races_list = []
    for _, race in races_dict.items():
        if race.date > datetime.now().date():
            continue
        races_list.append(race)

    races_list.sort(key=lambda x: x.date)

    return races_list

def get_qualis(data):
    qualis = data['qualifying']

    results = []
    for _, row in qualis.iterrows():
        results.append((
            row['raceId'],
            row['driverId'],
            row['constructorId'],
            row['position']
        ))

    quali_list = []
    results.sort(key=lambda x: x[0])
    temp = []
    curr_race_id = results[0][0] if results else None
    for result in results:
        if curr_race_id != result[0]:
            quali = Qualifying(
                race_id=curr_race_id,
                results=temp
            )
            quali_list.append(quali)
            temp = []
            curr_race_id = result[0]
        temp.append((result[1], result[2], result[3]))

    if temp:
        quali = Qualifying(
            race_id=curr_race_id,
            results=temp
        )
        quali_list.append(quali)

    return quali_list

def get_sprints(data):
    sprints = data['sprint_results'] # race_id, driver_id, constructor_id, position, additional_info, starting_position, time

    results = []
    for _, row in sprints.iterrows():
        time = row['time']
        time_seconds = None
        if time and time != '\\N' and '-' not in time and '+' not in time and ':' in time:
            time_parts = time.split(':')
            if len(time_parts) == 3:
                time_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])
            elif len(time_parts) == 2:
                time_seconds = int(time_parts[0]) * 60 + float(time_parts[1])
            else:
                time_seconds = float(time_parts[0])

        results.append((
            row['raceId'],
            row['driverId'],
            row['constructorId'],
            row['position'],
            row['statusId'],
            row['grid'],
            time_seconds
        ))

    sprint_list = []
    results.sort(key=lambda x: x[0])
    temp1 = []
    temp2 = []
    time = None
    curr_race_id = results[0][0] if results else None
    for result in results:
        if curr_race_id != result[0]:
            sprint = Sprint(
                race_id=curr_race_id,
                results=temp1,
                starting_positions=temp2,
                total_time=time
            )
            sprint_list.append(sprint)
            temp1 = []
            temp2 = []
            time = None
            curr_race_id = result[0]
        temp1.append((result[1], result[2], result[3], result[4]))
        temp2.append((result[1], result[5]))
        if result[6] is not None:
            time = result[6]

    if temp1 and temp2 and time is not None:
        sprint = Sprint(
            race_id=curr_race_id,
            results=temp1,
            starting_positions=temp2,
            total_time=time
        )
        sprint_list.append(sprint)

    return sprint_list

def get_statuses(data):
    statuses = data['status']
    status_dict = {}
    for _, row in statuses.iterrows():
        status_dict[row['statusId']] = row['status']
    return status_dict

def is_driver_fault(status_id, statuses):
    bad = [#3, # Accident
           #4, # Collision
           20, # Spun off
           77, # 107% rule
           81, # Did not qualify
           97, # Did not prequalify
           #130 # Collision damage
        ]
    if status_id in bad:
        return True
    else:
        return False

def compile_seasons(races):
    seasons = []

    races_sorted = races.copy()
    races_sorted.sort(key=lambda x: x.date)

    for year in range(1950, datetime.now().year + 1):
        races_filtered = list(filter(lambda x: x.date.year == year, races_sorted))
        seasons.append(Season(
            year=year,
            races=races_filtered
        ))

    return seasons

def distribution_function(x, a, N):
    try:
        x = float(x)
        a = float(a)
    except ValueError:
        return 0
    if x <= 0:
        return N
    elif x <= a / 2:
        return N * ((1 - (x - 1) / (a / 2 - 1)) ** 3)
    elif x <= a:
        return -N * (((x - a / 2) / (a - a / 2)) ** 3)
    else:
        return 0

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

def compute_team_rating_change(teams, team_id, teams_weighted_pos):
    team_weighted_pos = next((pos for pos in teams_weighted_pos if pos[0] == team_id), None)
    if not team_weighted_pos:
        return 0
    team_pos = team_weighted_pos[1]
    best_pos = min(pos[1] for pos in teams_weighted_pos)
    worst_pos = max(pos[1] for pos in teams_weighted_pos)
    if best_pos == worst_pos:
        return 0

    teams_weighted_pos.sort(key=lambda x: x[1])
    middle_pos = teams_weighted_pos[len(teams_weighted_pos)//2][1]
    raw_change = middle_pos - team_pos + len(teams_weighted_pos)
    raw_change = raw_change / (worst_pos - best_pos)

    team = next((t for t in teams if t.id == team_id), None)
    if not team or not team.ratings:
        return 0
    team_rating = team.ratings[-1][0]

    teams_filtered = [team for team in teams if team.id in [pos[0] for pos in teams_weighted_pos]]
    total_rating = sum(t.ratings[-1][0] for t in teams_filtered if t.ratings)
    num_teams = len(teams_filtered)
    if num_teams == 0:
        return 0
    average_opponent_rating = total_rating / num_teams
    rating_change = 1 / (1 + 10 ** ((average_opponent_rating - team_rating) / 400))
    final_change = raw_change * rating_change

    return final_change

def rerate_teams(season, teams):
    # normalize team ratings so the median rating is BASE_TEAM_RATING
    team_ids_in_season = set()
    for race in season.races:
        for result in race.results:
            if result[1] not in team_ids_in_season:
                team_ids_in_season.add(result[1])
    teams_in_season = [team for team in teams if team.id in team_ids_in_season]
    if not teams_in_season:
        return teams
    ratings = [team.ratings[-1][0] for team in teams_in_season if team.ratings]
    if not ratings:
        return teams
    median_rating = sorted(ratings)[len(ratings) // 2]
    for team in teams:
        if team.id not in team_ids_in_season:
            continue
        if team.ratings:
            team_rating = team.ratings[-1][0]
            normalized_rating = (team_rating - median_rating) + BASE_TEAM_RATING
            team.ratings.append((normalized_rating, None))  # Append new intermediate rating
        else:
            team.ratings.append((BASE_TEAM_RATING, None))

    return teams

def compute_teams_rating_decay(teams, decay_full_num_races, num_races_weight):
    decays = {}
    for team in teams:
        diff = team.ratings[-1][0] - BASE_TEAM_RATING
        if diff == 0:
            continue
        decay = diff / (decay_full_num_races/num_races_weight)
        decays[team.id] = decay
    return decays

def compute_drivers_rating_decay(drivers, decay_full_num_races, num_races_weight):
    decays = {}
    for driver in drivers:
        diff = driver.ratings[-1][0] - BASE_DRIVER_RATING
        if diff == 0:
            continue
        decay = diff / (decay_full_num_races/num_races_weight)
        decays[driver.id] = decay
    return decays

def reset_team_reentry_ratings(seasons, season, teams):
    prev_year = season.year - 1
    prev_season = next((s for s in seasons if s.year == prev_year), None)
    if not prev_season:
        return teams

    current_season_team_ids = set()
    for race in season.races:
        for result in race.results:
            current_season_team_ids.add(result[1])
    previous_season_team_ids = set()
    for race in prev_season.races:
        for result in race.results:
            previous_season_team_ids.add(result[1])
    for team in teams:
        if team.id in current_season_team_ids and team.id not in previous_season_team_ids:
            team.ratings.append((BASE_TEAM_RATING, None))
    return teams

def get_driver_by_id(drivers, driver_id):
    for driver in drivers:
        if driver.id == driver_id:
            return driver
    return None

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

        num_races_weight = most_races_in_season / len(season.races)

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

                driver = next((d for d in drivers if d.id == driver_result[0]), None)
                if driver:
                    driver_rating = driver.ratings[-1][0]
                    if len(driver.ratings) < ROOKIE_RATING_COUNT:
                        rookie_multiplier = 1 + ROOKIE_MODIFIER * (1 / (ROOKIE_RATING_COUNT - len(driver.ratings)))
                    else:
                        rookie_multiplier = 1
                    rating_penalty = 0
                    if penalty and len(driver.ratings) >= ROOKIE_RATING_COUNT:
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
                                ) * SWING_MULTIPLIER - rating_penalty
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
                        scaling_factor = (BASE_DRIVER_RATING + driver_rating_deviation) / BASE_DRIVER_RATING
                        race_avg += position[1] * scaling_factor
                    if len(team_positions_race) != 0:
                        race_avg /= len(team_positions_race)
                    quali_avg = 0
                    if team_id in teams_positions_qualis:
                        for position in teams_positions_qualis[team_id]:
                            driver_rating = get_driver_by_id(drivers, position[0]).ratings[-1][0]
                            driver_rating_deviation = driver_rating - BASE_DRIVER_RATING
                            scaling_factor = (BASE_DRIVER_RATING + driver_rating_deviation) / BASE_DRIVER_RATING
                            quali_avg += position[1] * scaling_factor
                        if len(teams_positions_qualis[team_id]) != 0:
                            quali_avg /= len(teams_positions_qualis[team_id])
                    sprint_avg = 0
                    if team_id in teams_positions_sprints:
                        for position in teams_positions_sprints[team_id]:
                            driver_rating = get_driver_by_id(drivers, position[0]).ratings[-1][0]
                            driver_rating_deviation = driver_rating - BASE_DRIVER_RATING
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
                    new_team_rating = team_rating + rating_change * SWING_MULTIPLIER_TEAM - decay
                    team.ratings.append((new_team_rating, race.date))

    return drivers, teams

def show_plot_team_rating(team):
    ratings_with_dates = []
    for rating in team.ratings:
        if rating[1] is not None:
            ratings_with_dates.append((rating[0], rating[1]))

    ratings = [rating[0] for rating in ratings_with_dates]
    dates = [rating[1] for rating in ratings_with_dates if rating[1] is not None]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, ratings, marker='o')
    plt.title(f"Rating Progression for {team.name}")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout(rect=(0, 0, 0.95, 1))
    plt.show()

def get_team_by_name(teams, name):
    for team in teams:
        if team.name.lower() == name.lower():
            return team
    return None

def get_driver_by_name(drivers, name):
    for driver in drivers:
        full_name = f"{driver.forename} {driver.surname}"
        if full_name.lower() == name.lower():
            return driver
    return None

def get_team_by_id(teams, team_id):
    for team in teams:
        if team.id == team_id:
            return team
    return None

def show_plot_teams_rating(teams):
    ratings_with_dates = {}
    for team in teams:
        ratings_with_dates[team.name] = []
        for rating in team.ratings:
            if rating[1] is not None:
                ratings_with_dates[team.name].append((rating[0], rating[1]))
    ratings = {team_name: [rating[0] for rating in ratings_with_dates[team_name]] for team_name in ratings_with_dates}
    dates = {team_name: [rating[1] for rating in ratings_with_dates[team_name] if rating[1] is not None] for team_name in ratings_with_dates}
    plt.figure(figsize=(10, 5))
    colors = plt.get_cmap(PLOT_COLORMAP, len(ratings))
    for i, team_name in enumerate(ratings):
        plt.plot(dates[team_name], ratings[team_name], marker='o', label=team_name, color=colors(i))
    plt.title(f"Rating Progression for Teams")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.tight_layout(rect=(0, 0, 0.95, 1))
    plt.show()

def show_plot_driver_rating(driver):
    ratings_with_dates = []
    for rating in driver.ratings:
        if rating[1] is not None:
            ratings_with_dates.append((rating[0], rating[1]))
    ratings = [rating[0] for rating in ratings_with_dates]
    dates = [rating[1] for rating in ratings_with_dates if rating[1] is not None]
    plt.figure(figsize=(10, 5))
    plt.plot(dates, ratings, marker='o')
    plt.title(f"Rating Progression for {driver.forename} {driver.surname}")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout(rect=(0, 0, 0.95, 1))
    plt.show()

def show_plot_drivers_rating(drivers):
    ratings_with_dates = {}
    for driver in drivers:
        ratings_with_dates[driver.forename + " " + driver.surname] = []
        for rating in driver.ratings:
            if rating[1] is not None:
                ratings_with_dates[driver.forename + " " + driver.surname].append((rating[0], rating[1]))
    ratings = {driver_name: [rating[0] for rating in ratings_with_dates[driver_name]] for driver_name in ratings_with_dates}
    dates = {driver_name: [rating[1] for rating in ratings_with_dates[driver_name] if rating[1] is not None] for driver_name in ratings_with_dates}
    plt.figure(figsize=(10, 5))
    colors = plt.get_cmap(PLOT_COLORMAP, len(ratings))
    for i, driver_name in enumerate(ratings):
        plt.plot(dates[driver_name], ratings[driver_name], marker='o', label=driver_name, color=colors(i))
    plt.title(f"Rating Progression for Drivers")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.tight_layout(rect=(0, 0, 0.95, 1))
    plt.show()

def save_plot_driver_rating(driver):
    ratings_with_dates = []
    for rating in driver.ratings:
        if rating[1] is not None:
            ratings_with_dates.append((rating[0], rating[1]))
    ratings = [rating[0] for rating in ratings_with_dates]
    dates = [rating[1] for rating in ratings_with_dates if rating[1] is not None]
    plt.figure(figsize=(10, 5))
    plt.plot(dates, ratings, marker='o')
    plt.title(f"Rating Progression for {driver.forename} {driver.surname}")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout(rect=(0, 0, 0.95, 1))
    plt.savefig(f"ratings/{driver.forename}_{driver.surname}_rating_progression.png", dpi=300)
    plt.close()

def save_plot_drivers_rating(drivers, name="drivers_rating_progression"):
    ratings_with_dates = {}
    for driver in drivers:
        ratings_with_dates[driver.forename + " " + driver.surname] = []
        for rating in driver.ratings:
            if rating[1] is not None:
                ratings_with_dates[driver.forename + " " + driver.surname].append((rating[0], rating[1]))
    ratings = {driver_name: [rating[0] for rating in ratings_with_dates[driver_name]] for driver_name in ratings_with_dates}
    dates = {driver_name: [rating[1] for rating in ratings_with_dates[driver_name] if rating[1] is not None] for driver_name in ratings_with_dates}
    plt.figure(figsize=(10, 5))
    colors = plt.get_cmap(PLOT_COLORMAP, len(ratings))
    for i, driver_name in enumerate(ratings):
        plt.plot(dates[driver_name], ratings[driver_name], marker='o', label=driver_name, color=colors(i))
    plt.title(f"Rating Progression for Drivers")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.tight_layout(rect=(0, 0, 0.95, 1))
    plt.savefig(f"ratings/{name}.png", dpi=300)
    plt.close()

def save_plot_team_rating(team):
    ratings_with_dates = []
    for rating in team.ratings:
        if rating[1] is not None:
            ratings_with_dates.append((rating[0], rating[1]))

    ratings = [rating[0] for rating in ratings_with_dates]
    dates = [rating[1] for rating in ratings_with_dates if rating[1] is not None]

    plt.figure(figsize=(10, 5))
    plt.plot(dates, ratings, marker='o')
    plt.title(f"Rating Progression for {team.name}")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout(rect=(0, 0, 0.95, 1))
    plt.savefig(f"ratings/{team.name}_rating_progression.png", dpi=300)
    plt.close()

def save_plot_teams_rating(teams, name="teams_rating_progression"):
    ratings_with_dates = {}
    for team in teams:
        ratings_with_dates[team.name] = []
        for rating in team.ratings:
            if rating[1] is not None:
                ratings_with_dates[team.name].append((rating[0], rating[1]))
    ratings = {team_name: [rating[0] for rating in ratings_with_dates[team_name]] for team_name in ratings_with_dates}
    dates = {team_name: [rating[1] for rating in ratings_with_dates[team_name] if rating[1] is not None] for team_name in ratings_with_dates}
    plt.figure(figsize=(10, 5))
    colors = plt.get_cmap(PLOT_COLORMAP, len(ratings))
    for i, team_name in enumerate(ratings):
        plt.plot(dates[team_name], ratings[team_name], marker='o', label=team_name, color=colors(i))
    plt.title(f"Rating Progression for Teams")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.tight_layout(rect=(0, 0, 0.95, 1))
    plt.savefig(f"ratings/{name}.png", dpi=300)
    plt.close()

def print_driver_rating(driver):
    print(f"Rating Progression for {driver.forename} {driver.surname}:")
    for rating in driver.ratings:
        date_str = rating[1].strftime('%Y-%m-%d') if rating[1] else 'N/A'
        print(f"Rating: {round(rating[0])}, Date: {date_str}")

def save_ratings(teams, drivers):
    drivers.sort(key=lambda x: x.ratings[-1][0])
    pos = len(drivers)
    with open("ratings/driver_ratings_current.txt", "w") as f:
        for driver in drivers:
            line = f"{pos:>4}. {driver.forename:<20} {driver.surname:<20} | {round(driver.ratings[-1][0]):>5}\n"
            f.write(line)
            pos -= 1

    drivers.sort(key=lambda x: max(x.ratings, key=lambda y: y[0]))
    pos = len(drivers)
    with open("ratings/driver_ratings_peak.txt", "w") as f:
        for driver in drivers:
            peak_rating = max(driver.ratings, key=lambda x: x[0])
            line = f"{pos:>4}. {driver.forename:<20} {driver.surname:<20} | {round(peak_rating[0]):>5} {peak_rating[1]}\n"
            f.write(line)
            pos -= 1

    pos = len(teams)
    teams.sort(key=lambda x: x.ratings[-1][0])
    with open("ratings/team_ratings_current.txt", "w") as f:
        for team in teams:
            line = f"{pos:>4}. {team.name:<20} | {team.ratings[-1][0]:>5}\n"
            f.write(line)
            pos -= 1

    pos = len(teams)
    teams.sort(key=lambda x: max(x.ratings, key=lambda y: y[0]))
    with open("ratings/team_ratings_peak.txt", "w") as f:
        for team in teams:
            peak_rating = max(team.ratings, key=lambda x: x[0])
            line = f"{pos:>4}. {team.name:<20} | {round(peak_rating[0]):>5} {peak_rating[1]}\n"
            f.write(line)
            pos -= 1

def get_last_race_drivers(drivers, races):
    races.sort(key=lambda x: x.date, reverse=True)
    last_race = races[0]
    last_race_drivers = set()
    for result in last_race.results:
        driver = get_driver_by_id(drivers, result[0])
        if driver not in last_race_drivers:
            last_race_drivers.add(driver)
    return list(last_race_drivers)

def get_last_race_teams(teams, races):
    races.sort(key=lambda x: x.date, reverse=True)
    last_race = races[0]
    last_race_teams = set()
    for result in last_race.results:
        team = get_team_by_id(teams, result[1])
        if team not in last_race_teams:
            last_race_teams.add(team)
    return list(last_race_teams)

def print_today_grid(teams, drivers, races):
    print("Today's grid:")
    last_race_drivers = get_last_race_drivers(drivers, races)
    num_current_drivers = len(last_race_drivers)
    drivers.sort(key=lambda x: x.ratings[-1][0])
    for driver in drivers:
        if driver in last_race_drivers:
            print(f"{num_current_drivers:>2}. {driver}")
            num_current_drivers -= 1

    print("Today's teams:")
    last_race_teams = get_last_race_teams(teams, races)
    num_current_teams = len(last_race_teams)
    teams.sort(key=lambda x: x.ratings[-1][0])
    for team in teams:
        if team in last_race_teams:
            print(f"{num_current_teams:>2}. {team}")
            num_current_teams -= 1

if __name__ == "__main__":
    data = load_data()
    drivers = get_drivers(data)
    teams = get_teams(data)
    races = get_races(data)
    qualis = get_qualis(data)
    sprints = get_sprints(data)
    seasons = compile_seasons(races)
    statuses = get_statuses(data)

    drivers, teams = compute_ratings(seasons, drivers, teams, qualis, sprints, statuses)

    print("Ratings computed successfully!")

    save_ratings(teams, drivers)
    print("Ratings saved to files.")

    print_today_grid(teams, drivers, races)

    save_plot_drivers_rating(get_last_race_drivers(drivers, races), name="current_drivers_rating_progression")
    save_plot_teams_rating(get_last_race_teams(teams, races), name="current_teams_rating_progression")

    show_plot_driver_rating(get_driver_by_name(drivers, "Mick Schumacher"))
