import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
import networkx as nx
import statistics
import folium        

def kruskal(tri, points, m):
    #Ce code (l5-l10) vient de stack overflow, il crée un objet G (graphe pondéré) pour la fonction minimum_spanning_tree
    G = nx.Graph() #on utilise une fonction de la bibliothèque NetworkX
    for simplex in tri.simplices:
        for i in range(3):
            p1, p2 = tuple(points[simplex[i]]), tuple(points[simplex[(i+1) % 3]])#calcul des triangles les +petits
            weight = np.linalg.norm(np.array(p1) - np.array(p2))#calcul du poids (la distance entre les deux points) de chaque segment
            G.add_edge(p1, p2, weight=weight)#
    #G est un graphe pondéré

    # Calcul de l'arbre couvrant minimal avec Kruskal
    mst = nx.minimum_spanning_tree(G, algorithm="kruskal") #fonction kruskal de NetworkX
    #entrée et sortie = graphe pondérée 

    # Affichage de l'arbre couvrant minimal
    plt.triplot(points[:, 0], points[:, 1], tri.simplices, linestyle="dashed", color="gray", alpha=0.5)
    plt.scatter(points[:, 0], points[:, 1], color='red')
    for u, v in mst.edges():
        plt.plot([u[0], v[0]], [u[1], v[1]], 'b-')
    

    for u, v in mst.edges():
        line = folium.PolyLine(locations=[(u[0], u[1]), (v[0], v[1])], color='purple', weight=5, opacity=0.8)
        line.add_to(m)
    
    return G, m