from .dataclasses import *
from .fetch import *
from .prints import *
from .compute import *
from .plots import *
from .files import *
from .config import *

import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from datetime import datetime

class F1Ratings:
    def __init__(self, linewidth=PLOT_LINEWIDTH, markersize=PLOT_MARKERSIZE, colormap=PLOT_COLORMAP):
        self.drivers = []
        self.teams = []
        self.races = []
        self.qualis = []
        self.sprints = []
        self.seasons = []
        self.statuses = []
        mpl.rcParams['lines.linewidth'] = linewidth
        mpl.rcParams['lines.markersize'] = markersize
        try:
            os.makedirs("ratings", exist_ok=True)
        except OSError as e:
            print(f"Error creating directory: {e}")
            exit(1)

    def fetch(self):
        data = fetch_data()
        self.drivers = get_drivers(data)
        self.teams = get_teams(data)
        self.races = get_races(data)
        self.qualis = get_qualis(data)
        self.sprints = get_sprints(data)
        self.seasons = compile_seasons(self.races)
        self.statuses = get_statuses(data)

    def compute(self):
        self.drivers, self.teams = compute_ratings(
            self.seasons, self.drivers, self.teams, self.qualis, self.sprints, self.statuses
        )

    def save_ratings(self):
        save_ratings(self.teams, self.drivers)

    def print_today_grid(self):
        print_today_grid(self.teams, self.drivers, self.races)

    def show_plot_today_grid(self):
        drivers = get_last_race_drivers(self.drivers, self.races)
        teams = get_last_race_teams(self.teams, self.races)
        plt_drivers = plot_drivers_rating(drivers, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date())
        plt_teams = plot_teams_rating(teams, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date())
        if plt_drivers is None or plt_teams is None:
            return
        plt_drivers.show()
        plt_teams.show()
        plt_drivers.close()
        plt_teams.close()

    def save_plot_today_grid(self, name="current_grid"):
        drivers = get_last_race_drivers(self.drivers, self.races)
        teams = get_last_race_teams(self.teams, self.races)
        plt_drivers = plot_drivers_rating(drivers, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date())
        plt_teams = plot_teams_rating(teams, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date())
        if plt_drivers is None or plt_teams is None:
            return
        plt_drivers.savefig(f"ratings/{name}_drivers.png", dpi=300)
        plt_teams.savefig(f"ratings/{name}_teams.png", dpi=300)
        plt_drivers.close()
        plt_teams.close()

    def show_plot_driver_rating(self, driver_name, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        driver = get_driver_by_name(self.drivers, driver_name)
        if not driver:
            return
        plt = plot_driver_rating(driver, startdate, enddate)
        if plt is None:
            return
        plt.show()
        plt.close()

    def show_plot_drivers_rating(self, driver_names, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        drivers = [get_driver_by_name(self.drivers, name) for name in driver_names]
        if not all(drivers):
            return
        plt = plot_drivers_rating(drivers, startdate, enddate)
        if plt is None:
            return
        plt.show()
        plt.close()

    def show_plot_team_rating(self, team_name, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        team = get_team_by_name(self.teams, team_name)
        if not team:
            return
        plt = plot_team_rating(team, startdate, enddate)
        if plt is None:
            return
        plt.show()
        plt.close()

    def show_plot_teams_rating(self, team_names, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        teams = [get_team_by_name(self.teams, name) for name in team_names]
        if not all(teams):
            return
        plt = plot_teams_rating(teams, startdate, enddate)
        if plt is None:
            return
        plt.show()
        plt.close()

    def show_plot_team_vs_driver(self, team_name, driver_name, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        team = get_team_by_name(self.teams, team_name)
        driver = get_driver_by_name(self.drivers, driver_name)
        if not team or not driver:
            return
        plt = plot_team_vs_driver_rating(team, driver, startdate, enddate)
        if plt is None:
            return
        plt.show()
        plt.close()

    def show_plot_teams_vs_drivers(self, team_names, driver_names, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        teams = [get_team_by_name(self.teams, name) for name in team_names]
        drivers = [get_driver_by_name(self.drivers, name) for name in driver_names]
        if not all(teams) or not all(drivers):
            return
        plt = plot_teams_vs_drivers(teams, drivers, startdate, enddate)
        if plt is None:
            return
        plt.show()
        plt.close()

    def save_plot_driver_rating(self, driver_name, name="driver_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        driver = get_driver_by_name(self.drivers, driver_name)
        if not driver:
            return
        plt = plot_driver_rating(driver, name, startdate, enddate)
        if plt is None:
            return
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def save_plot_drivers_rating(self, driver_names, name="drivers_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        drivers = [get_driver_by_name(self.drivers, name) for name in driver_names]
        if not all(drivers):
            return
        plt = plot_drivers_rating(drivers, name, startdate, enddate)
        if plt is None:
            return
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def save_plot_team_rating(self, team_name, name="team_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        team = get_team_by_name(self.teams, team_name)
        if not team:
            return
        plt = plot_team_rating(team, name, startdate, enddate)
        if plt is None:
            return
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def save_plot_teams_rating(self, team_names, name="teams_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        teams = [get_team_by_name(self.teams, name) for name in team_names]
        if not all(teams):
            return
        plt = plot_teams_rating(teams, name, startdate, enddate)
        if plt is None:
            return
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def save_plot_team_vs_driver(self, team_name, driver_name, name="team_vs_driver_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        team = get_team_by_name(self.teams, team_name)
        driver = get_driver_by_name(self.drivers, driver_name)
        if not team or not driver:
            return
        plt = plot_team_vs_driver_rating(team, driver, name, startdate, enddate)
        if plt is None:
            return
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def save_plot_teams_vs_drivers(self, team_names, driver_names, name="teams_vs_drivers_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        teams = [get_team_by_name(self.teams, name) for name in team_names]
        drivers = [get_driver_by_name(self.drivers, name) for name in driver_names]
        if not all(teams) or not all(drivers):
            return
        plt = plot_teams_vs_drivers(teams, drivers, name, startdate, enddate)
        if plt is None:
            return
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def print_driver_rating(self, driver_name):
        driver = get_driver_by_name(self.drivers, driver_name)
        if not driver:
            return
        print_driver_rating(driver)

    def print_team_rating(self, team_name):
        team = get_team_by_name(self.teams, team_name)
        if not team:
            return
        print_team_rating(team)
