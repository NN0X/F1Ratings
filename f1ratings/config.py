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

#Current Season
CURRENT_SEASON_LENGTH = 24

# Ratings
BASE_DRIVER_RATING = 1200
BASE_TEAM_RATING = 1200

# Ratings Computation Drivers
PENALTY_FACTOR = 0.15 # anti-de Cesaris factor

DIFF_TEAMMATES = 0.7
RACE_BONUS = 0.45
QUALI_BONUS = 0.25
SPRINT_BONUS = 0.05
DIFF_RACE = 0.1
DIFF_SPRINT = 0.05

ROOKIE_RATING_COUNT = 7
ROOKIE_MODIFIER = 1.3

# Ratings Computation Teams
TEAM_RACE_WEIGHT = 1
TEAM_QUALI_WEIGHT = 0.7
TEAM_SPRINT_WEIGHT = 0.15

DIFF_TEAM_GROWTH_WEIGHT = 4
DIFF_TEAM_DUMPER_WEIGHT = 4

DRIVER_RATING_DEVIATION_MULTIPLIER = 1.2

# Ratings Speed of Change
SWING_MULTIPLIER = 6
SWING_MULTIPLIER_TEAM = 500

# Team Ratings Meta Rules
RESET_TEAM_RATINGS_SEASON = False
RERATE_TEAM_RATINGS_SEASON = False
RESET_TEAM_REENTRY_RATINGS = True

# Ratings Decay
TEAM_RATING_DECAY_NUM_RACES = 3
DRIVER_RATING_DECAY_NUM_RACES = 100

# Number of Races Influence
NUM_RACES_INFLUENCE_TREND = 5
NUM_RACES_INFLUENCE_STEEPNESS = 1.5
