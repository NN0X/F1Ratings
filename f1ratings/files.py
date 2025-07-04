from .dataclasses import *

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
