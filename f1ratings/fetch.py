import kagglehub
from kagglehub import KaggleDatasetAdapter
from datetime import datetime

from .dataclasses import *
from .config import *

def fetch_data():
    print("Fetching data from Kaggle dataset...")
    data = {}
    for file in FILES:
        file_name = file.split('.')[0]
        data[file_name] = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            KAGGLE_PATH,
            file
        )
    return data

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
    sprints = data['sprint_results']

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
