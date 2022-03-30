import neo4j
import time
from neo4j import GraphDatabase
print('yo')
uri = "neo4j+ssc://347bdfd6.production-orch-0002.neo4j.io:7687"
username = "neo4j"
password = "6uNa34OrH1v3_T08NF-bX7DMaqc55YE--ZUQCHI5zCc"
driver = GraphDatabase.driver(uri, auth=(username, password))
session = driver.session()


def path_finder_simple(slong: str, slat: str, elong: str, elat: str):
  max_nodes = 15
  while True:
    seconds = time.time()
    # print(max_nodes)
    query = "MATCH paths = (a:LOCATION {x:"+str(slong)+"})-[:ROAD*1.."+str(max_nodes)+"]-(b:LOCATION {x:"+str(elong)+"}) WITH paths, relationships(paths) AS rels UNWIND rels AS rel WITH [metro IN nodes(paths) | metro.x] AS long, [metro IN nodes(paths) | metro.y] AS lat, [metro IN nodes(paths) | metro.INTERSECTION] AS intersection, sum(rel.safety_score) AS travelTime RETURN long, lat, intersection ORDER BY travelTime Limit 1"
    result = (session.run(query))  
    path = list()
    final_path = list()
    for result in result:
      for long in result[0]:
        path.append([long])
      for i, lat in enumerate(result[1]):
        path[i].append(lat)
      for i, intersection in enumerate(result[2]):
        if intersection == True:
          final_path.append(path[i])
    delta_time = time.time()-seconds
    # print(delta_time)
    if delta_time>2 and final_path!=[]:
      return final_path
    max_nodes += 2

print('hello')
print(path_finder_simple(-121.8701274150132, 'yo', -121.86845369704432, 'yo'))
print('done')
print(path_finder_simple(-121.8701274150132, 'yo', -121.86845369704432, 'yo'))
print('sup')