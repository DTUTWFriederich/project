There are a lot of ingredients that are used by only one cuisine. "Wasabi" by the Japanese, "Frog" by the French, and "thai chilli paste" well, I'll let you figure out for yourself. The full list can be found under 'output/ingredient_filter_report'.
Please note however, this is according to their usage in the WikiMedia:Cookbook. Ingredients like "truffles" are also removed from our list, even though in real life they are indeed used in multiple cuisines. For our purposes however, this distinction does not exist (Although they may be usefull in defining the most unique cuisine). 
Next, we would also like to remove ingredients that are too common, they don't tell us much either. Using TF-IDF, these were found to be 'salt' and 'onion'.

With the above applied, we can immediately notice a few things:
- The american clique has been dethroned. They are no longer the most similair to all other cuisines.
- On the WikiMedia:Cookbook, the recipes can be organised by origin. It is not very strict what origin entails however. This could be a country, ethnic group, region or even continent. If you sort the edges based on weight, the indigenous enthic groups almost completely make up the top 10.  
- Bordering countries consitently rank higher as neighbours. As an example, for austria the top 10 looks as follows:

Austrian	Hungarian       0.5817137360572815  
Austrian	German		    0.5514074563980103  
Austrian	English 	    0.535006046295166   
Austrian	Slovenian       0.48203426599502563    
Austrian	Scottish        0.43665459752082825  
Austrian	French          0.42694252729415894  
Austrian	Canadian        0.42688271403312683  
Austrian	Cornish		    0.42592546343803406  
Austrian	United States	0.42012229561805725  
Austrian	Czech			0.4145570695400238   


Out of the 8 countries Austria borders, 5 are found in the top 10, with Italy on 12th place. The remaining two, Switzerland and Slovakia, have no edges to Austria. Slovakia has no recipes at all on the cookbook (so the node doesn't even exist), and Switzerland's page only has three recipes which mostly use characteristic ingredients, thus making it hard to find relations as well (Alstian, a region on on the borders of Switzerland, Germany, and France, however, ranks 13th).