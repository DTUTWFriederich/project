import csv
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# (csv file, cuisine name, recipe colour)
CUISINES = [
    ("recipe_ingredients.csv",        "main",   "#E69F00"),  # orange
    ("danish_recipe_ingredients.csv", "danish", "#009E73"),  # green
    ("German_recipe_ingredients.csv", "german", "#CC79A7"),  # pink
]

G = nx.Graph()

def load(path, source, recipe_colour):
    with open(path, encoding="utf-8") as csvfile:
        for row in csv.DictReader(csvfile):
            recipe, ingredient = row["recipe"], row["ingredient"]

            if recipe not in G:
                G.add_node(recipe, kind="recipe", colour=recipe_colour)
            if ingredient not in G:
                G.add_node(ingredient, kind="ingredient", sources=set())

            G.nodes[ingredient]["sources"].add(source)
            G.add_edge(ingredient, recipe)

for path, source, colour in CUISINES:
    load(path, source, colour)

# Ingredient colour = number of cuisines it appears in
n_cuisines = len(CUISINES)

def ingredient_colour(count):
    # 1 cuisine -> light blue, all cuisines -> dark blue
    return plt.cm.Blues(0.25 + 0.75 * (count - 1) / max(n_cuisines - 1, 1))

for n, data in G.nodes(data=True):
    if data["kind"] == "ingredient":
        data["colour"] = ingredient_colour(len(data["sources"]))

colour_map = [G.nodes[n]["colour"] for n in G.nodes]

# Top ingredients/recipes by betweenness (sorted by score, not by name)
bs = nx.betweenness_centrality(G)
for name, score in sorted(bs.items(), key=lambda kv: kv[1], reverse=True)[:15]:
    print(f"{score:.4f}  {name}")

# Draw
plt.figure(figsize=(16, 12))
pos = nx.spring_layout(G, k=0.3, seed=1)
nx.draw(G, pos, with_labels=True, node_color=colour_map,
        edgecolors="black", node_size=300, font_size=7, edge_color="#bbbbbb")

legend = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
                 markeredgecolor="black", markersize=10, label=f"Recipe: {s}")
          for _, s, c in CUISINES]
legend += [Line2D([0], [0], marker="o", color="w",
                  markerfacecolor=ingredient_colour(k), markeredgecolor="black",
                  markersize=10,
                  label=f"Ingredient: {k} cuisine{'s' if k > 1 else ''}")
           for k in range(1, n_cuisines + 1)]
plt.legend(handles=legend, loc="upper left")
plt.show()