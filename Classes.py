import pandas as pd
import numpy as np
import typing
class wHouse:
    
    def __init__(self,tag:str, position:tuple[float, float],surplus:int):
        self.tag=tag
        self.long, self.lat=position
        self.position=position
        self.surplus=surplus
        self.comply=abs(self.surplus)<=5
        pass
    def set_position(self,new_position:tuple[float,float]):
        self.long, self.lat=new_position
        self.position=new_position
    def add(self,amount):
        self.surplus+=amount
        self.comply=abs(self.surplus)<=5
    def remove(self,amount):
        self.surplus-=amount
        self.comply=abs(self.surplus)<=5

def distance(WH1:wHouse,WH2:wHouse)->float:
    def to_radians(arg:float)->float:
        return arg*2*np.pi/360
    lat1=to_radians(WH1.lat)
    lon1=to_radians(WH1.long)
    lat2=to_radians(WH2.lat)
    lon2=to_radians(WH2.long)
    d=np.arccos(np.sin(lat1)*np.sin(lat2)+np.cos(lat1)*np.cos(lat2)*np.cos(lon2-lon1))*6371
    return d
#%%
pop=300
map_list=np.empty(300,dtype=object)
for i in range(pop):
    map_list[i-1]=wHouse(str(i),(np.random.uniform(-15.0,15.0),np.random.uniform(-20.0,20.0)),np.random.randint(-100,100))
#%%
class map:
    def __init__(self,map_list):
        self.map_list=map_list
        self.distances=np.zeros((pop,pop),dtype=float)
        for i in range(len(self.map_list)):
            for j in range(len(self.map_list)):
                if i!=j:
                    self.distances[i][j]=distance(self.map_list[i], self.map_list[j])  
#%%

while any (not warehouse.comply for warehouse in map_list):
