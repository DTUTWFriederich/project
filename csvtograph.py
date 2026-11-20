import csv
import glob

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D

MIN_RECIPES = 10      # skip cuisines with fewer recipes than this
MAX_CUISINES = 12     # keep the biggest N so recipe colours stay distinguishable
N_LABELS = 40         # only label the N best-connected nodes

# ---------- find cuisine files ----------
cuisines = {}   # name -> (path, n_recipes)
for path in glob.glob("*_recipe_ingredients.csv"):
    if path.lower().startswith("european"):
        continue
    name = path[: -len("_recipe_ingredients.csv")].lower()   # German_ and german_ -> same cuisine
    with open(path, encoding="utf-8") as f:
        n = len({row["recipe"] for row in csv.DictReader(f)})
    if n >= MIN_RECIPES and (name not in cuisines or n > cuisines[name][1]):
        cuisines[name] = (path, n)

top = sorted(cuisines.items(), key=lambda kv: kv[1][1], reverse=True)[:MAX_CUISINES]
print([(name, n) for name, (_, n) in top])

# Recipe colours: warm/green/purple/brown/pink tab20 shades, no blues or greys,
# so they can't be confused with the blue ingredient scale
palette = [plt.cm.tab20(i) for i in range(2, 14)]
cuisine_colour = {name: palette[i % len(palette)] for i, (name, _) in enumerate(top)}

# ---------- build graph ----------
G = nx.Graph()
labels = {}

def load(path, cuisine):
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # prefixes stop a recipe and an ingredient with the same name from merging
            r, i = "r:" + row["recipe"], "i:" + row["ingredient"]
            if r not in G:
                G.add_node(r, kind="recipe", colour=to_rgba(cuisine_colour[cuisine]))
                labels[r] = row["recipe"]
            if i not in G:
                G.add_node(i, kind="ingredient", cuisines=set())
                labels[i] = row["ingredient"]
            G.nodes[i]["cuisines"].add(cuisine)
            G.add_edge(i, r)

for name, (path, _) in top:
    load(path, name)

# ---------- ingredient colour = number of cuisines, binned ----------
BINS = [(1, 1, 0.20, "1 cuisine"),
        (2, 3, 0.45, "2-3 cuisines"),
        (4, 6, 0.70, "4-6 cuisines"),
        (7, 10**9, 0.95, "7+ cuisines")]

def ingredient_colour(count):
    for lo, hi, shade, _ in BINS:
        if lo <= count <= hi:
            return to_rgba(plt.cm.Blues(shade))

for n, data in G.nodes(data=True):
    if data["kind"] == "ingredient":
        data["colour"] = ingredient_colour(len(data["cuisines"]))

# ---------- centrality (sampled, exact is very slow on big graphs) ----------
bs = nx.betweenness_centrality(G, k=min(500, len(G)), seed=1)
for n, score in sorted(bs.items(), key=lambda kv: kv[1], reverse=True)[:15]:
    print(f"{score:.4f}  {labels[n]}")

# ---------- draw ----------
plt.figure(figsize=(16, 12))
pos = nx.spring_layout(G, k=0.15, seed=1)

colour_map = [G.nodes[n]["colour"] for n in G.nodes]
sizes = [40 if G.nodes[n]["kind"] == "recipe" else 40 + 8 * G.degree(n) for n in G.nodes]

nx.draw_networkx_edges(G, pos, edge_color="#cccccc", width=0.5)
nx.draw_networkx_nodes(G, pos, node_color=colour_map, node_size=sizes,
                       edgecolors="black", linewidths=0.5)

top_nodes = sorted(G.nodes, key=G.degree, reverse=True)[:N_LABELS]
nx.draw_networkx_labels(G, pos, labels={n: labels[n] for n in top_nodes}, font_size=8)

legend = [Line2D([0], [0], marker="o", color="w", markerfacecolor=cuisine_colour[name],
                 markeredgecolor="black", markersize=10, label=f"Recipe: {name}")
          for name, _ in top]
legend += [Line2D([0], [0], marker="o", color="w",
                  markerfacecolor=plt.cm.Blues(shade), markeredgecolor="black",
                  markersize=10, label=f"Ingredient: {text}")
           for lo, _, shade, text in BINS if lo <= len(top)]
plt.legend(handles=legend, loc="upper left")
plt.axis("off")
plt.show()