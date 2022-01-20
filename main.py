import math
import mapbox
import random
import time
from mapbox import Directions
import requests
import json



# help(mapbox.Directions)

class MapDirections:
    def __init__(self, waypoints):
        service = Directions()
        total = []
        for i in range(len(waypoints)):
            point = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': waypoints[i]}}
            total.append(point)
        response = service.directions(total, 'mapbox/walking').geojson()

        self.response = response
        self.waypoints = waypoints
        self.distance = self.response['features'][0]['properties']['distance']
        self.coordinates = self.response['features'][0]['geometry']['coordinates'].copy()
        self.duration = self.response['features'][0]['properties']['duration']

    def get_waypoints(self):
        return self.waypoints

    def get_response(self):
        return self.response

    def get_coordinates(self):
        # if self.response is not None:
        #     for i in self.response["features"]:
        #         self.coordinates = i["geometry"]["coordinates"]
        return self.response['features'][0]['geometry']['coordinates']

    def get_distance(self):
        # if self.response is not None:
        #     for i in self.response["features"]:
        #         self.distance = i["properties"]["distance"]
        return self.distance

    def get_duration(self):
        # if self.response is not None:
        #     for i in self.response["features"]:
        #         self.duration = i["properties"]["duration"]
        return self.duration

    def get_origin(self):
        return self.waypoints[0]

    def get_destination(self):
        return self.waypoints[len(self.waypoints) - 1]

    def __print__(self):
        print(self.waypoints)


def map_test():
    service = Directions()
    origin = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [-122.7282, 45.5801]}}
    destination = {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [-121.3153, 44.0582]}}
    destination1 = {
        'type': 'Feature',
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
    ERROR_BUFFER = 3.7 / 111139  # intersections have a buffer of 3.7 meters
    waypoints = directions.getWaypoints()
    coordinates = directions.getCoordinates()
    for i in range(len(waypoints) - 1):
        tempWaypoints = list()
        for j in range(i):
            tempWaypoints.append(waypoints[j])
        tempWaypoints.append(avoidCoordinates)
        tempDirections = Directions(tempWaypoints)
        tempCoordinates = tempDirections.get_coordinates()
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


def distanceCoordinates(coordinate0, coordinate1):
    # returns the distance between two coordinates in meters
    coordinateDistance = math.sqrt(coordinate0[0] - coordinate1[0] ** 2 + (coordinate1[1] - coordinate0[1]) ** 2)
    return coordinateDistance * 111139


def getRandomPoint(coordinate0, coordinate1):
    # returns a random point within a circle centered in between coordinates
    EXCESS_SPACE = 1.1  # artificial radius increase (product)
    midPoint = []
    midPoint.append((coordinate0[0] + coordinate1[0]) / 2)
    midPoint.append((coordinate0[1] + coordinate1[1]) / 2)
    # print("midpoint", midPoint)
    # print("coordinate1", coordinate1)
    radius = EXCESS_SPACE * math.sqrt((midPoint[0] - coordinate1[0]) ** 2 + ((midPoint[1] - coordinate1[1]) ** 2))
    # print("radius", radius)
    theta = random.random() * 2 * math.pi
    randomCoordinate = []
    randomCoordinate.append(midPoint[0] + math.cos(theta) * radius)
    randomCoordinate.append(midPoint[1] + math.sin(theta) * radius)
    return randomCoordinate


def generateAlternateDirections(origin, destination, iterations, depth):
    generatedDirections = [MapDirections([origin, destination])]
    for i in range(iterations-1):
        # generatedDirections.append(MapDirections([origin, getRandomPoint(origin, destination), destination]))
        start = origin
        waypoints = [start]
        for n in range(depth):
            randomPoint = getRandomPoint(start, destination)
            waypoints.append(randomPoint)
            tempWaypoints = waypoints.copy()
            tempWaypoints.append(destination)
            generatedDirections.append(MapDirections(tempWaypoints))
            start = randomPoint
    return generatedDirections

def getStreetAddress(coordinates, GMAPS_ACCESS_TOKEN):
    url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(coordinates[1]) + ',' + str(coordinates[0]) + '&result_type=route&key='+GMAPS_ACCESS_TOKEN
    r = requests.get(url)
    # print(r.json())
    r = r.json()
    # print(r['results'])
    return r['results'][0]['address_components'][1]['long_name']



def generateStreetAddressesSet(Directions, MAPBOX_ACCESS_TOKEN, GMAPS_ACCESS_TOKEN):
    url = 'https://api.mapbox.com/directions/v5/mapbox/walking/'
    coordinates = Directions.get_waypoints()
    counter = 0
    for cords in coordinates:
        lat = cords[1]
        long = cords[0]
        url += str(long) + ',' + str(lat)
        if counter != len(coordinates) - 1:
            url += ';'
        counter += 1
    url += '?access_token=' + MAPBOX_ACCESS_TOKEN + '&steps=true'
    addressDict = {}
    # print(url)
    r = requests.get(url)
    # print(r.json())
    r = r.json()
    for i in r['routes'][0]['legs'][0]['steps']:
        if i['duration'] != 0:
            name = ''
            if i['name'] == '':
                name = getStreetAddress([i['intersections'][0]['location'][0],i['intersections'][0]['location'][1]], GMAPS_ACCESS_TOKEN)
                # addressDict[getStreetAddress([i['intersections'][0]['location'][0],i['intersections'][0]['location'][1]], GMAPS_ACCESS_TOKEN)] = i['duration']
            else:
                name = i['name']
            if name in addressDict:
                addressDict[name] += i['duration']
            else:
                addressDict[name] = i['duration']
    return addressDict



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    GMAPS_ACCESS_TOKEN = 'ASK_COEN_FOR_THIS'
    ACCESS_TOKEN = 'pk.eyJ1IjoiY29hc3RlcjQxIiwiYSI6ImNreHpsNmw4ejdteTIydW9jdTM1eWtzbXYifQ.Osaih74nYJNxDEOiz9FK6A'
    # d = MapDirections([[36.98365515596037,-122.00899387223498],[36.97421013125925, -122.0098521790967]])
    d = MapDirections([[-122.04441141616797, 36.96841340396887], [-122.01927448088864, 36.97390676208401]])
    print(generateStreetAddressesSet(d, ACCESS_TOKEN, GMAPS_ACCESS_TOKEN))
    # r = requests.get('https://api.mapbox.com/directions/v5/mapbox/walking/-122.00899387223498,36.98365515596037;-122.0098521790967,36.97421013125925;-122.0011521790967,36.96821013125925?access_token=pk.eyJ1IjoiY29hc3RlcjQxIiwiYSI6ImNreHpsNmw4ejdteTIydW9jdTM1eWtzbXYifQ.Osaih74nYJNxDEOiz9FK6A&steps=true')
    # # print(r.text)
    # r = r.json()
    # for i in r['routes'][0]['legs'][0]['steps']:
    #     print(i['name'])
    # print(r['routes'][0]['legs'][0]['steps'])
    # origin = [-122.04441141616797, 36.96841340396887]
    # destination = [-122.01927448088864, 36.97390676208401]
    # randomizedPosition = getRandomPoint(origin, destination)
    # print(randomizedPosition[0], randomizedPosition[1])
    # print(MapDirections([origin, randomizedPosition, destination]).get_waypoints())
    # DirectionsList = generateAlternateDirections([-122.04441141616797, 36.96841340396887], [-122.01927448088864, 36.97390676208401], 20, 3)
    # for direction in DirectionsList:
    #     print(direction.get_waypoints())
    # print(map_test())
