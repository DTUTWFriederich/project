import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D

K = 3    # nearest neighbours kept per cuisine
M = 5    # "pseudo-recipes": a cuisine with M recipes gets half weight

df = pd.read_csv("all_cuisines_combined.csv").drop_duplicates()

# a cuisine filed under two regions gets its most common one
region = df.groupby("cuisine")["region"].agg(lambda s: s.mode().iloc[0])
n = df.groupby("cuisine")["recipe"].nunique()

# global rate: share of ALL recipes that use each ingredient
g = (df.drop_duplicates(["recipe", "ingredient"]).groupby("ingredient")["recipe"].nunique()
     / df["recipe"].nunique())

# cuisine x ingredient: share of the cuisine's recipes using the ingredient
counts = df.groupby(["cuisine", "ingredient"]).size().unstack(fill_value=0)
share = counts.div(n[counts.index], axis=0)

# only look at OVER-use relative to the global rate; staples (salt, oil) cancel out,
# and a tiny cuisine that happens not to use an ingredient isn't penalised
over = (share - g[share.columns]).clip(lower=0)

unit = over.div(np.linalg.norm(over, axis=1), axis=0).fillna(0)
cos = unit @ unit.T

# discount similarities involving cuisines with little evidence
conf = n[cos.index] / (n[cos.index] + M)
strength = cos * np.outer(conf, conf)

# keep each cuisine's K strongest links
G = nx.Graph()
for c in strength.index:
    G.add_node(c, n=n[c], region=region[c], conf=conf[c])
for a in strength.index:
    for b in strength[a].drop(a).nlargest(K).index:
        if strength.loc[a, b] > 0:
            G.add_edge(a, b, weight=strength.loc[a, b])

# ---------- draw ----------
regions = sorted(region.unique())
rcol = {r: plt.cm.tab20(i % 20) for i, r in enumerate(regions)}

pos = nx.spring_layout(G, weight="weight", k=0.6, seed=1)
fig, ax = plt.subplots(figsize=(16, 12))

w = np.array([G[u][v]["weight"] for u, v in G.edges])
nx.draw_networkx_edges(G, pos, ax=ax, width=0.5 + 6 * w / w.max(),
                       edge_color="#777777", alpha=0.5)

nodes = list(G.nodes)
nx.draw_networkx_nodes(
    G, pos, ax=ax, nodelist=nodes, edgecolors="black", linewidths=0.8,
    node_size=[80 + 40 * np.sqrt(G.nodes[c]["n"]) for c in nodes],
    node_color=[to_rgba(rcol[G.nodes[c]["region"]], alpha=0.3 + 0.7 * G.nodes[c]["conf"])
                for c in nodes],
)
nx.draw_networkx_labels(G, pos, ax=ax, font_size=8,
                        labels={c: f"{c} ({G.nodes[c]['n']})" for c in nodes})

ax.legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor=rcol[r],
                          markeredgecolor="black", markersize=10, label=r) for r in regions],
          loc="upper left", title="Region (faded = few recipes)")
ax.axis("off")
plt.show()