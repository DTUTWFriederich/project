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




import csv, json, time, re
from collections import defaultdict, Counter
from urllib.parse import unquote
import requests

API = "https://en.wikibooks.org/w/api.php"
S = requests.Session()
S.headers["User-Agent"] = "ingredient-scraper/1.0 (your@email.com)"

def api(params):
    params = {**params, "format": "json", "formatversion": 2, "maxlag": 5}
    while True:
        r = S.get(API, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("error", {}).get("code") == "maxlag":
            time.sleep(5)
            continue
        time.sleep(0.3)  # be polite
        return data

def category_members(cat, cmtype):
    params = {"action": "query", "list": "categorymembers", "cmtitle": cat,
              "cmlimit": 500, "cmtype": cmtype}
    out = []
    while True:
        data = api(params)
        out += [m["title"] for m in data["query"]["categorymembers"]]
        if "continue" not in data:
            return out
        params.update(data["continue"])

def all_recipes(root="Category:German_recipes"):
    """Walk the category tree, collecting every Cookbook: page."""
    seen_cats, recipes, stack = set(), set(), [root]
    while stack:
        cat = stack.pop()
        if cat in seen_cats:
            continue
        seen_cats.add(cat)
        recipes.update(t for t in category_members(cat, "page") if t.startswith("Cookbook:"))
        stack += category_members(cat, "subcat")
    return sorted(recipes)

def links_for(titles):
    """Outgoing Cookbook: links for up to 50 pages at once."""
    result = defaultdict(set)
    params = {"action": "query", "prop": "links", "titles": "|".join(titles),
              "pllimit": "max"}
    while True:
        data = api(params)
        for page in data["query"]["pages"]:
            for link in page.get("links", []):
                if link["title"].startswith("Cookbook:"):
                    result[page["title"]].add(link["title"])
                    print(result)
        if "continue" not in data:
            return result
        params.update(data["continue"])

def normalize(title):
    title = unquote(title).split("#")[0]
    return title.removeprefix("Cookbook:").replace("_", " ").strip().lower()

# ---- main ----
# `ingredients` = list from your earlier Category:Ingredients step
ingredient_set = {normalize(i) for i in ingredients}

recipes = all_recipes()
print(f"{len(recipes)} recipe pages")

recipe_ingredients = {}
for i in range(0, len(recipes), 50):
    batch = recipes[i:i + 50]
    for recipe, targets in links_for(batch).items():
        found = sorted({normalize(t) for t in targets} & ingredient_set)
        recipe_ingredients[recipe] = found
    print(f"{min(i + 50, len(recipes))}/{len(recipes)}")

# ---- save ----
with open("German_recipe_ingredients.json", "w", encoding="utf-8") as f:
    json.dump(recipe_ingredients, f, ensure_ascii=False, indent=2)

with open("German_recipe_ingredients.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["recipe", "ingredient"])
    for recipe, ings in recipe_ingredients.items():
        for ing in ings:
            w.writerow([recipe.removeprefix("Cookbook:"), ing])

print(Counter(i for v in recipe_ingredients.values() for i in v).most_common(20))