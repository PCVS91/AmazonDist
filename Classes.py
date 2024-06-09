import pandas as pd
import numpy as np
import typing
import string
import copy

class wHouse:
    def __init__(self, tag: str, name: str, longitude: float, latitude: float, surplus: int):
        self.tag = tag
        self.name = name
        self.lon = longitude
        self.lat = latitude
        self.surplus = surplus
        self.comply = abs(self.surplus) <= 5

    def add(self, amount):
        self.surplus += amount
        self.comply = abs(self.surplus) <= 5

def distance(WH1: wHouse, WH2: wHouse) -> float:
    def to_radians(arg: float) -> float:
        return arg * 2 * np.pi / 360

    lat1 = to_radians(WH1.lat)
    lon1 = to_radians(WH1.lon)
    lat2 = to_radians(WH2.lat)
    lon2 = to_radians(WH2.lon)
    d = np.arccos(np.sin(lat1) * np.sin(lat2) + np.cos(lat1) * np.cos(lat2) * np.cos(lon2 - lon1)) * 6371
    return d

#%% Generate/Import data
pop = 300
map_list = np.empty((pop, 5), dtype=object)
map_instances = np.empty(pop, dtype=object)

def distances(map_instances):
    map_distances = np.zeros((pop, pop), dtype=float)
    for i in range(len(map_instances)):
        for j in range(len(map_instances)):
            if i != j:
                map_distances[i][j] = distance(map_instances[i], map_instances[j])
    return map_distances

# Define the alphabet
alphabet = string.ascii_uppercase

# Initialize an empty list to store the patterns
patterns = []

# Generate patterns of length 3
for first in alphabet:
    for second in alphabet:
        for third in alphabet:
            if len(patterns) <= pop:
                patterns.append(first + second + third)
            else:
                break

for i in range(pop):
    map_list[i, :] = patterns[i], 2 * patterns[i], np.random.uniform(-15.0, 15.0), np.random.uniform(-20.0, 20.0), np.random.randint(-100, 100)
    map_instances[i] = wHouse(*map_list[i, :])

#%%Create Dataframes
map_df = pd.DataFrame(
    data = map_list,
    columns = ['Tag', 'Warehouse', 'Longitude', 'Latitude', 'Surplus']
)
map_df.set_index('Tag', inplace = True)
distances_df = pd.DataFrame(
    data = distances(map_instances),
    index = map_df.index,
    columns = map_df.index
)

#%%


def send(local_df, sender='', carry_on=0, visited=None):
    if visited is None:
        visited = []
    transfer_occurred = False

    def transfer(sender: str, receiver: str, amount: int, df: pd.DataFrame = None):
        if df is None:
            df = local_df
        df.at[sender, 'Surplus'] -= amount
        df.at[receiver, 'Surplus'] += amount
        return df

    if not sender:
        sender = local_df['Surplus'].idxmax()

    receiver = distances_df.loc[sender, local_df.loc[local_df['Surplus'] < 0].index].idxmin()
    print(f"Sender: {sender}, Receiver: {receiver}, Carry_on: {carry_on}, Visited: {visited}")
    if local_df.loc[sender, 'Surplus'] <= abs(local_df.loc[receiver, 'Surplus']):
        resto = 0 if local_df.loc[sender, 'Surplus'] % 25 >= 5 else local_df.loc[sender, 'Surplus'] % 25
        amount = local_df.loc[sender, 'Surplus'] - resto
        local_df = transfer(sender, receiver, amount)
        if amount> 0:
            transfer_occurred = True
    else:
        visited.append(receiver)
        amount = abs(local_df.loc[receiver, 'Surplus'] + carry_on)
        closest_notcomply_sender = distances_df.loc[sender, local_df.loc[(local_df['Surplus'] <= 0) & (~local_df.index.isin(visited))].index].idxmin()
        closest_notcomply_receiver = distances_df.loc[receiver, local_df.loc[local_df['Surplus'] < 0].index].idxmin()

        if distances_df.loc[sender, closest_notcomply_sender] <= distances_df.loc[receiver, closest_notcomply_receiver]:
            local_df = transfer(sender, receiver, amount)
            if amount > 0:
                transfer_occurred = True
        else:
            carry_on += abs(local_df.loc[receiver, 'Surplus'])
            print(f"Sender: {sender}, Receiver: {receiver}, Amount: {amount}, Carry_on: {carry_on}, Visited: {visited}")
            local_df, transfer_occurred = send(local_df, sender=receiver, carry_on=carry_on, visited=visited)
    return local_df, transfer_occurred

#%%
local_df = copy.copy(map_df)
count = 0
visited = []  # Initialize the visited list outside the loop
while any(not warehouse.comply for warehouse in map_instances):
    count += 1
    local_df, transfer_occurred = send(local_df, visited=visited)  # Pass visited list
    print(transfer_occurred)
    if not transfer_occurred:
        break
