import pandas as pd
import networkx as nx
from itertools import combinations

df = pd.read_csv("data/all_cuisines_combined.csv")

freq = df.groupby("ingredient")["cuisine"].nunique()
common = freq[freq > 0.8 * df["cuisine"].nunique()].index
df = df[~df["ingredient"].isin(common)]
# 
# Set of unique ingredients per cuisine
ingredients = df.groupby("cuisine")["ingredient"].apply(set)

G = nx.Graph()
G.add_nodes_from(ingredients.index)

for a, b in combinations(ingredients.index, 2):
    shared = ingredients[a] & ingredients[b]
    if shared:
        G.add_edge(a, b, weight=len(shared))

MIN_SHARED = 1
H = nx.Graph()
H.add_nodes_from(G.nodes)
H.add_edges_from(
    (u, v, d) for u, v, d in G.edges(data=True) if d["weight"] >= MIN_SHARED
)

weight = len(shared) / len(ingredients[a] | ingredients[b])





nx.write_gexf(H, "output/cuisines.gexf")   # open in Gephi