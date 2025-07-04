# Dataset
KAGGLE_PATH = "jtrotman/formula-1-race-data"
FILES = ["constructor_results.csv",
         "constructor_standings.csv",
         "constructors.csv",
         "driver_standings.csv",
         "drivers.csv",
         "qualifying.csv",
         "races.csv",
         "results.csv",
         "sprint_results.csv",
         "status.csv"]


# Plots
PLOT_COLORMAP = "nipy_spectral"
PLOT_LINEWIDTH = 0.5
PLOT_MARKERSIZE = 2

# Ratings
BASE_DRIVER_RATING = 1200
BASE_TEAM_RATING = 1200

# Ratings Computation Drivers
PENALTY_FACTOR = 0.1

DIFF_TEAMMATES = 0.5
RACE_BONUS = 0.4
QUALI_BONUS = 0.3
SPRINT_BONUS = 0.05
DIFF_RACE = 0.15
DIFF_SPRINT = 0.025

ROOKIE_RATING_COUNT = 7
ROOKIE_MODIFIER = 1.5

# Ratings Computation Teams
TEAM_RACE_WEIGHT = 0.6
TEAM_QUALI_WEIGHT = 0.3
TEAM_SPRINT_WEIGHT = 0.1

DIFF_TEAM_GROWTH_WEIGHT = 3
DIFF_TEAM_DUMPER_WEIGHT = 2

# Ratings Speed of Change
SWING_MULTIPLIER = 10
SWING_MULTIPLIER_TEAM = 300

# Team Ratings Meta Rules
RESET_TEAM_RATINGS_SEASON = False
RERATE_TEAM_RATINGS_SEASON = False
RESET_TEAM_REENTRY_RATINGS = True

# Ratings Decay
TEAM_RATING_DECAY_NUM_RACES = 5 # 0.2 * ~25
DRIVER_RATING_DECAY_NUM_RACES = 100 # 4 * ~25
