from .config import *
from .dataclasses import *

def compute_team_rating_change(teams, team_id, teams_weighted_pos):
    team_weighted_pos = next((pos for pos in teams_weighted_pos if pos[0] == team_id), None)
    if not team_weighted_pos:
        return 0
    team_pos = team_weighted_pos[1]
    best_pos = min(pos[1] for pos in teams_weighted_pos)
    worst_pos = max(pos[1] for pos in teams_weighted_pos)
    if best_pos == worst_pos:
        return 0

    teams_weighted_pos.sort(key=lambda x: x[1])
    middle_pos = teams_weighted_pos[len(teams_weighted_pos)//2][1]
    raw_change = middle_pos - team_pos + len(teams_weighted_pos)
    raw_change = raw_change / (worst_pos - best_pos)

    team = next((t for t in teams if t.id == team_id), None)
    if not team or not team.ratings:
        return 0
    team_rating = team.ratings[-1][0]

    teams_filtered = [team for team in teams if team.id in [pos[0] for pos in teams_weighted_pos]]
    total_rating = sum(t.ratings[-1][0] for t in teams_filtered if t.ratings)
    num_teams = len(teams_filtered)
    if num_teams == 0:
        return 0
    average_opponent_rating = total_rating / num_teams
    rating_change = 1 / (1 + 10 ** ((average_opponent_rating - team_rating) / 400))
    final_change = raw_change * rating_change

    return final_change

def rerate_teams(season, teams):
    team_ids_in_season = set()
    for race in season.races:
        for result in race.results:
            if result[1] not in team_ids_in_season:
                team_ids_in_season.add(result[1])
    teams_in_season = [team for team in teams if team.id in team_ids_in_season]
    if not teams_in_season:
        return teams
    ratings = [team.ratings[-1][0] for team in teams_in_season if team.ratings]
    if not ratings:
        return teams
    median_rating = sorted(ratings)[len(ratings) // 2]
    for team in teams:
        if team.id not in team_ids_in_season:
            continue
        if team.ratings:
            team_rating = team.ratings[-1][0]
            normalized_rating = (team_rating - median_rating) + BASE_TEAM_RATING
            team.ratings.append((normalized_rating, None))  # Append new intermediate rating
        else:
            team.ratings.append((BASE_TEAM_RATING, None))

    return teams

def compute_teams_rating_decay(teams, decay_full_num_races, num_races_weight):
    decays = {}
    for team in teams:
        diff = team.ratings[-1][0] - BASE_TEAM_RATING
        if diff == 0:
            continue
        decay = diff / (decay_full_num_races/num_races_weight)
        decays[team.id] = decay
    return decays

def reset_team_reentry_ratings(seasons, season, teams):
    prev_year = season.year - 1
    prev_season = next((s for s in seasons if s.year == prev_year), None)
    if not prev_season:
        return teams

    current_season_team_ids = set()
    for race in season.races:
        for result in race.results:
            current_season_team_ids.add(result[1])
    previous_season_team_ids = set()
    for race in prev_season.races:
        for result in race.results:
            previous_season_team_ids.add(result[1])
    for team in teams:
        if team.id in current_season_team_ids and team.id not in previous_season_team_ids:
            team.ratings.append((BASE_TEAM_RATING, None))
    return teams
