import csv
from collections import defaultdict, Counter
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt

CUISINES = [
    ("recipe_ingredients.csv",        "main",   "#E69F00"),
    ("danish_recipe_ingredients.csv", "danish", "#009E73"),
    ("German_recipe_ingredients.csv", "german", "#CC79A7"),
]

MIN_WEIGHT = 2        # drop pairs that co-occur in fewer recipes than this
MAX_LINEWIDTH = 8

def cooccurrence_graph(path):
    # recipe -> set of ingredients
    recipes = defaultdict(set)
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            recipes[row["recipe"]].add(row["ingredient"])

    pair_counts = Counter()
    for ingredients in recipes.values():
        for a, b in combinations(sorted(ingredients), 2):
            pair_counts[(a, b)] += 1

    G = nx.Graph()
    # Count how many recipes use each ingredient (for node size)
    uses = Counter(i for ings in recipes.values() for i in ings)
    for ingredient, n in uses.items():
        G.add_node(ingredient, uses=n)
    for (a, b), w in pair_counts.items():
        if w >= MIN_WEIGHT:
            G.add_edge(a, b, weight=w)

    # Remove ingredients left with no edges after thresholding
    G.remove_nodes_from(list(nx.isolates(G)))
    return G

graphs = {name: (cooccurrence_graph(path), colour)
          for path, name, colour in CUISINES}

fig, axes = plt.subplots(1, len(graphs), figsize=(8 * len(graphs), 8))

for ax, (name, (G, colour)) in zip(axes, graphs.items()):
    pos = nx.spring_layout(G, weight="weight", k=0.5, seed=1)

    weights = [d["weight"] for _, _, d in G.edges(data=True)]
    max_w = max(weights, default=1)
    widths = [0.5 + MAX_LINEWIDTH * w / max_w for w in weights]

    sizes = [100 + 40 * G.nodes[n]["uses"] for n in G.nodes]

    nx.draw_networkx_edges(G, pos, ax=ax, width=widths, edge_color="#888888", alpha=0.6)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=sizes,
                           node_color=colour, edgecolors="black")
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=8)

    ax.set_title(f"{name}: {G.number_of_nodes()} ingredients, "
                 f"{G.number_of_edges()} pairs")
    ax.axis("off")

plt.tight_layout()
plt.show()