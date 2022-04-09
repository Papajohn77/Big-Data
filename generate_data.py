import csv
import random
import argparse
from scipy.stats import skewnorm
from matplotlib import pyplot as plt

def read_centroids(centroids_file_path):
    centroids = []
    with open(centroids_file_path) as centroids_file:
        for centroid in csv.reader(centroids_file):
            centroids.append(centroid)
    return centroids

def generate_points_around_centroids(centroids, num_of_points):
    points = []
    for x_centroid, y_centroid in centroids:
        # When a = 0 the distribution is identical to normal distribution.
        x_skews = skewnorm.rvs(a=0, scale=1.5, size=num_of_points)
        y_skews = skewnorm.rvs(a=0, scale=1.5, size=num_of_points)
        for x_skew, y_skew in zip(x_skews, y_skews):
            x = float(x_centroid) + x_skew
            y = float(y_centroid) + y_skew
            points.append((x, y))
    return points

def write_points(points_file_path, points):
    with open(points_file_path, 'w') as points_file:
        for point in points:
            csv.writer(points_file).writerow(point)

def draw_points(points):
    x, y = zip(*points)
    plt.scatter(x, y)
    plt.savefig('points')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True,
        help="path to the file containing the centroids")
    parser.add_argument("-o", required=True,
        help="path to the file where the points will be written")
    parser.add_argument("-n", nargs='?', const=400000, type=int,
        help="number of points to be generated around each centroid")
    parser.add_argument("-d", action="store_true", help="draw points")
    args = parser.parse_args()

    centroids_file_path, points_file_path, num_of_points  = args.i, args.o, args.n

    centroids = read_centroids(centroids_file_path)
    points = generate_points_around_centroids(centroids, num_of_points)
    write_points(points_file_path, points)

    if args.d:
        draw_points(points)
