from dataclasses import dataclass
from datetime import datetime

@dataclass
class Driver:
    id: int
    forename: str
    surname: str
    ratings: list # (rating, date)
    first_race_date: datetime.date = None
    last_race_date: datetime.date = None
    def __str__(self):
        if self.ratings is None:
            return f"{self.forename} {self.surname} (ID: {self.id}) | Rating: N/A"
        return  f"{(self.forename + " " + self.surname):<40} | {round(self.ratings[-1][0]):>5} " \
                f"Peak: {round(max(self.ratings, key=lambda y: y[0])[0]):>5} " \
                f"{max(self.ratings, key=lambda y: y[0])[1] if max(self.ratings, key=lambda y: y[0])[1] else 'N/A'}"
    def __hash__(self):
        return hash(self.id)

@dataclass
class Team:
    id: int
    name: str
    ratings: list # (rating, date)
    first_race_date: datetime.date = None
    last_race_date: datetime.date = None
    def __str__(self):
        if self.ratings is None:
            return f"{self.name} (ID: {self.id}) | Rating: N/A"
        return  f"{self.name:<40} | {round(self.ratings[-1][0]):>5} " \
                f"Peak: {round(max(self.ratings, key=lambda y: y[0])[0]):>5} " \
                f"{max(self.ratings, key=lambda y: y[0])[1] if max(self.ratings, key=lambda y: y[0])[1] else 'N/A'}"
    def __hash__(self):
        return hash(self.id)

@dataclass
class Race:
    id: int
    name: str
    date: datetime.date
    circuit_id: int
    results: list # (driver_id, team_id, position, additional_info)
    starting_positions: list # (driver_id, starting_position)
    total_time: float = None
    def __str__(self):
        return f"{self.name} (ID: {self.id}) | Date: {self.date} | Circuit ID: {self.circuit_id}"

@dataclass
class Qualifying:
    race_id: int
    results: list # (driver_id, team_id, position)
    def __str__(self):
        sorted_results = sorted(self.results, key=lambda x: x[1])
        return f"Qualifying to race ID: {self.race_id} | Pole driver ID: {sorted_results[0][0]}"

@dataclass
class Sprint:
    race_id: int
    results: list # (driver_id, team_id, position, additional_info)
    starting_positions: list # (driver_id, starting_position)
    total_time: float = None
    def __str__(self):
        sorted_results = sorted(self.results, key=lambda x: x[2])
        return f"Sprint to race ID: {self.race_id} | Winner driver ID: {sorted_results[0][0]}"

@dataclass
class Season:
    year: int
    races: list # sorted by date
    def __str__(self):
        return f"Season: {self.year} with {len(self.races)} races"
