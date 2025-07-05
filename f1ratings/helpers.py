from .dataclasses import *
from math import log

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

def influence_function(x, a, b):
    try:
        x = float(x)
    except ValueError:
        return 0
    c = 1 - b * log(a + 1)
    return log(a*x + 1) * b + c

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

def get_driver_by_id(drivers, driver_id):
    for driver in drivers:
        if driver.id == driver_id:
            return driver
    return None

def get_team_by_id(teams, team_id):
    for team in teams:
        if team.id == team_id:
            return team
    return None

def get_driver_by_name(drivers, name):
    for driver in drivers:
        full_name = f"{driver.forename} {driver.surname}"
        if full_name.lower() == name.lower():
            return driver
    return None

def get_team_by_name(teams, name):
    for team in teams:
        if team.name.lower() == name.lower():
            return team
    return None

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
