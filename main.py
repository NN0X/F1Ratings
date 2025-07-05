import f1ratings as f1
from datetime import datetime
import sys

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

if __name__ == "__main__": 
    if len(sys.argv) > 1 and sys.argv[1] == "gen":
        f1ratings = gen_ratings()
    else:
        f1ratings = load_ratings()

    f1ratings.dump_ratings()
    print("Ratings saved to files.")

    f1ratings.print_today_grid()

    #f1ratings.show_plot_today_grid()
    #f1ratings.save_plot_today_grid()

    #f1ratings.show_plot_driver_rating("Max Verstappen", datetime(2014, 1, 1).date())

    #f1ratings.show_plot_teams_rating(["Mercedes", "Red Bull"], datetime(2024, 1, 1).date())

    #f1ratings.show_plot_driver_rating("Max Verstappen", datetime(2020, 1, 1).date())

    #f1ratings.show_plot_teams_and_drivers(
    #    ["Red Bull", "Mercedes", "Ferrari"],
    #    ["Max Verstappen", "Lewis Hamilton", "Charles Leclerc"],
    #    datetime(2010, 1, 1).date()
    #)
