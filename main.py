import kagglehub
from kagglehub import KaggleDatasetAdapter
from datetime import datetime
from dataclasses import dataclass

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
PENALTY_FACTOR = 0.05
DIFF_TEAMMATES = 0.3

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

    diffs_adjusted = [diff * expected_score for diff, expected_score in zip(diffs, expectedScores)]

    return sum(diffs_adjusted) / len(diffs_adjusted) if diffs_adjusted else 0

def compute_ratings(seasons, drivers, teams, qualis, sprints, statuses):
    for driver in drivers:
        driver.ratings.append(BASE_DRIVER_RATING)
    for team in teams:
        team.ratings.append(BASE_TEAM_RATING)

    for season in seasons:
        print(f"Computing ratings for season {season.year}...")
        for race in season.races:
            print(f"\tComputing ratings for race {race.name}...")
            numDrivers = len(race.results)
            for driver_result in race.results:
                diff_teammates = compute_teammate_place_diff(drivers, statuses,
                                                             driver_result[0], driver_result[1], driver_result[2], driver_result[3],
                                                             race.results, numDrivers)
                penalty = False
                if driver_result[3] is not None and is_driver_fault(driver_result[3], statuses):
                    penalty = True

                driver = next((d for d in drivers if d.id == driver_result[0]), None)
                if driver:
                    driver_rating = driver.ratings[-1]
                    rating_penalty = 0
                    if penalty:
                        rating_penalty = driver_rating * PENALTY_FACTOR
                    new_driver_rating = driver_rating + diff_teammates*DIFF_TEAMMATES - rating_penalty
                    driver.ratings.append(new_driver_rating)

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
    print("Drivers current:")
    drivers.sort(key=lambda x: x.ratings[-1])
    pos = len(drivers)
    for driver in drivers:
        print(f"{pos:>4}. {driver.forename:<12} {driver.surname:<12} | {driver.ratings[-1]:>5}")
        pos -= 1

    pos = len(drivers)
    with open("driver_ratings_current.txt", "w") as f:
        for driver in drivers:
            line = f"{pos:>4}. {driver.forename:<12} {driver.surname:<12} | {driver.ratings[-1]:>5}\n"
            f.write(line)
            pos -= 1

    print("Drivers' peak ratings:")
    drivers.sort(key=lambda x: max(x.ratings))
    pos = len(drivers)
    for driver in drivers:
        peak_rating = max(driver.ratings)
        print(f"{pos:>4}. {driver.forename:<12} {driver.surname:<12} | {peak_rating:>5}")
        pos -= 1

    pos = len(drivers)
    with open("driver_ratings_peak.txt", "w") as f:
        for driver in drivers:
            peak_rating = max(driver.ratings)
            line = f"{pos:>4}. {driver.forename:<12} {driver.surname:<12} | {peak_rating:>5}\n"
            f.write(line)
            pos -= 1
