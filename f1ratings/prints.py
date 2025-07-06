from datetime import datetime
from .dataclasses import *
from .helpers import *

def print_driver_rating(driver):
    print(f"Rating Progression for {driver.forename} {driver.surname}:")
    for rating in driver.ratings:
        date_str = rating[1].strftime('%Y-%m-%d') if rating[1] else 'N/A'
        print(f"Rating: {round(rating[0])}, Date: {date_str}")

def print_team_rating(team):
    print(f"Rating Progression for {team.name}:")
    for rating in team.ratings:
        date_str = rating[1].strftime('%Y-%m-%d') if rating[1] else 'N/A'
        print(f"Rating: {round(rating[0])}, Date: {date_str}")

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

def print_driver_last_change(driver):
    last_rating = driver.ratings[-1]
    prev_rating = driver.ratings[-2] if len(driver.ratings) > 1 else None
    if prev_rating:
        change = last_rating[0] - prev_rating[0]
        change_str = f"{change:+.2f}"
        date = last_rating[1].strftime('%Y-%m-%d') if last_rating[1] else 'N/A'
    else:
        change_str = "N/A"
    print(f"Last change for {driver.forename} {driver.surname}: {change_str} on {date}")

def print_team_last_change(team):
    last_rating = team.ratings[-1]
    prev_rating = team.ratings[-2] if len(team.ratings) > 1 else None
    if prev_rating:
        change = last_rating[0] - prev_rating[0]
        change_str = f"{change:+.2f}"
        date = last_rating[1].strftime('%Y-%m-%d') if last_rating[1] else 'N/A'
    else:
        change_str = "N/A"
    print(f"Last change for {team.name}: {change_str} on {date}")

