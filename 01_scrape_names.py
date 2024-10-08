
#scrape airport names

import requests
from bs4 import BeautifulSoup
import csv

def scrape_airports(year):

    base_url = "https://en.wikipedia.org/wiki/Category:Airports_established_in_"
    year_url = base_url + str(year)

    response = requests.get(year_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    #all airport names under mw-category group
    airports = []
    groups = soup.find_all('div', class_ = 'mw-category-group')
    for group in groups:
        links = group.find_all('a') #all anchor tags
        for link in links:
            airport_name = link.text.strip()
            airport_url = 'https://en.wikipedia.org' + link['href']
            airports.append((airport_name, airport_url))

    csv_filename = f'airports_{year}.csv'
    
    with open(csv_filename, 'w', newline = '', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Airport Name', 'URL'])
        writer.writerows(airports)

    print(f"Scraped and saved {len(airports)} airports for the year {year} in {csv_filename}.")


scrape_airports(1950)

