import requests
from bs4 import BeautifulSoup
import pandas

def scrape_state_trails(state):
    #Login to  base site
    all_trails_site = "https://www.alltrails.com"
    state_search = all_trails_site + "/" + "us" + "/" + state
    r = requests.get(base_url)
    c = r.content
