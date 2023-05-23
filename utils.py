import requests
from bs4 import BeautifulSoup

def get_current_week_type():
    url = 'http://orar.ase.md/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.select_one("table").text.strip().split()[-1][:-1]

