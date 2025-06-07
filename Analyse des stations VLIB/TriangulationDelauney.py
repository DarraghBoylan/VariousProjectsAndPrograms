import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import networkx as nx
import statistics
import folium



def Delauney(points, place_names, m):
    triangulation = Delaunay(points) #triangulation = graphe, fonction Delauney() de SciPy
    #affichage du graphe de Triangulation
    plt.triplot(points[:, 0], points[:, 1], triangulation.simplices, color="gray", alpha=0.5)
    plt.scatter(points[:, 0], points[:, 1], color='red')

    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Triangulation de Delauney")
    plt.show()
    for i in range(len(points)):
        folium.CircleMarker(
        location=points[i],
        radius=2,
        color="green",            
        fill=True,
        fill_color="cyan",
        fill_opacity=0.7,
        tooltip=place_names[i]
        ).add_to(m)

    return triangulation, m

