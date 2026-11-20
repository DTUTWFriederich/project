with the following two rules for the graph "CuisinesRawCounts": 

- every cuisine is a node 
- two cuisines have an undirected edge between them if they share at least X amount of ingredients, currently, X=1. The edge weight is the raw count of the number of ingredients shared between the cuisines.

Already some structure can be seen. Firstly, due to the obvious disproportionate ammount of american recipes contributed by american editors on an american website as opposed to editors from other cultures, the cuisines "Southern U.S.", "United States", "Texas" and "Tex-Mex" concistently rank amongst the most 'similair' to every other cuisine when comparing with raw numbers. 
If you disregard those however, the most obvious neighbours can already be found. I.E. Afghan cuisine is clostest to pakistani cuisine, Dutch to English/German, Greek to Turkish, French to Italian etc etc. 
These "nearest neighbours" arent very strict however. Thus, at this point, it is more logical to look at it on a bigger scale (i.e. continents. African cuisines rank high among african cuisines, european among european, etc).
Also interesting, if you for example look at the follwing line of countries: belgium, france, Spain and Portugal, you get the following edge weights between them: 

Belgium / France = 23
Belgium / Spain = 14
France  / Spain = 46
Spain   / Portugal = 23
Belgium / Portugal = 12 
France  / Portugal = 27 

Thus, while we cannot say when two countries do border for certain, we can say when they do not. This is still derived only from used ingredients however, so keep in mind that borders in these conclusions should rather be replaced by "cuisine similarity". 