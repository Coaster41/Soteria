import math
import mapbox
import random
from mapbox import Directions

help(mapbox.Directions)

class Information:
    def __init__(self, response, origin, destination):
        self.response = response
        self.A = origin
        self.B = destination
        self.distance = 0
        self.duration = 0
        self.coordinates = []

    def get_coordinates(self):
        if self.response is not None:
            for i in self.response["features"]:
                self.coordinates = i["geometry"]["coordinates"]
        return self.coordinates

    def get_distance(self):
        if self.response is not None:
            for i in self.response["features"]:
                self.distance = i["properties"]["distance"]
        return self.distance

    def get_duration(self):
        if self.response is not None:
            for i in self.response["features"]:
                self.duration = i["properties"]["duration"]
        return self.duration

    def get_origin(self):
        return self.A

    def get_destination(self):
        return self.B


def map_test():
    service = Directions()
    origin = {
        'type': 'Feature',
        'properties': {'name': 'Portland, OR'},
        'geometry': {
            'type': 'Point',
            'coordinates': [-122.7282, 45.5801]}}
    destination = {
        'type': 'Feature',
        'properties': {'name': 'Bend, OR'},
        'geometry': {
            'type': 'Point',
            'coordinates': [-121.3153, 44.0582]}}
    destination1 = {
        'type': 'Feature',
        'properties': {'name': 'Bend, OR'},
        'geometry': {
            'type': 'Point',
            'coordinates': [-122, 45]}}
    response = service.directions([origin, destination1, destination], 'mapbox/walking', alternatives=True,
                                  continue_straight=True, geometries='geojson', language='en', overview='simplified',
                                  steps=False).geojson()
    return response


def check_intersection(directions, avoidCoordinates, radius):
    # Determines whether the avoid location is RADIUS units from the path
    # Directions class contains the current directions that are being tested
    # avoidCoordinates are the coordinates of the point we are avoiding
    ERROR_BUFFER = 3.7/111139 # intersections have a buffer of 3.7 meters
    waypoints = directions.getWaypoints()
    coordinates = directions.getCoordinates()
    for i in range(len(waypoints) - 1):
        tempWaypoints = list()
        for j in range(i):
            tempWaypoints.append(waypoints[j])
        tempWaypoints.append(avoidCoordinates)
        tempDirections = getDirections(tempWaypoints)
        tempCoordinates = tempDirections.getCoordinates()
        iter = 0
        while iter < len(coordinates) and iter < len(tempCoordinates):
            if abs(coordinates[iter][0] - tempCoordinates[iter][0]) < ERROR_BUFFER and \
                    abs(coordinates[iter][1] - tempCoordinates[iter][1]) < ERROR_BUFFER:
                iter += 1
            else:
                # coordinates don't match iter is divergent point
                break
        divergentCoordinate = tempCoordinates[iter]
        divergentDistance = distanceCoordinates(divergentCoordinate, avoidCoordinates)
        distanceToDivergent = distanceCoordinates(tempCoordinates[iter - 1], divergentCoordinate)
        distanceToNextCoordinate = distanceCoordinates(coordinates[iter - 1], coordinates[iter])
        if divergentDistance > radius or distanceToDivergent > distanceToNextCoordinate:
            pass
        else:
            return False
    return True

def totalDirections(coordinateList):
    # total directions
    service = Directions()
    total = []
    for i in range(len(coordinateList)):
        point = {
            'type': 'Feature',
            'properties': {'name': 'Portland, OR'},
            'geometry': {
                'type': 'Point',
                'coordinates': coordinateList[i]}}
        total.append(point)
    response = service.directions(total, 'mapbox/walking').geojson()
    return response


def distanceCoordinates(coordinate0, coordinate1):
    # returns the distance between two coordinates in meters
    coordinateDistance = math.sqrt(coordinate0 ** 2 + coordinate1 ** 2)
    return coordinateDistance * 111139


def getRandomPoint(coordinate0, coordinate1):
    midPoint = []
    midPoint[0] = (coordinate0[0]+coordinate1[0]) / 2
    midPoint[1] = (coordinate0[1] + coordinate1[1]) / 2
    radius = math.sqrt(midPoint ** 2 + coordinate1 ** 2)
    theta = random.random()*2*math.pi
    randomCoordinate = []
    randomCoordinate[0] = midPoint[0] + math.cos(theta) * radius
    randomCoordinate[1] = midPoint[1] + math.sin(theta) * radius
    return randomCoordinate


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(map_test())  # ['features'][0]['geometry']['coordinates']

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
