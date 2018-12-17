import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import glob


from prime_numbers import return_list_of_primes, load_primes, save_primes, is_prime 

def Generate_Random_Path(cities,seed=0):
    #return a random path, input cities
    #The returned path does not include the north pole at ID = 0, where the voyage should start and end
    np.random.seed(seed=seed)
    NumberOfCities = len(cities)
    Path = np.arange(1,NumberOfCities)
    Path = np.random.permutation(Path)
    return Path

def is_step_10(StepNumber):
    #returns 1 of is a %10 step, 0 otherwise
    if StepNumber % 10 == 0:
        return 1
    else:
        return 0
    
def dist(cities, City_1, City_2):
    #Input city IDs, output distance
    return np.linalg.norm (cities.iloc[City_1]['X':'Y'] - cities.iloc[City_2]['X':'Y']  )


def length_of_path(path, cities,prime_list):
    length = 0

    #distance between NP and 1st city
    length += dist(cities,0,path[0])

    #for all cities calculate distances
    for i in range(len(path)-1):
        length += dist_primes(path,cities,prime_list,i) 
#use that step = i + 2, first step is 0-> city1 (path0), so the second step is path0->path2
       
    #distance between last city and NP
    length += dist(cities,path[len(path)-1], 0)
    
    return length


def dist_primes(path,cities,prime_list,i):
    step = i+2 # see above for arguments on this
    
    #make exception if i = len(path)-1, then it has to go back to 0
    if (i==len(path)-1):
        if (step % 10 == 0): #if step % 10 and not prime, take longer
            if is_prime(step,prime_list):
                return dist(cities, path[i], 0)
            else:
                return  ( 1.10 * dist(cities, path[i], 0)  )
        else:
            return dist(cities, path[i], 0)        
        
    #normal scenario, where i is in the middle
    if (step % 10 == 0): #if step % 10 and not prime, take longer
        if is_prime(step,prime_list):
            return dist(cities, path[i], path[i+1])
        else:
            return  ( 1.10 * dist(cities, path[i], path[i+1])  )
    else:
        return dist(cities, path[i], path[i+1])
    

def length_difference(cities, original_path, path_ID1, path_ID2, prime_list):
#calculates the  difference in length between the original_path and a new path where city_IDs 1 and 2 at the path IDs are swopped
    #positive if proposed length is longer than original path
    #first Calculate relevant distances of original_path (from and to city ID1,2)
    original_path_length = 0
    original_path_length += dist_primes(original_path,cities,prime_list, path_ID1-1)+dist_primes(original_path,cities,prime_list, path_ID1)
    original_path_length += dist_primes(original_path,cities,prime_list, path_ID2-1)+dist_primes(original_path,cities,prime_list, path_ID2)
    
    #calculate proposed path
    proposed_path = np.copy(original_path)
    proposed_path[path_ID1] = original_path[path_ID2]
    proposed_path[path_ID2] = original_path[path_ID1]
    
    #calculate relevant distances for new path
    proposed_path_length = 0
    proposed_path_length += dist_primes(proposed_path,cities,prime_list, path_ID1-1) + dist_primes(proposed_path,cities,prime_list, path_ID1)
    proposed_path_length += dist_primes(proposed_path,cities,prime_list, path_ID2-1) + dist_primes(proposed_path,cities,prime_list, path_ID2)
    
    #substract
    return  proposed_path_length - original_path_length 


def rearange_cities(cities,path):
    #arranges cities according to optimal path
    cities_plot = cities.copy()
    path_to_index = np.insert(path, 0, 0)
    for i in range(0,len(cities)):
        cities_plot.iloc[i] = cities.iloc[path_to_index[i]]
    return cities_plot


def visualize_path(cities,path):
    cities_in_order = rearange_cities(cities,path)
    plt.plot( cities_in_order['X'] , cities_in_order['Y'] )
    
def MC_step(cities,path,length,prime_list,beta):
    path_ID1, path_ID2 = np.random.randint(len(path)),np.random.randint(len(path))
    difference = length_difference(cities,path,path_ID1,path_ID2,prime_list)
    if difference >= 0:
        if np.random.random() < energy(difference,beta): 
            #swop anyway, even though it is worse
            new_path = np.copy(path)
            new_path[path_ID1] = path[path_ID2]
            new_path[path_ID2] = path[path_ID1]
            new_length = length + difference
            return new_path, new_length
        else:
            return path, length
                    
    elif difference < 0:
        new_path = np.copy(path)
        new_path[path_ID1] = path[path_ID2]
        new_path[path_ID2] = path[path_ID1]
        new_length = length + difference
        return new_path, new_length
    
    
def energy(difference,beta):
    #low difference corresponds to high energy
    return np.exp(- difference/beta)


def save_best(cities,min_path,min_length):
    cities_ordered = rearange_cities(cities,min_path)['CityId'].astype(np.int)
    frame = cities_ordered.to_frame()
    frame.columns = ['Path']
    frame = frame.append({'Path':0},ignore_index=True)
    SAVE_PATH = 'results/path_' + str(min_length.astype(int)) + '.csv'
    frame.to_csv(SAVE_PATH,index=False) #no index!
    print("saved as " + str(SAVE_PATH))

def load_best():
    filelist = glob.glob("results/*.csv")
    lengths = [ re.search('path_(.*).csv',file)[1] for file in filelist ] 
    min_length = np.min(np.array(lengths).astype(np.int))
    PATH_MIN = 'results\\path_' + str(min_length) + '.csv'
    frame = np.array ( pd.read_csv(PATH_MIN)[1:-1] )
    frame = frame.reshape(len(frame))
    return frame , min_length