#!/usr/bin/env python
"""mapper.py"""

__authors__ = "Evangelia Panourgia, Iwannis Papadatos"

# import libraries 
import csv
from math import sqrt

def calculate_euclidian_distance(xx, yy, cc1, cc2): return sqrt((xx - cc1)**2 + (yy - cc2)**2) # calculate euclidian distance between two points xx, yy

# read generated data 
def read_data_points(url):
    list_data_points = [] # Initialize a list with centers 
    with open(url, 'r') as file:
        reader = csv.reader(file)
        for row in reader: list_data_points.append(row)
    file.close()
    return(list_data_points)

def read_centers(file):
    list_centers = [] # Initialize a list with centers 
    with open(file, 'r') as file:
        reader = csv.reader(file)
        for row in reader: list_centers.append(row)
    file.close()
    return(list_centers)

url_generated_data = 'src\data\dataset.csv'
list_data = read_data_points(url_generated_data)
list_centers = read_centers('src\data\centers.csv') 
 
for i in list_data: # for each data point 
    res1 = calculate_euclidian_distance(float(i[0]), float(i[1]), float(list_centers[0][0]),float(list_centers[0][1])) # dist point with first cendroid 
    res2 = calculate_euclidian_distance(float(i[0]), float(i[1]), float(list_centers[1][0]),float(list_centers[1][1])) # dist point with second centroid
    res3 = calculate_euclidian_distance(float(i[0]), float(i[1]), float(list_centers[2][0]),float(list_centers[2][1])) # dist point with third cendroid

    # hold nearest distance 
    smallest, euclidian_ceneter = res1, list_centers[0]
    if (res2 < res1) and (res2 < res3): smallest, euclidian_ceneter = res2, list_centers[1]
    elif (res3 < res1): smallest, euclidian_ceneter = res3, list_centers[2]

    print(str(list_data[0]), ',' + str(list_data[1]), ',' + str(euclidian_ceneter)) # reducer takes from here    
    