import csv, json, re, time
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote
import requests

API = "https://en.wikibooks.org/w/api.php"
S = requests.Session()
S.headers["User-Agent"] = "ingredient-scraper/1.0 (your@email.com)"

EXCLUDE_SUBCATS = set()   # e.g. {"Category:Some non-country category"}
CACHE = Path("link_cache.json")

def api(params):
    params = {**params, "format": "json", "formatversion": 2, "maxlag": 5}
    while True:
        r = S.get(API, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if data.get("error", {}).get("code") == "maxlag":
            time.sleep(5)
            continue
        time.sleep(0.3)
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

def recipes_in(cat):
    """All Cookbook: pages in a category, including its subcategories."""
    seen, pages, stack = set(), set(), [cat]
    while stack:
        c = stack.pop()
        if c in seen:
            continue
        seen.add(c)
        pages.update(t for t in category_members(c, "page") if t.startswith("Cookbook:"))
        stack += [s for s in category_members(c, "subcat") if s not in EXCLUDE_SUBCATS]
    return pages

def normalize(title):
    title = unquote(title).split("#")[0]
    return title.removeprefix("Cookbook:").replace("_", " ").strip().lower()

def build_ingredient_set(root="Category:Ingredients"):
    titles = set(category_members(root, "page"))
    for sub in category_members(root, "subcat"):      # drop this loop if subcats aren't ingredients
        titles |= set(category_members(sub, "page"))
    return {normalize(t) for t in titles}

def links_for(titles):
    """Outgoing Cookbook: links for up to 50 pages per request."""
    result = defaultdict(set)
    params = {"action": "query", "prop": "links", "titles": "|".join(titles),
              "pllimit": "max"}
    while True:
        data = api(params)
        for page in data["query"]["pages"]:
            for link in page.get("links", []):
                if link["title"].startswith("Cookbook:"):
                    result[page["title"]].add(link["title"])
        if "continue" not in data:
            return result
        params.update(data["continue"])
ROOT = "Category:Recipes by origin"
EXCLUDE_SUBCATS = set()      # e.g. {"Category:National Nigerian recipes"}
RENAME = {"Ghanian": "Ghanaian"}   # merge spelling duplicates
DRY_RUN = False               # first run: just print the tree

def label(cat):
    name = cat.removeprefix("Category:").removesuffix(" recipes")
    return RENAME.get(name, name)

regions = [c for c in category_members(ROOT, "subcat") if c not in EXCLUDE_SUBCATS]
if not regions:
    raise SystemExit(f"No subcategories under {ROOT}. Check the category title.")

# (region, cuisine) -> recipe titles
membership = defaultdict(set)
for reg in regions:
    seen, stack = set(), [reg]
    while stack:
        cat = stack.pop()
        if cat in seen:
            continue
        seen.add(cat)
        pages = {t for t in category_members(cat, "page") if t.startswith("Cookbook:")}
        if pages:
            cuisine = label(cat) if cat != reg else label(reg) + " (general)"
            membership[(label(reg), cuisine)] |= pages
        stack += [s for s in category_members(cat, "subcat") if s not in EXCLUDE_SUBCATS]

for (reg, cui), recs in sorted(membership.items()):
    print(f"{reg:22} {cui:32} {len(recs)}")
unique = {r for recs in membership.values() for r in recs}
print(f"\n{len(membership)} cuisines, {len(unique)} unique recipes")
if DRY_RUN:
    raise SystemExit("Dry run done. Set DRY_RUN = False to scrape.")

# ---------- fetch links (cached) ----------
ingredient_set = build_ingredient_set()
cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
todo = sorted(unique - cache.keys())
print(len(todo), "recipe pages to fetch")

for i in range(0, len(todo), 50):
    batch = todo[i:i + 50]
    fetched = links_for(batch)
    for r in batch:
        cache[r] = sorted(fetched.get(r, []))
    CACHE.write_text(json.dumps(cache))
    print(f"{min(i + 50, len(todo))}/{len(todo)}")

# ---------- one big CSV ----------
rows = set()
for (reg, cui), recs in membership.items():
    for r in recs:
        found = {normalize(t) for t in cache.get(r, [])} & ingredient_set
        for ing in found:
            rows.add((reg, cui, r.removeprefix("Cookbook:"), ing))

with open("all_cuisines_combined.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["region", "cuisine", "recipe", "ingredient"])
    w.writerows(sorted(rows))
print(len(rows), "rows written to all_cuisines_combined.csv")
