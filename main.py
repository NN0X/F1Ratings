import kagglehub
from kagglehub import KaggleDatasetAdapter
from datetime import datetime
from dataclasses import dataclass

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

def load_data():
    print("Loading data from Kaggle dataset...")
    data = {}
    for file in FILES:
        file_name = file.split('.')[0]
        data[file_name] = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            KAGGLE_PATH,
            file
        )
    return data

@dataclass
class Driver:
    id: int
    forename: str
    surname: str
    first_race_date: datetime.date = None
    last_race_date: datetime.date = None
    ratings: list = None
    def __str__(self):
        if self.ratings is None:
            return f"{self.forename} {self.surname} (ID: {self.id}) | Rating: N/A"
        return f"{self.forename} {self.surname} (ID: {self.id}) | Rating: {self.ratings[-1]}"

@dataclass
class Team:
    id: int
    name: str
    first_race_date: datetime.date = None
    last_race_date: datetime.date = None
    drivers: dict = None # key: raceId, value: list of Driver objects
    ratings: list = None
    def __str__(self):
        if self.ratings is None:
            return f"{self.name} (ID: {self.id}) | Rating: N/A"
        return f"{self.name} (ID: {self.id}) | Rating: {self.ratings[-1]}"

def get_drivers(data):
    drivers = data["drivers"]
    driver_list = []
    for _, row in drivers.iterrows():
        driver = Driver(
            id=row['driverId'],
            forename=row['forename'],
            surname=row['surname']
        )
        driver_list.append(driver)
    return driver_list

def get_driver_results(data, driver):
    driver_id = driver.id
    if driver_id not in data["drivers"]['driverId'].values:
        print(f"Driver ID {driver_id} not found.")
        return []

    results = data["results"]
    driver_results = results[results['driverId'] == driver_id]
    return driver_results[['raceId', 'positionOrder', 'points']].to_dict('records')

def rating_update_step(drivers: list, teammates: dict, teams: list, race_results: list):
    return "Not implemented yet"

if __name__ == "__main__":
    data = load_data()
