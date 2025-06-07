import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay, Voronoi, voronoi_plot_2d;
import networkx as nx
import statistics
from enum import auto#je sais meme pas
from itertools import islice #pour une ligne de code lol
import folium
from shapely.geometry import Polygon as ShapelyPolygon, box
from shapely.ops import unary_union
import geopandas as gpd
#ils ne serventpas tous juste la flemme de les trier lol



#changez le chemin
#ouvrir fichier json
with open("C:/Users/but-info\OneDrive - UPEC/Bureau/projets SAE/sae 202/levrai/infos_vlib.json", "r", encoding="utf-8") as file:
    json_data = json.load(file)


stations_dict = {}#dictionnaire des stations 
for station in json_data["data"]["stations"]:#on sort l'info du json
    station_id = station["station_id"]  # id pour unique en clé car noms de stations en doublons
    station_name = station["name"]  # nom 
    coordonnees = (station["lat"], station["lon"]) #coordonnées
                    #nom et coordonnées valeures dans un tuple
    stations_dict[station_id] = (station_name, coordonnees)

# test Affiche du dictionnaire
print(len(stations_dict))
print(stations_dict[213688169])#test d'un elt


place_names = np.array([name for name, _ in stations_dict.values()]) #pareil pour les noms pour leur affichage +tard
points = np.array([coords for _, coords in stations_dict.values()])
print(points)

 # faire une liste de points pour delauney
tri = Delaunay(points) 


donnee = json_data['data']['stations']
final = {}
finale ={}
cap = []
adj = {}

#coordonnées des stations
for i in donnee :
  id = i['station_id']
  final[id] = [i['lat'], i['lon']]

a = final.values()
a = list(a)
points = np.array(a)
tri = Delaunay(points)

#liste d'adjacence

for j in range(len(final)):
  adj[j]=[]
  for i in tri.simplices:
    if j in i :
      for k in i:
        if k not in adj[j] and k != j :
          adj[j].append(k)

#capacite des stations

for i in donnee :
  cap.append(i['capacity'])


# Indice de qualité de la répartition
alpha = 0.5
indice = []
#max capacite
max = cap[0]
for i in cap:
    if i >= max:
        max = i

#calcul indice
for i in range(len(cap)):
  if len(adj[i]) == 6 :
    indice.append(0)
  else :
    I = (alpha*(len(adj[i])-6))/6+((1+alpha)*(max-cap[i]))/max
    indice.append(I)

caca = 0
for i in indice :
  caca += i

quartiles = statistics.quantiles(indice, n=4)
print("Premier quartile (Q1):", quartiles[0])
print("Mediane:", quartiles[1])
print("Troisième quartile (Q3):", quartiles[2])
print("Cest la moyenne ",caca/len(points))
z = (indice)
y = indice[0]
for i in indice:
    if i >= y:
        y = i
print("Cest le max ", y)
print("Cest le min ", min(indice))


import webbrowser

m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)

for i in range(len(points)):
  
  if indice[i] > 0.8333333333333334:
    folium.CircleMarker(
        location=points[i],
        radius=2,
        color="darkgreen",            
        fill=True,
        fill_color="cyan",
        fill_opacity=0.7,
        tooltip=place_names[i]
        ).add_to(m)
  elif indice[i] >0:
    folium.CircleMarker(
        location=points[i],
        radius=2,
        color="lightgreen",
        fill=True,
        fill_color="cyan",
        fill_opacity=0.7,
        tooltip=place_names[i]
        ).add_to(m)
  elif indice[i] <-0.021929824561403508:
    folium.CircleMarker(
        location=points[i],
        radius=2,
        color="#FF6666",
        fill=True,
        fill_color="cyan",
        fill_opacity=0.7,
        tooltip=place_names[i]
        ).add_to(m)
  elif indice[i]==0.000000000000000000000:
    folium.CircleMarker(
        location=points[i],
        radius=2,
        color="yellow",
        fill=True,
        fill_color="cyan",
        fill_opacity=0.7,
        tooltip=place_names[i]
        ).add_to(m)
  else:
    folium.CircleMarker(
        location=points[i],
        radius=2,
        color="#8B0000",
        fill=True,
        fill_color="cyan",
        fill_opacity=0.7,
        tooltip=place_names[i]
        ).add_to(m)

m

m.save("map.html")
webbrowser.open("map.html")