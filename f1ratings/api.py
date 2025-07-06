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
import pickle

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
        if not data:
            raise ValueError("No data fetched from the source.")

        self.drivers = get_drivers(data)
        self.teams = get_teams(data)
        self.races = get_races(data)
        self.qualis = get_qualis(data)
        self.sprints = get_sprints(data)
        self.seasons = compile_seasons(self.races)
        self.statuses = get_statuses(data)

        if not self.drivers:
            raise ValueError("No drivers found in the fetched data.")
        if not self.teams:
            raise ValueError("No teams found in the fetched data.")
        if not self.races:
            raise ValueError("No races found in the fetched data.")
        if not self.qualis:
            raise ValueError("No qualifying sessions found in the fetched data.")
        if not self.sprints:
            raise ValueError("No sprints found in the fetched data.")
        if not self.seasons:
            raise ValueError("No seasons compiled from the fetched data.")
        if not self.statuses:
            raise ValueError("No statuses found in the fetched data.")

    def compute(self):
        self.drivers, self.teams = compute_ratings(
            self.seasons, self.drivers, self.teams, self.qualis, self.sprints, self.statuses
        )

    def save(self, name="f1ratings"):
        with open(f"ratings/{name}.f1", 'wb') as f:
            pickle.dump(self, f)

    def load(self, name="f1ratings"):
        with open(f"ratings/{name}.f1", 'rb') as f:
            obj = pickle.load(f)
        if not isinstance(obj, F1Ratings):
            raise ValueError("Loaded object is not an instance of F1Ratings.")
        self.__dict__.clear()
        self.__dict__.update(obj.__dict__)

    def dump_ratings(self):
        save_ratings(self.teams, self.drivers)

    def get_driver_by_name(self, driver_name):
        driver = get_driver_by_name(self.drivers, driver_name)
        return driver

    def get_team_by_name(self, team_name):
        team = get_team_by_name(self.teams, team_name)
        return team

    def print_today_grid(self):
        print_today_grid(self.teams, self.drivers, self.races)

    def show_plot_today_grid(self):
        drivers = get_last_race_drivers(self.drivers, self.races)
        teams = get_last_race_teams(self.teams, self.races)
        plt_drivers = plot_drivers_rating(drivers, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date())
        plt_teams = plot_teams_rating(teams, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date())
        if plt_drivers is None or plt_teams is None:
            raise ValueError("No data available for plotting.")
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
            raise ValueError("No data available for plotting.")
        plt_drivers.savefig(f"ratings/{name}_drivers.png", dpi=300)
        plt_teams.savefig(f"ratings/{name}_teams.png", dpi=300)
        plt_drivers.close()
        plt_teams.close()

    def show_plot_driver_rating(self, driver_name, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        driver = get_driver_by_name(self.drivers, driver_name)
        if not driver:
            raise ValueError(f"Driver '{driver_name}' not found.")
        plt = plot_driver_rating(driver, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.show()
        plt.close()

    def show_plot_drivers_rating(self, driver_names, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        drivers = [get_driver_by_name(self.drivers, name) for name in driver_names]
        if not all(drivers):
            for name in driver_names:
                if not get_driver_by_name(self.drivers, name):
                    raise ValueError(f"Driver '{name}' not found.")
        plt = plot_drivers_rating(drivers, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.show()
        plt.close()

    def show_plot_team_rating(self, team_name, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        team = get_team_by_name(self.teams, team_name)
        if not team:
            raise ValueError(f"Team '{team_name}' not found.")
        plt = plot_team_rating(team, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.show()
        plt.close()

    def show_plot_teams_rating(self, team_names, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        teams = [get_team_by_name(self.teams, name) for name in team_names]
        if not all(teams):
            for name in team_names:
                if not get_team_by_name(self.teams, name):
                    raise ValueError(f"Team '{name}' not found.")
        plt = plot_teams_rating(teams, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.show()
        plt.close()

    def show_plot_team_and_driver(self, team_name, driver_name, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        team = get_team_by_name(self.teams, team_name)
        driver = get_driver_by_name(self.drivers, driver_name)
        if not team and not driver:
            raise ValueError(f"Team '{team_name}' and Driver '{driver_name}' not found.")
        elif not team:
            raise ValueError(f"Team '{team_name}' not found.")
        elif not driver:
            raise ValueError(f"Driver '{driver_name}' not found.")
        plt = plot_team_and_driver_rating(team, driver, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.show()
        plt.close()

    def show_plot_teams_and_drivers(self, team_names, driver_names, startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        teams = [get_team_by_name(self.teams, name) for name in team_names]
        drivers = [get_driver_by_name(self.drivers, name) for name in driver_names]
        if not all(teams) or not all(drivers):
            for name in team_names:
                if not get_team_by_name(self.teams, name):
                    raise ValueError(f"Team '{name}' not found.")
            for name in driver_names:
                if not get_driver_by_name(self.drivers, name):
                    raise ValueError(f"Driver '{name}' not found.")
        plt = plot_teams_and_drivers(teams, drivers, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.show()
        plt.close()

    def save_plot_driver_rating(self, driver_name, name="driver_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        driver = get_driver_by_name(self.drivers, driver_name)
        if not driver:
            raise ValueError(f"Driver '{driver_name}' not found.")
        plt = plot_driver_rating(driver, name, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def save_plot_drivers_rating(self, driver_names, name="drivers_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        drivers = [get_driver_by_name(self.drivers, name) for name in driver_names]
        if not all(drivers):
            for name in driver_names:
                if not get_driver_by_name(self.drivers, name):
                    raise ValueError(f"Driver '{name}' not found.")
        plt = plot_drivers_rating(drivers, name, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def save_plot_team_rating(self, team_name, name="team_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        team = get_team_by_name(self.teams, team_name)
        if not team:
            raise ValueError(f"Team '{team_name}' not found.")
        plt = plot_team_rating(team, name, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def save_plot_teams_rating(self, team_names, name="teams_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        teams = [get_team_by_name(self.teams, name) for name in team_names]
        if not all(teams):
            raise ValueError("One or more teams not found.")
        plt = plot_teams_rating(teams, name, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def save_plot_team_and_driver(self, team_name, driver_name, name="team_vs_driver_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        team = get_team_by_name(self.teams, team_name)
        driver = get_driver_by_name(self.drivers, driver_name)
        if not team and not driver:
            raise ValueError(f"Team '{team_name}' and Driver '{driver_name}' not found.")
        elif not team:
            raise ValueError(f"Team '{team_name}' not found.")
        elif not driver:
            raise ValueError(f"Driver '{driver_name}' not found.")
        plt = plot_team_and_driver_rating(team, driver, name, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def save_plot_teams_and_drivers(self, team_names, driver_names, name="teams_vs_drivers_rating_progression", startdate=datetime(1950, 1, 1).date(), enddate=datetime.now().date()):
        teams = [get_team_by_name(self.teams, name) for name in team_names]
        drivers = [get_driver_by_name(self.drivers, name) for name in driver_names]
        if not all(teams) or not all(drivers):
            for name in team_names:
                if not get_team_by_name(self.teams, name):
                    raise ValueError(f"Team '{name}' not found.")
            for name in driver_names:
                if not get_driver_by_name(self.drivers, name):
                    raise ValueError(f"Driver '{name}' not found.")
        plt = plot_teams_and_drivers(teams, drivers, name, startdate, enddate)
        if plt is None:
            raise ValueError("No data available for plotting.")
        plt.savefig(f"ratings/{name}.png", dpi=300)
        plt.close()

    def print_driver_rating(self, driver_name):
        driver = get_driver_by_name(self.drivers, driver_name)
        if not driver:
            raise ValueError(f"Driver '{driver_name}' not found.")
        print_driver_rating(driver)

    def print_team_rating(self, team_name):
        team = get_team_by_name(self.teams, team_name)
        if not team:
            raise ValueError(f"Team '{team_name}' not found.")
        print_team_rating(team)

    def print_driver_last_change(self, driver_name):
        driver = get_driver_by_name(self.drivers, driver_name)
        if not driver:
            raise ValueError(f"Driver '{driver_name}' not found.")
        print_driver_last_change(driver)

    def print_team_last_change(self, team_name):
        team = get_team_by_name(self.teams, team_name)
        if not team:
            raise ValueError(f"Team '{team_name}' not found.")
        print_team_last_change(team)
