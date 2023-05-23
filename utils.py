import requests
from bs4 import BeautifulSoup
import random


def get_current_week_type():
    url = 'http://orar.ase.md/'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.select_one("table").text.strip().split()[-1][:-1]


def get_weather_comment():
    comments = [
        "Educația este cheia către viitorul tău. Fie că plouă sau strălucește soarele, mergi la universitate și investește în tine însuți.",
        "Universitatea este locul unde îți poți descoperi pasiunile și talentele ascunse. Fii curajos și explorează cunoașterea, indiferent de vreme!",
        "Chiar și în cele mai ploioase zile, universitatea este un refugiu al învățăturii și al oportunităților. Profită de fiecare zi și mergi la universitate cu entuziasm!",
        "Indiferent de starea vremii, fiecare zi la universitate înseamnă oportunitatea de a te dezvolta, de a învăța lucruri noi și de a-ți extinde orizonturile.",
        "Chiar și în cele mai reci zile de iarnă sau în cele mai fierbinți zile de vară, universitatea este locul unde îți poți modela viitorul. Nu lăsa vremea să îți diminueze dorința de a învăța.",
        "Fiecare pas pe care îl faci spre universitate este un pas spre succesul viitor. Ignoră vremea și fii dedicat în atingerea obiectivelor tale academice.",
        "Vremea poate fi schimbătoare, dar oportunitățile de învățare și dezvoltare pe care le oferă universitatea sunt constante. Nu pierde șansa de a învăța și de a te dezvolta.",
        "Universitatea este locul unde îți poți întâlni colegi și profesori inspiraționali, unde poți construi relații și aliații pe termen lung. Nu rata această oportunitate indiferent de vreme!"

    ]

    comment = random.choice(comments)
    return comment
def get_weather(api_key, city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        wind_speed = data["wind"]["speed"]

        weather_info = f"Timpul de afară: {weather_description}\nTemperatura: {temperature}°C\nViteza vântului: {wind_speed} m/s \n" \
                       f"O zi perfecta pentru a merge la universitate!\n"
        weather_info += get_weather_comment()
        return weather_info
    else:
        return "Failed to fetch weather information"