import pandas as pd
import numpy as np
import typing
import string
class wHouse:
    
    def __init__(self,tag:str,name:str, longitude:float, latitude:float,surplus:int):
        self.tag=tag
        self.name=name
        self.lon=longitude
        self.lat=latitude
        self.surplus=surplus
        self.comply=abs(self.surplus)<=5
    def add(self,amount):
        self.surplus+=amount
        self.comply=abs(self.surplus)<=5
        map_df[self.tag]['Surplus']+=amount
    def remove(self,amount):
        self.surplus-=amount
        self.comply=abs(self.surplus)<=5
        map_df[self.tag]['Surplus']-=amount

def distance(WH1:wHouse,WH2:wHouse)->float:
    def to_radians(arg:float)->float:
        return arg*2*np.pi/360
    lat1=to_radians(WH1.lat)
    lon1=to_radians(WH1.lon)
    lat2=to_radians(WH2.lat)
    lon2=to_radians(WH2.lon)
    d=np.arccos(np.sin(lat1)*np.sin(lat2)+np.cos(lat1)*np.cos(lat2)*np.cos(lon2-lon1))*6371
    return d
def send(tag1,tag2,amount):
    
#%%
pop=300
map_list=np.empty(((pop),5),dtype=object)
map_instances=np.empty(pop,dtype=object)
# Define the alphabet
alphabet = string.ascii_uppercase

# Initialize an empty list to store the patterns
patterns = []

# Generate patterns of length 3

for first in alphabet:
    for second in alphabet:
        for third in alphabet:
            if len(patterns)<=pop:
                patterns.append(first + second + third)
            else:
                break
            
for i in range(pop):
    map_list[i,:]=patterns[i],2*patterns[i],np.random.uniform(-15.0,15.0),np.random.uniform(-20.0,20.0),np.random.randint(-100,100)
    map_instances[i]=wHouse(*map_list[i,:])
    #%%
def distances(map_instances):
    map_distances=np.zeros((pop,pop),dtype=float)
    for i in range(len(map_instances)):
        for j in range(len(map_instances)):
            if i!=j:
                map_distances[i][j]=distance(map_instances[i], map_instances[j])  
    return map_distances
#%%
#Create Dataframe
map_df=pd.DataFrame(
    data=map_list, 
    columns=['Tag', 'Warehouse', 'Longitude', 'Latitude', 'Surplus']
    )
map_df.set_index('Tag', inplace=True)
#%%

while any (not warehouse.comply for warehouse in map_list):
#%%

