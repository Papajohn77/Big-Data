#!/usr/bin/env python3

# This script generates 3M data points
# in the form (x, y), where x and y are real numbers.
# by Evangelia Panourgia, 8190130 
# and  Iwannis Papadatos, 8190314
# 
# USAGE: # run python script with 
# python generateDate.py or
# python generateDate.py -d (if you want to see plots of generated data)
# - - - - - - - - - - -  - - - -  
# OUTPUT : # 
#   case 1 : without arg, generate data and produce dataset.csv file 
#   case 2 : with arg -d, show plot, too. 

# import libraries 
import argparse
import csv
import random
from matplotlib import pyplot as plt
from scipy.stats import skewnorm

def read_centers(file):
    """
    This function reads the centers from the file centers.csv
    Input : file, a file that contains 3 centers in the form (x, y). 
    Condition : Not leave blank lines. 
    Output : list_centers, return a list with 3 centers in the form 
    [['x1', 'y1'], ['x2', 'y2'], ['x3', 'y3']]
    """

    list_centers = [] # Initialize a list with centers 

    with open('src\data\centers.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            list_centers.append(row)
    file.close()
    
    return(list_centers)

def generate_dataponits(centers, data_points):
    """
    This function generates the dataset. 
    Input : cenetrs, a list with centers 
            data_points, an empty list to hold the generated data points 
    Output : data_points, the generated data points - dataset 
    """
    for center in centers:
        # Generate 800k right skewed distances (a = 5), twice the amount of points per center
        distances = skewnorm.rvs(5, size = 800000)
        for i in range(0, 800000, 2):
            # Use random distances to place points around centers
            x = float(center[0]) + [-1,1][random.randrange(2)] * distances[i]
            y = float(center[1]) + [-1,1][random.randrange(2)] * distances[i + 1]
            data_points.append((x, y))
    return data_points

def write_data(data_points):
    """
    This function writes the generated data points to dataset.csv file. 
    Input : data_points, a list with the generates data points in the form [(xx1, yy1, ..., (xx,yy))] 
    Result: file dataset.csv 
    """
    f = open('src\data\dataset.csv', 'w', newline="")
    writer = csv.writer(f)
    for data in data_points:
        writer.writerow(data)
    f.close()

def draw_points(data_points):
    """
    This function draw the generated data points
    Input : data_points, a list with the generates data points in the form [(xx1, yy1, ..., (xx,yy))] 
    Result: show plots with babbles 
    """
    xx, yy = zip(*data_points)
    plt.scatter(xx, yy)
    plt.show()

if __name__ == '__main__': # main 
    
    parser = argparse.ArgumentParser() # Fix Parameters 
    parser.add_argument("-d", help="draw points", action="store_true")
    args = parser.parse_args()

    centers = read_centers('centers.csv') # load three centers
    data_points = [] # Initialize a list that holds all data points
    data_points = generate_dataponits(centers, data_points)
    
    if args.d: # draw points
        draw_points(data_points)

    write_data(data_points) # write data to csv file