
#scrape list of airports from skyvector

import requests
from bs4 import BeautifulSoup
import csv

def generate_url(state):
    state_url = state.replace(' ', '%20')
    return f'https://skyvector.com/airports/United%20States/{state_url}'


# Function to scrape a state's airport list from SkyVector
def scrape_skyvector_state(state_name, filename):
    
    base_url = generate_url(state_name)
    
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to retrieve page for {state_name}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all table rows with the relevant classes: 'odd', 'even', 'views-row-first'
    airport_rows = soup.find_all('tr', class_=['odd', 'even', 'views-row-first'])
    if not airport_rows:
        print(f"No table found for {state_name}. The page format may differ.")
        return None


    with open(filename, mode = 'w', newline = '', encoding = 'utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Code', 'Airport', 'URL'])

        for row in airport_rows:
        # Find the 'a' tag containing the airport info
            link_tag = row.find('a')
            if link_tag:
                href = link_tag['href']  # Get the link suffix
                full_url = f"https://skyvector.com{href}"  # Construct full URL

                # Extract code and name from the link text
                link_text = link_tag.text.strip()
                code, name = link_text.split(' - ', 1)  # Split by " - " to separate code and name

                writer.writerow([code, name, full_url])
    print(f"Data for {state_name} saved to {filename}")


# Example usage: Scrape airports in Minnesota and save to a CSV
if __name__ == '__main__':
    state_name = input("Enter the state name (e.g., Minnesota, North Carolina): ")
    output_file = f'/Users/alliej/Desktop/bu/airports/example_data/{state_name.lower()}_airports_skyv.csv'

    scrape_skyvector_state(state_name, output_file)