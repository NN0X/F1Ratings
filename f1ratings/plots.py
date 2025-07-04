import matplotlib.pyplot as plt
import matplotlib as mpl

from .config import PLOT_COLORMAP

def plot_team_rating(team, startdate, enddate):
    ratings_with_dates = []
    for rating in team.ratings:
        if rating[1] is not None:
            ratings_with_dates.append((rating[0], rating[1]))
    ratings_with_dates = [(rating[0], rating[1]) for rating in ratings_with_dates if startdate <= rating[1] <= enddate]
    if not ratings_with_dates:
        return None
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
    return plt

def plot_teams_rating(teams, startdate, enddate):
    ratings_with_dates = {}
    for team in teams:
        ratings_with_dates[team.name] = []
        for rating in team.ratings:
            if rating[1] is not None:
                ratings_with_dates[team.name].append((rating[0], rating[1]))
    ratings_with_dates = {team_name: [(rating[0], rating[1]) for rating in ratings if startdate <= rating[1] <= enddate]
                           for team_name, ratings in ratings_with_dates.items()}
    if not ratings_with_dates:
        return None
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
    return plt

def plot_driver_rating(driver, startdate, enddate):
    ratings_with_dates = []
    for rating in driver.ratings:
        if rating[1] is not None:
            ratings_with_dates.append((rating[0], rating[1]))
    ratings_with_dates = [(rating[0], rating[1]) for rating in ratings_with_dates if startdate <= rating[1] <= enddate]
    if not ratings_with_dates:
        return None
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
    return plt

def plot_drivers_rating(drivers, startdate, enddate):
    ratings_with_dates = {}
    for driver in drivers:
        ratings_with_dates[driver.forename + " " + driver.surname] = []
        for rating in driver.ratings:
            if rating[1] is not None:
                ratings_with_dates[driver.forename + " " + driver.surname].append((rating[0], rating[1]))
    ratings_with_dates = {driver_name: [(rating[0], rating[1]) for rating in ratings if startdate <= rating[1] <= enddate]
                           for driver_name, ratings in ratings_with_dates.items()}
    if not ratings_with_dates:
        return None
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
    return plt

def plot_team_vs_driver_rating(team, driver, startdate, enddate):
    team_ratings = []
    for rating in team.ratings:
        if rating[1] is not None:
            team_ratings.append((rating[0], rating[1]))
    team_ratings = [(rating[0], rating[1]) for rating in team_ratings if startdate <= rating[1] <= enddate]
    driver_ratings = []
    for rating in driver.ratings:
        if rating[1] is not None:
            driver_ratings.append((rating[0], rating[1]))
    driver_ratings = [(rating[0], rating[1]) for rating in driver_ratings if startdate <= rating[1] <= enddate]
    if not team_ratings or not driver_ratings:
        return None
    team_dates = [rating[1] for rating in team_ratings]
    driver_dates = [rating[1] for rating in driver_ratings]
    common_dates = sorted(set(team_dates) & set(driver_dates))
    team_values = [next((rating[0] for rating in team_ratings if rating[1] == date), None) for date in common_dates]
    driver_values = [next((rating[0] for rating in driver_ratings if rating[1] == date), None) for date in common_dates]
    plt.figure(figsize=(10, 5))
    plt.plot(common_dates, team_values, marker='o', label=team.name, color='blue')
    plt.plot(common_dates, driver_values, marker='o', label=f"{driver.forename} {driver.surname}", color='orange')
    plt.title(f"Rating Progression: {team.name} vs {driver.forename} {driver.surname}")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend()
    plt.tight_layout(rect=(0, 0, 0.95, 1))
    return plt

def plot_teams_vs_drivers(teams, drivers, startdate, enddate):
    team_ratings = {}
    for team in teams:
        team_ratings[team.name] = []
        for rating in team.ratings:
            if rating[1] is not None:
                team_ratings[team.name].append((rating[0], rating[1]))
    driver_ratings = {}
    for driver in drivers:
        driver_ratings[driver.forename + " " + driver.surname] = []
        for rating in driver.ratings:
            if rating[1] is not None:
                driver_ratings[driver.forename + " " + driver.surname].append((rating[0], rating[1]))
    team_ratings = {team_name: [(rating[0], rating[1]) for rating in ratings if startdate <= rating[1] <= enddate]
                    for team_name, ratings in team_ratings.items()}
    driver_ratings = {driver_name: [(rating[0], rating[1]) for rating in ratings if startdate <= rating[1] <= enddate]
                      for driver_name, ratings in driver_ratings.items()}
    if not team_ratings or not driver_ratings:
        return None
    common_dates = set()
    for ratings in team_ratings.values():
        common_dates.update(rating[1] for rating in ratings)
    for ratings in driver_ratings.values():
        common_dates.update(rating[1] for rating in ratings)
    common_dates = sorted(common_dates & set([rating[1] for ratings in team_ratings.values() for rating in ratings]) &
                           set([rating[1] for ratings in driver_ratings.values() for rating in ratings]))
    plt.figure(figsize=(10, 5))
    colors = plt.get_cmap(PLOT_COLORMAP, len(team_ratings) + len(driver_ratings))
    i = 0
    for team_name, ratings in team_ratings.items():
        values = [next((rating[0] for rating in ratings if rating[1] == date), None) for date in common_dates]
        plt.plot(common_dates, values, marker='o', label=team_name, color=colors(i))
        i += 1
    for driver_name, ratings in driver_ratings.items():
        values = [next((rating[0] for rating in ratings if rating[1] == date), None) for date in common_dates]
        plt.plot(common_dates, values, marker='o', label=driver_name, color=colors(i))
        i += 1
    plt.title(f"Rating Progression: Teams vs Drivers")
    plt.xlabel("Date")
    plt.ylabel("Rating")
    plt.xticks(rotation=45)
    plt.grid()
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.tight_layout(rect=(0, 0, 0.95, 1))
    return plt
