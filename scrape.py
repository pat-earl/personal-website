import requests
from bs4 import BeautifulSoup as bs

url = "https://www.youtube.com/feed/trending"

page = requests.get(url)
soup = bs(page.content, 'html.parser')

links = soup.find_all('a', class_="yt-uix-tile-link", href=True)

for x in range(10):
    print(str(x+1) + ") " + links[x].text)
    print("https://www.youtube.com" + links[x]['href'] + "\n")

