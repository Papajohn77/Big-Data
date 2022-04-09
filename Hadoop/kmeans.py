from math import sqrt
from mrjob.job import MRJob
from mrjob.step import MRStep

class KMeans(MRJob):

    def configure_args(self):
        super(KMeans, self).configure_args()

        self.add_file_arg(
            '--centroids-file',
            dest='centroids_file',
            help='path to the file containing the centroids.'
        )

    def steps(self):
        return[
            MRStep(mapper_init=self.load_centroids,
                   mapper=self.mapper,
                   reducer=self.reducer)
        ]

    # This method is executed before mappers process any input.
    def load_centroids(self):
        self.__centroids = []

        with open(self.options.centroids_file) as centroids_file:
            for line in centroids_file:
                x, y = line.strip().split(',')
                centroid = (float(x), float(y))
                self.__centroids.append(centroid)

    def __calculate_euclidean_dist(self, point, centroid):
        x1, y1 = point
        x2, y2 = centroid
        return sqrt((x2 - x1)**2 + (y2 - y1)**2)

    # The line will be a raw line of the input file, with newline (\n) stripped.
    def mapper(self, _, line):
        x, y = line.split(',')
        point = (float(x), float(y))

        min_euclidean_dist = float('inf')
        closest_centroid = None
        for centroid in self.__centroids:
            euclidean_dist = self.__calculate_euclidean_dist(point, centroid)
            if euclidean_dist < min_euclidean_dist:
                min_euclidean_dist = euclidean_dist
                closest_centroid = centroid

        yield closest_centroid, point

    def reducer(self, centroid, points):
        n, sum_x, sum_y = 0, 0, 0
        for x, y in points:
            sum_x += x
            sum_y += y
            n += 1
        mean_x = sum_x / n
        mean_y = sum_y / n

        yield centroid, (mean_x, mean_y)

if __name__ == "__main__":
    KMeans.run()
