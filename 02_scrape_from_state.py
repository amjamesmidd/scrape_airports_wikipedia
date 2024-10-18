# Scrape names from a state's page

import requests
from bs4 import BeautifulSoup
import csv

def generate_url(state):
    state_url = state.replace(' ', '_')
    return f'https://en.wikipedia.org/wiki/List_of_airports_in_{state_url}'

def extract_airports(state, filename):

    url = generate_url(state)

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error: Could not retrieve data for {state}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')

    with open(filename, mode = 'w', newline = '', encoding = 'utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(['City', 'Code', 'Airport', 'URL'])

        table = soup.find('table', {'class': 'wikitable'})

        if not table:
            print(f"No table found for {state}. The page format may differ.")
            return
        
        for row in table.find_all('tr')[1:]:
            columns = row.find_all('td')

            if len(columns) < 5 or not columns[0].get_text(strip=True):
                continue

            
            city = columns[0].get_text(strip = True)
            code = columns[1].get_text(strip = True)
            airport = columns[4].get_text(strip = True)

            link_tag = columns[4].find('a')
            if link_tag:
                link = f"https://en.wikipedia.org{link_tag['href']}".replace(',', '') 
            else: link = 'NA'

            if city:
                writer.writerow([city, code, airport, link])

    print(f"Data for {state} saved to {filename}")


if __name__ == "__main__":
    state_name = input("Enter the state name (e.g., Minnesota, North_Carolina) with underscores instead of spaces: ")
    filename = f'/Users/alliej/Desktop/bu/airports/example_data/{state_name}_airports.csv'

    extract_airports(state_name, filename)
