import pandas as pd
import numpy as np
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

# Generate/Import data
pop = 300
map_list = np.empty((pop, 5), dtype=object)
map_instances = np.empty(pop, dtype=object)

def distances(map_instances):
    map_distances = np.zeros((pop, pop), dtype=float)
    for i in range(len(map_instances)):
        for j in range(len(map_instances)):
            if i != j:
                map_distances[i][j] = distance(map_instances[i], map_instances[j])
            else:
                map_distances[i][j] = np.nan
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

# Populate the map_list and map_instances
for i in range(pop):
    map_list[i, :] = patterns[i], 2 * patterns[i], np.random.uniform(-15.0, 15.0), np.random.uniform(-20.0, 20.0), np.random.randint(-100, 100)
    map_instances[i] = wHouse(*map_list[i, :])

# Create DataFrames
map_df = pd.DataFrame(
    data = map_list,
    columns = ['Tag', 'Warehouse', 'Longitude', 'Latitude', 'Surplus']
)
map_df.set_index('Tag', inplace=True)
distances_df = pd.DataFrame(
    data = distances(map_instances),
    index = map_df.index,
    columns = map_df.index
)

# For simplicity, we will only keep surplus, since distances are all already calculated
local = copy.copy(map_df.Surplus)

# Initialize log file
log_file = open("transfer_log.txt", "w")

total_distance_traveled = 0

def pull(local: pd.Series):
    def transfer(sender: str, receiver: str, amount: int):
        local[sender] -= amount
        local[receiver] += amount
        return amount != 0

    transfer_amounts = {}
    total_distance = 0 
    receiver = local.idxmin()
    sender = distances_df.loc[receiver, local[local > 0].index].idxmin()
    distance_r_s = distances_df.loc[sender, receiver]
    
    # Warehouses between sender and receiver with negative surplus for potential drops
    between = local.loc[
        (distances_df.loc[sender, :] < distance_r_s) & 
        (distances_df.loc[receiver, :] < distance_r_s) &
        (local < 0)
    ].index
    # Sort with shorter distance to receiver
    between = distances_df.loc[sender, between].sort_values().index
    
 
    amount = min([abs(local[receiver]), local[sender]])
    transfer_occurred = transfer(sender, receiver, amount)
    transfer_amounts[sender] = -amount
    transfer_amounts[receiver] = amount
    
    transfer_path = [receiver]
    last=sender
    for bt in between:
        if local[sender] <= 0:
            break
        if bt==between[0]:
            distance_bt_r = distances_df.loc[bt, receiver]  # Measure to the receiver 
        else:
            distance_bt_r = distances_df.loc[bt, last]
        total_distance += distance_bt_r
        amount = min([abs(local[bt]), local[sender]])
        transfer_occurred = transfer(sender, bt, amount)
        transfer_path.append(bt)
        transfer_amounts[bt] = amount
        transfer_amounts[sender]-=amount
        last=bt
    total_distance+=distances_df.loc[last,receiver]
    transfer_path.append(sender)
    
    
    return local, transfer_occurred, total_distance, transfer_amounts, transfer_path[::-1]


# Perform pulls and log details
count=0
while any(abs(local) > 5):
    count+=1
    local, transfer_occurred, total_distance, transfer_amounts, transfer_path = pull(local)
    total_distance_traveled += total_distance
    if transfer_path and abs(transfer_amounts[transfer_path[0]])<5:
        continue
    # Log the pull information
    log_file.write(f"Transfer: {count} Distance: {total_distance:.2f} km\n")
    log_file.write(" -> ".join(transfer_path) + "\n")
    amounts_line = " ".join([f"{transfer_amounts[wh]:<6}" for wh in transfer_path])
    log_file.write(amounts_line + "\n\n")
    if not transfer_occurred or all(local >= 0) or all(local <= 0):
        break
    
# Log total distance traveled
log_file.write(f"Total distance traveled: {total_distance_traveled:.2f} km\n\n")


log_file.close()
