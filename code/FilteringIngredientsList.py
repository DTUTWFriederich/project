import numpy as np
import pandas as pd
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pprint

df = pd.read_csv("data/all_cuisines_combined.csv", usecols=["region", "cuisine", "recipe", "ingredient"])
df["ingredient"] = df["ingredient"].str.strip().str.lower()
df = df.dropna(subset=["cuisine", "ingredient"])

# One list of ingredients per cuisine. Duplicates are kept on purpose,
# so TF reflects how often the cuisine uses the ingredient.
docs = df.groupby("cuisine")["ingredient"].apply(list)

def tfidf(doc_lists):
    vec = TfidfVectorizer(analyzer=lambda x: x, sublinear_tf=True)
    X = vec.fit_transform(doc_lists)
    return vec, X

# Pass 1: fit on everything to get document frequencies
vec, X = tfidf(docs)
terms = np.array(vec.get_feature_names_out())
n_cuisines = X.shape[0]
n_docs_with_term = np.asarray((X > 0).sum(axis=0)).ravel()
doc_frac = n_docs_with_term / n_cuisines

# Prune: too common (salt, oil...) or too rare (only one cuisine, can never form an edge)
MAX_DF = 0.65
MIN_DOCS = 2
keep_mask = (doc_frac <= MAX_DF) & (n_docs_with_term >= MIN_DOCS)

kept = terms[keep_mask]
removed = terms[~keep_mask]

# Record why each term was removed
report = pd.DataFrame({
    "ingredient": terms,
    "n_cuisines": n_docs_with_term,
    "doc_frac": doc_frac,
    "idf": vec.idf_,
    "status": np.where(keep_mask, "kept", "removed"),
    "reason": np.select(
        [doc_frac > MAX_DF, n_docs_with_term < MIN_DOCS],
        ["too common", "too rare"],
        default="",
    ),
}).sort_values("n_cuisines", ascending=False)

report.to_csv("ingredient_filter_report.csv", index=False)
print(f"kept {len(kept)}, removed {len(removed)}")
print("Removed (too common):", report.query("reason == 'too common'")["ingredient"].tolist())
print("Removed (too rare):  ", report.query("reason == 'too rare'")["ingredient"].tolist()[:30], "...")

# Pass 2: refit on the kept vocabulary so IDF is recomputed without the pruned terms
kept_set = set(kept)
docs_kept = docs.apply(lambda lst: [t for t in lst if t in kept_set])
vec2, X2 = tfidf(docs_kept)

sim = cosine_similarity(X2)
np.fill_diagonal(sim, 0)

MIN_SIM = 0.3
G = nx.Graph()
G.add_nodes_from(docs_kept.index)
idx = docs_kept.index
for i in range(len(idx)):
    for j in range(i + 1, len(idx)):
        if sim[i, j] >= MIN_SIM:
            G.add_edge(idx[i], idx[j], weight=float(sim[i, j]))


result = nx.community.louvain_communities(G, weight="weight")
pprint.pprint(result)

nx.write_gexf(G, "output/FiltredIngredientcuisines65.gexf")   # open in Gephi