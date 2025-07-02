import kagglehub
from kagglehub import KaggleDatasetAdapter
from datetime import datetime
from dataclasses import dataclass
import matplotlib.pyplot as plt

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

BASE_DRIVER_RATING = 1000
BASE_TEAM_RATING = 1000

PENALTY_FACTOR = 0.01

DIFF_TEAMMATES = 0.65
RACE_BONUS = 0.1
QUALI_BONUS = 0.05
SPRINT_BONUS = 0.025
DIFF_RACE = 0.15
DIFF_SPRINT = 0.025

RACE_WEIGHT = 0.65
QUALI_WEIGHT = 0.25
SPRINT_WEIGHT = 0.1

ROOKIE_RATING_COUNT = 5
ROOKIE_MODIFIER = 1.2

SWING_MULTIPLIER = 2
SWING_MULTIPLIER_TEAM = 100

RESET_TEAM_RATINGS_SEASON = True

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
    ratings: list
    first_race_date: datetime.date = None
    last_race_date: datetime.date = None
    def __str__(self):
        if self.ratings is None:
            return f"{self.forename} {self.surname} (ID: {self.id}) | Rating: N/A"
        return f"{self.forename} {self.surname} (ID: {self.id}) | Rating: {self.ratings[-1]}"

@dataclass
class Team:
    id: int
    name: str
    ratings: list
    first_race_date: datetime.date = None
    last_race_date: datetime.date = None
    def __str__(self):
        if self.ratings is None:
            return f"{self.name} (ID: {self.id}) | Rating: N/A"
        return f"{self.name} (ID: {self.id}) | Rating: {self.ratings[-1]}"

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

def distribution_function(x, a, N=1):
    try:
        x = float(x)
        a = float(a)
    except ValueError:
        return 0
    if x <= 0:
        return 0
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
            teammate_rating = teammate.ratings[-1]
            driver_rating = next((d for d in drivers if d.id == driver_id), None).ratings[-1]
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

    middle_pos = (best_pos + worst_pos) / 2
    raw_change = team_pos - middle_pos
    raw_change = raw_change / (worst_pos - best_pos)

    team = next((t for t in teams if t.id == team_id), None)
    if not team or not team.ratings:
        return 0
    team_rating = team.ratings[-1]

    teams_filtered = [team for team in teams if team.id in [pos[0] for pos in teams_weighted_pos]]
    total_rating = sum(t.ratings[-1] for t in teams_filtered if t.ratings)
    num_teams = len(teams_filtered)
    if num_teams == 0:
        return 0
    average_opponent_rating = total_rating / num_teams
    rating_change = 1 / (1 + 10 ** ((average_opponent_rating - team_rating) / 400))
    final_change = raw_change * rating_change

    return final_change

def compute_ratings(seasons, drivers, teams, qualis, sprints, statuses):
    for driver in drivers:
        driver.ratings.append(BASE_DRIVER_RATING)
    if not RESET_TEAM_RATINGS_SEASON:
        for team in teams:
            team.ratings.append(BASE_TEAM_RATING)

    for season in seasons:
        print(f"Computing ratings for season {season.year}...")
        if RESET_TEAM_RATINGS_SEASON:
            for team in teams:
                team.ratings.append(BASE_TEAM_RATING) # reset team ratings at the start of each season
        for race in season.races:
            print(f"\tComputing ratings for race {race.name}...")
            numDrivers = len(race.results)
            teams_positions_races = {}
            teams_positions_qualis = {}
            teams_positions_sprints = {}
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

                driver_team_rating = next((t for t in teams if t.id == driver_result[1]), None)
                driver_team_rating = driver_team_rating.ratings[-1] if driver_team_rating else BASE_TEAM_RATING
                diff_team_performance = driver_team_rating - BASE_TEAM_RATING

                sign = 1
                if driver_team_rating < BASE_TEAM_RATING:
                    sign = -1
                diff_team_performance = distribution_function(abs(diff_team_performance), 1000, 1) * sign

                if driver_result[1] not in teams_positions_races:
                    teams_positions_races[driver_result[1]] = []
                try:
                    race_pos = int(driver_result[2])
                except (ValueError, TypeError):
                    race_pos = numDrivers
                teams_positions_races[driver_result[1]].append(race_pos)

                if driver_result[1] not in teams_positions_qualis:
                    teams_positions_qualis[driver_result[1]] = []
                if quali_result:
                    try:
                        quali_pos = int(quali_result[2])
                    except (ValueError, TypeError):
                        quali_pos = numDrivers
                    teams_positions_qualis[driver_result[1]].append(quali_pos)

                if driver_result[1] not in teams_positions_sprints:
                    teams_positions_sprints[driver_result[1]] = []
                if sprint_result:
                    try:
                        sprint_pos = int(sprint_result[2])
                    except (ValueError, TypeError):
                        sprint_pos = numDrivers
                    teams_positions_sprints[driver_result[1]].append(sprint_pos)

                driver = next((d for d in drivers if d.id == driver_result[0]), None)
                if driver:
                    driver_rating = driver.ratings[-1]
                    if len(driver.ratings) < ROOKIE_RATING_COUNT:
                        rookie_multiplier = 1 + ROOKIE_MODIFIER * (1 / (ROOKIE_RATING_COUNT - len(driver.ratings)))
                    else:
                        rookie_multiplier = 1
                    rating_penalty = 0
                    if penalty:
                        rating_penalty = driver_rating*PENALTY_FACTOR
                    rating_change = (
                                    + diff_teammates*DIFF_TEAMMATES * rookie_multiplier
                                    + race_bonus*RACE_BONUS * rookie_multiplier
                                    + quali_bonus*QUALI_BONUS * rookie_multiplier
                                    + sprint_bonus*SPRINT_BONUS * rookie_multiplier
                                    + diff_race*DIFF_RACE * rookie_multiplier
                                    + diff_sprint*DIFF_SPRINT * rookie_multiplier
                                    - rating_penalty
                                ) * SWING_MULTIPLIER
                    if diff_team_performance < 0:
                        rating_change *= 1 + diff_team_performance
                    elif diff_team_performance > 0:
                        rating_change *= 1 + diff_team_performance
                    new_driver_rating = driver_rating + rating_change

                    driver.ratings.append(new_driver_rating)

            teams_weighted_pos = [] # (team_id, weighted_position)
            for team_id, team_positions_race in teams_positions_races.items():
                team = next((t for t in teams if t.id == team_id), None)
                if team:
                    race_avg = 0
                    for position in team_positions_race:
                        race_avg += position
                    if len(team_positions_race) != 0:
                        race_avg = len(team_positions_race)
                    quali_avg = 0
                    if team_id in teams_positions_qualis:
                        for position in teams_positions_qualis[team_id]:
                            quali_avg += position
                        if len(teams_positions_qualis[team_id]) != 0:
                            quali_avg = len(teams_positions_qualis[team_id])
                    sprint_avg = 0
                    if team_id in teams_positions_sprints:
                        for position in teams_positions_sprints[team_id]:
                            sprint_avg += position
                        if len(teams_positions_sprints[team_id]) != 0:
                            sprint_avg = len(teams_positions_sprints[team_id])
                    team_weighted_pos = (
                                      + race_avg*RACE_WEIGHT
                                      + quali_avg*QUALI_WEIGHT
                                      + sprint_avg*SPRINT_WEIGHT
                                  )
                    teams_weighted_pos.append((team.id, team_weighted_pos))

            teams_copy = teams.copy()
            for team_id, _ in teams_weighted_pos:
                team = next((t for t in teams if t.id == team_id), None)
                rating_change = compute_team_rating_change(teams_copy, team_id, teams_weighted_pos)
                if team:
                    team_rating = team.ratings[-1]
                    new_team_rating = team_rating + rating_change * SWING_MULTIPLIER_TEAM
                    team.ratings.append(new_team_rating)

    return drivers, teams

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

    drivers.sort(key=lambda x: x.ratings[-1])
    pos = len(drivers)
    with open("ratings/driver_ratings_current.txt", "w") as f:
        for driver in drivers:
            line = f"{pos:>4}. {driver.forename:<12} {driver.surname:<12} | {driver.ratings[-1]:>5}\n"
            f.write(line)
            pos -= 1

    drivers.sort(key=lambda x: max(x.ratings))
    pos = len(drivers)
    with open("ratings/driver_ratings_peak.txt", "w") as f:
        for driver in drivers:
            peak_rating = max(driver.ratings)
            line = f"{pos:>4}. {driver.forename:<12} {driver.surname:<12} | {peak_rating:>5}\n"
            f.write(line)
            pos -= 1

    pos = len(teams)
    teams.sort(key=lambda x: x.ratings[-1])
    with open("ratings/team_ratings_current.txt", "w") as f:
        for team in teams:
            line = f"{pos:>4}. {team.name:<12} | {team.ratings[-1]:>5}\n"
            f.write(line)
            pos -= 1

    pos = len(teams)
    teams.sort(key=lambda x: max(x.ratings))
    with open("ratings/team_ratings_peak.txt", "w") as f:
        for team in teams:
            peak_rating = max(team.ratings)
            line = f"{pos:>4}. {team.name:<12} | {peak_rating:>5}\n"
            f.write(line)
            pos -= 1

    print("Today's grid:")
    races.sort(key=lambda x: x.date, reverse=True)
    last_race = races[0]
    last_race_drivers = set()
    for result in last_race.results:
        if result[0] not in last_race_drivers:
            last_race_drivers.add(result[0])

    num_current_drivers = len(last_race_drivers)
    drivers.sort(key=lambda x: x.ratings[-1])
    for driver in drivers:
        if driver.id in last_race_drivers:
            print(f"{num_current_drivers:>2}. {driver.forename:<12} {driver.surname:<12} | {driver.ratings[-1]:>5}")
            num_current_drivers -= 1

    print("Today's teams:")
    last_race_teams = set()
    for result in last_race.results:
        if result[1] not in last_race_teams:
            last_race_teams.add(result[1])

    num_current_teams = len(last_race_teams)
    teams.sort(key=lambda x: x.ratings[-1])
    for team in teams:
        if team.id in last_race_teams:
            print(f"{num_current_teams:>2}. {team.name:<12} | {team.ratings[-1]:>5}")
            num_current_teams -= 1
