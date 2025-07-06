import f1ratings as f1
from datetime import datetime
import sys
from f1ratings.helpers import get_driver_by_name, get_team_by_name
from f1ratings.dataclasses import Driver, Team

def gen_ratings():
    f1ratings = f1.F1Ratings()
    f1ratings.fetch()
    f1ratings.compute()
    print("Ratings computed successfully!")
    f1ratings.save()
    print("Ratings saved successfully!")
    return f1ratings

def load_ratings():
    f1ratings = f1.F1Ratings()
    f1ratings.load()
    print("Ratings loaded successfully!")
    return f1ratings

def plot_ratings(f1ratings, args):
    if args[1] == "plot" and len(args) == 2:
            f1ratings.show_plot_today_grid()
    elif args[1] == "plot" and len(args) == 3:
        driver = f1ratings.get_driver_by_name(args[2])
        team = f1ratings.get_team_by_name(args[2])
        if driver is not None:
            f1ratings.show_plot_driver_rating(f"{driver.forename} {driver.surname}")
        elif team is not None:
            f1ratings.show_plot_teams_rating(team.name)
        else:
            print(f"Driver or team '{args[2]}' not found.")
    elif args[1] == "plot" and len(args) > 3:
        names = args[2:]
        drivers = [f1ratings.get_driver_by_name(name) for name in names]
        teams = [f1ratings.get_team_by_name(name) for name in names]
        if any(driver is not None for driver in drivers) and any(team is not None for team in teams):
            f1ratings.show_plot_teams_and_drivers(
                [team.name for team in teams if team is not None],
                [f"{driver.forename} {driver.surname}" for driver in drivers if driver is not None]
            )
        elif any(driver is not None for driver in drivers):
            f1ratings.show_plot_drivers_rating(
                [f"{driver.forename} {driver.surname}" for driver in drivers if driver is not None]
            )
        elif any(team is not None for team in teams):
            f1ratings.show_plot_teams_rating(
                [team.name for team in teams if team is not None]
            )
        else:
            print("Some drivers or teams not found.")

def print_ratings(f1ratings, args):
    if args[1] == "print":
        if len(args) == 2:
            f1ratings.print_today_grid()
        elif len(args) == 3:
            driver = f1ratings.get_driver_by_name(args[2])
            team = f1ratings.get_team_by_name(args[2])
            if driver is not None:
                f1ratings.print_driver_rating(f"{driver.forename} {driver.surname}")
            elif team is not None:
                f1ratings.print_team_rating(team.name)
            else:
                print(f"Driver or team '{args[2]}' not found.")
        elif len(args) > 3:
            names = args[2:]
            drivers = [f1ratings.get_driver_by_name(name) for name in names]
            teams = [f1ratings.get_team_by_name(name) for name in names]
            for driver in drivers:
                if driver is not None:
                    f1ratings.print_driver_rating(f"{driver.forename} {driver.surname}")
                else:
                    print(f"Driver not found.")
            for team in teams:
                if team is not None:
                    f1ratings.print_team_rating(team.name)
                else:
                    print(f"Team not found.")

def change_ratings(f1ratings, args):
    if args[1] == "change":
        if len(args) == 3:
            driver = f1ratings.get_driver_by_name(args[2])
            team = f1ratings.get_team_by_name(args[2])
            if driver is not None:
                f1ratings.print_driver_last_change(args[2])
            elif team is not None:
                f1ratings.print_team_last_change(team.name)
            else:
                print(f"Driver or team '{args[2]}' not found.")
        else:
            print("Usage: change [name]")
            print("  name: Name of the driver or team to check last change")

if __name__ == "__main__": 
    if len(sys.argv) > 1:
        if sys.argv[1] not in ["gen", "load", "dump", "plot", "print", "change"] or sys.argv[1] == "help" or (sys.argv[1] == "plot" and len(sys.argv) < 3) or (sys.argv[1] == "print" and len(sys.argv) < 2):
            print("Usage: python main.py [gen|load|dump|plot [driver_name|team_name]]")
            print("  gen: Generate ratings from scratch")
            print("  dump: Dump ratings to file")
            print("  plot [name]: Plot ratings for a driver or team")
            print("  plot [name1 name2 ...]: Plot ratings for multiple drivers or teams")
            print("  print [name]: Print ratings for a driver or team")
            print("  print [name1 name2 ...]: Print ratings for multiple drivers or teams")
            print("  change [name]: Last change in ratings for a driver or team")
            sys.exit(1)

        if sys.argv[1] == "gen":
            f1ratings = gen_ratings()
        else:
            f1ratings = load_ratings()

        if sys.argv[1] == "dump":
            f1ratings.dump_ratings()
            print("Ratings dumped successfully!")

        plot_ratings(f1ratings, sys.argv)
        print_ratings(f1ratings, sys.argv)
        change_ratings(f1ratings, sys.argv)
