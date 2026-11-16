from bs4 import BeautifulSoup
import re


page = open("C:\\Users\\tijnf\\Documents\\DTU\\02805_Social_Graphs\\49fb73ea07d2a1380c15197db5589934937457ed\\recipes\\recipe_00_000.html","rb")
soup = BeautifulSoup(page, 'html.parser')

links = [a["href"] for a in soup.find_all("a", href=re.compile(r"^/wiki/Cookbook:"))]
print(links)