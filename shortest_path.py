import neo4j
from neo4j import GraphDatabase
from flask import Flask
from flask import jsonify
from flask_cors import CORS
import time
app = Flask(__name__)
CORS(app)

uri = "neo4j+ssc://347bdfd6.production-orch-0002.neo4j.io:7687"
username = "neo4j"
password = "6uNa34OrH1v3_T08NF-bX7DMaqc55YE--ZUQCHI5zCc"
driver = GraphDatabase.driver(uri, auth=(username, password))
session = driver.session()

def nearest_node(location):
  lat = location[0]
  longit = location[1]
  query = "MATCH (n:LOCATION) RETURN n ORDER BY (n.x - "+str(lat)+") * (n.x - "+str(lat)+")" + " + (n.y - " + str(longit)+")*(n.y - "+str(longit)+")  ASC LIMIT 1"
  closest = session.run(query)
  c_dict = dict()
  for c in closest:
    c_dict = dict(c["n"])
  print("Nearest Node: ", (c_dict["x"], c_dict["y"]))
  return (c_dict["x"], c_dict["y"])

def nearest_intersection(location):
  lat = location[0]
  longit = location[1]
  query = "MATCH (n:LOCATION) WHERE n.INTERSECTION = TRUE RETURN n ORDER BY (n.x - "+str(lat)+") * (n.x - "+str(lat)+")" + " + (n.y - " + str(longit)+")*(n.y - "+str(longit)+")  ASC LIMIT 1"
  closest = session.run(query)
  c_dict = dict()
  for c in closest:
    c_dict = dict(c[0])
  return (c_dict["x"], c_dict["y"])

def route(closestart, closeend):
  print("CLOSESTART: ", closestart, ", CLOSEEND: ", closeend)
  prev = dict()
  dist = dict()
  unex_dist = dict()
  unex = set()
  for v in session.run("MATCH (n:LOCATION) RETURN n"):
      try:
        vert = (dict(v["n"])["x"], dict(v["n"])["y"])
      except:
        print(dict(v["n"]))
      dist[vert] = float("INF")
      prev[vert] = None
  print("Completed initialization in Djikstra's.")
  #print("unex: ", unex)
  dist[closestart] = 0
  unex_dist = dict()
  curr_vert = closestart
  unex.add(curr_vert)
  unex_dist[closestart] = 0
  while closeend != curr_vert:
    curr_vert = min(unex_dist, key = unex_dist.get)
    unex.remove(curr_vert)
    unex_dist.pop(curr_vert)
    for w in session.run("MATCH (n:LOCATION)-[r:ROAD]->(m:LOCATION) WHERE n.x = " + str(curr_vert[0]) + " AND n.y = " + str(curr_vert[1]) + " RETURN m, r"):
      wv = (dict(w['m'])["x"], dict(w['m'])["y"])
      if dist[curr_vert] + dict(w["r"])["length"] < dist[wv]:
          dist[wv] = dist[curr_vert] + dict(w["r"])["safety_score"]
          prev[wv] = curr_vert
      unex.add(wv)
      unex_dist[wv] = dist[wv]
  x = closeend
  path = [list(x)]
  while x != closestart:
    x = prev[x]
    path.append(list(x))
  print("PATH CREATED")
  print("PATH: ",path[::-1])
  return jsonify({"Path":path[::-1]})

@app.route("/test")
def test():
  return "API WORKS."

#def path_finder(slat: float, slong: float, elat: float, elong: float):

# @app.route("/route/<string:slong>/<string:slat>/<string:elong>/<string:elat>", methods = ["GET"])
def path_finder(slong: str, slat: str, elong: str, elat: str):
  slat = float(slat)
  slong = float(slong)
  elat = float(elat)
  elong = float(elong)
  latstart = slat
  longstart = slong
  latend = elat
  longend = elong
  print("SLAT: ", slat, ", SLONG: ", slong, ", ELAT: ", elat, ", ELONG: ", elong)
  query = "MATCH (n:LOCATION) RETURN n ORDER BY (n.x - "+str(latstart)+") * (n.x - "+str(latstart)+")" + " + (n.y - " + str(longstart)+")*(n.y - "+str(longstart)+")  ASC LIMIT 1"
  closestart = (session.run(query))
  for r in closestart:
    print(r)
    start_dict = dict(r["n"])
    print(start_dict)
  closestart = (start_dict["x"], start_dict["y"])
  query = "MATCH (n:LOCATION) RETURN n ORDER BY (n.x - "+str(latend)+") * (n.x - "+str(latend)+")" + " + (n.y - " + str(longend)+")*(n.y - "+str(longend)+")  ASC LIMIT 1"
  closeend = (session.run(query))
  for r in closeend:
    end_dict = dict(r["n"])
  closeend = (end_dict["x"], end_dict["y"])
  print("CLOSESTART: ", closestart, " , CLOSEEND: ", closeend)
  return route(nearest_node(closestart), nearest_node(closeend))

@app.route("/route/<string:slong>/<string:slat>/<string:elong>/<string:elat>", methods = ["GET"])
def path_finder_simple(slong: str, slat: str, elong: str, elat: str):
  start = [float(slong),float(slat)]
  end = [float(elong), float(elat)]
  start = nearest_node(start)
  end = nearest_node(end)
  slong = str(start[0])
  slat = str(start[1])
  elong = str(end[0])
  elat = str(end[1])
  max_nodes=15
  while True:
    seconds = time.time()
    print(max_nodes)
    # Used code from https://liberation-data.com/saxeburg-series/2018/11/28/rock-n-roll-traffic-routing.html
    query = "MATCH paths = (a:LOCATION {x:"+str(slong)+"})-[:ROAD*1.."+str(max_nodes)+"]-(b:LOCATION {x:"+str(elong)+"}) WITH paths, relationships(paths) AS rels UNWIND rels AS rel WITH [metro IN nodes(paths) | metro.x] AS long, [metro IN nodes(paths) | metro.y] AS lat, [metro IN nodes(paths) | metro.INTERSECTION] AS intersection, sum(rel.safety_score) AS travelTime RETURN long, lat, intersection ORDER BY travelTime Limit 1"
    result = (session.run(query))  
    path = list()
    final_path = list()
    for result in result:
      for long in result[0]:
        path.append([long])
      for i, lat in enumerate(result[1]):
        path[i].append(lat)
      # for i, intersection in enumerate(result[2]):
      #   if intersection == True:
      #     final_path.append(path[i])
    delta_time = time.time()-seconds
    print(delta_time)
    print(path)
    if delta_time>2 and path!=[]:
      return jsonify(path)
    if path==[]:
      max_nodes += 4
    else:
      max_nodes+=2

if __name__=="__main__":
    app.run()