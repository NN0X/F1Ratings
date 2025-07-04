import f1ratings as f1
from datetime import datetime

if __name__ == "__main__":
    f1ratings = f1.F1Ratings()
    f1ratings.fetch()
    f1ratings.compute()
    print("Ratings computed successfully!")
    f1ratings.save_ratings()
    print("Ratings saved to files.")

    f1ratings.print_today_grid()

    f1ratings.show_plot_today_grid()
    f1ratings.save_plot_today_grid()

    f1ratings.show_plot_driver_rating("Max Verstappen", datetime(2024, 1, 1).date())

    f1ratings.show_plot_team_vs_driver("Red Bull", "Max Verstappen", datetime(2024, 1, 1).date())

    f1ratings.show_plot_teams_vs_drivers(
        ["Red Bull", "Mercedes", "Ferrari"],
        ["Max Verstappen", "Lewis Hamilton", "Charles Leclerc"],
        datetime(2024, 1, 1).date()
    )
