import requests
import networkx as nx
import matplotlib.pyplot as plt
API = "https://en.wikibooks.org/w/api.php"
params = {
    "action": "query",
    "list": "categorymembers",
    "cmtitle": "Category:Ingredients",
    "cmlimit": 500,
    "cmtype": "page",   # use "page|subcat" to include subcategories
    "format": "json",
}
headers = {"User-Agent": "ingredient-scraper/1.0 (your@email.com)"}

ingredients = []
while True:
    data = requests.get(API, params=params, headers=headers, timeout=30).json()
    ingredients += [m["title"].removeprefix("Cookbook:")
                    for m in data["query"]["categorymembers"]]
    if "continue" not in data:
        break
    params.update(data["continue"])



import requests
from urllib.parse import unquote, urlparse
from bs4 import BeautifulSoup

BASE = "https://en.wikibooks.org"
headers = {"User-Agent": "ingredient-scraper/1.0 (your@email.com)"}

def normalize(title):
    """'Cookbook:Olive_Oil#Uses' -> 'olive oil'"""
    title = unquote(title).split("#")[0]
    title = title.removeprefix("Cookbook:").replace("_", " ")
    return title.strip().lower()

# `ingredients` is the list from the previous step
ingredient_set = {normalize(i) for i in ingredients}

def recipe_ingredients(recipe_url):
    soup = BeautifulSoup(requests.get(recipe_url, headers=headers, timeout=30).text,
                         "html.parser")
    found = []
    for a in soup.select('a[href^="/wiki/Cookbook:"]'):
        name = normalize(urlparse(a["href"]).path.removeprefix("/wiki/"))
        if name in ingredient_set:
            found.append(name)
    return list(dict.fromkeys(found))  # dedupe, keep order

ingredients = recipe_ingredients(f"{BASE}/wiki/Cookbook:Bánh_Mì")
G = nx.graph(1)
mapping = {i:ingredients for i,ingredients in enumerate(ingredients)}
#now mapping looks like {0:'a', 1:'b', ...}
H=nx.relabel_nodes(G,mapping)
nx.draw(H, with_labels=True)
plt.show()