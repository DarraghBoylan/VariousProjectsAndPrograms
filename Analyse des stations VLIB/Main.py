#########ceci est le main

##importation des bibliotheques
import json
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import folium
from scipy.spatial import Voronoi, voronoi_plot_2d
import webbrowser
#importation des fichiers
import TriangulationDelauney
#import Voronoi  
import minimumSpanTree
import indiceRep



with open("C:/Users/but-info\OneDrive - UPEC/Bureau/projets SAE/sae 202/levrai/infos_vlib.json", "r", encoding="utf-8") as file:
    json_data = json.load(file)

#( •̀ ω •́ )✧
#\^o^/
#(〃￣︶￣)人(￣︶￣〃)




stations_dict = {}#dictionnaire des stations 
for station in json_data["data"]["stations"]:#on sort l'info du json
    station_id = station["station_id"]  # id pour unique en clé car noms de stations en doublons
    station_name = station["name"]  # nom 
    coordonnees = (station["lat"], station["lon"]) #coordonnées
                    #nom et coordonnées valeures dans un tuple
    stations_dict[station_id] = (station_name, coordonnees)

place_names = np.array([name for name, _ in stations_dict.values()]) #pareil pour les noms pour leur affichage +tard
points = np.array([coords for _, coords in stations_dict.values()]) # faire une liste de points pour delauney







# test Affiche du dictionnaire
print(len(stations_dict))
print(stations_dict[213688169])#test d'un elt

m = folium.Map(location=[48.8566, 2.3522], zoom_start=12)


triangulation=TriangulationDelauney.Delauney(points, place_names, m)



#indice de repartition a mettre dans sa propre fonction+tard
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
tri = triangulation

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

Voronoi.voronoi(points, m,)



#minimumSpanTree.kruskal(triangulation, points)

#indiceRepartition.indice2Repartition(json_data, triangulation, place_names, m)



