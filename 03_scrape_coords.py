
# Scrape airport coordinates and activation date from SkyVector

import csv
import requests
from bs4 import BeautifulSoup
import re

# Function to clean up the airport name for the URL format
def clean_airport_name(name):
    # Remove anything inside parentheses or brackets, and special characters
    name = re.sub(r"[\(\)\[\]]", "", name)
    name = name.replace("&", "%20")
    name = re.sub(r"\s+", "-", name)  # Replace spaces and other separators with dashes
    return name.strip()

def scrape_skyvector(airport_code, airport_name):

    # First URL attempt
    url1 = f"https://skyvector.com/airport/{airport_code}"

    response = requests.get(url1)
    if response.status_code != 200:
        print(f"Error: Could not retrieve data for airport code {airport_code}")
        cleaned_name = clean_airport_name(airport_name)
        url2 = f"https://skyvector.com/airport/{airport_code}/{cleaned_name}"
        response = requests.get(url2)

        if response.status_code != 200:  # If the second attempt also fails, return None
            print(f"Error: Could not retrieve data for airport code {airport_code} using both URLs.")
            return None, None, 9999, None
        sv_url = url2
    else:
        sv_url = url1
        
    
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        coord_text = soup.find(string=re.compile(r'N\d+°\d+')).strip()
        coord_text_clean = re.sub(r"Coordinates:\s*", "", coord_text)
        lat, lon = coord_text_clean.split(' / ')
        lat = lat.strip()
        lon = lon.strip()
    except AttributeError:
        lat, lon = None, None

    try:
        activation_table = soup.find_all('table')[1]  # This finds the second table as in your XPath
        activation_year_row = activation_table.find_all('tr')[1]  # Find the second row in the table
        activation_year_text = activation_year_row.find('td').text.strip()
        activation_year = re.search(r'\d{4}', activation_year_text).group(0) 
    except (AttributeError, IndexError):
        activation_year = 9999

    return lat, lon, activation_year, sv_url



def process_airport_csv(input_csv, output_csv):

    with open(input_csv, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Latitude', 'Longitude', 'Activation Year', 'Wiki URL', 'SV URL']

    
        with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                # Iterate through each row in the input CSV
                for row in reader:
                    airport_code = row['Code']
                    airport_name = row['Airport']
                    
                    if airport_code:  # Only process if there's a valid code
                        lat, lon, activation_year, sv_url = scrape_skyvector(airport_code, airport_name)

                        wiki_url = f"https://en.wikipedia.org/wiki/{airport_name.replace(' ', '_')}"
                        row['Wiki URL'] = wiki_url

                        # Add the scraped data to the row
                        row['Latitude'] = lat
                        row['Longitude'] = lon
                        row['Activation Year'] = activation_year
                        row['SV URL'] = sv_url

                    # Write the updated row to the output CSV
                    writer.writerow(row)

    print(f"Data saved to {output_csv}")

if __name__ == "__main__":
    input_csv = "/Users/alliej/Documents/cafe/scrape_airports_wikipedia/example data/airports_missouri.csv"  # Replace with your input CSV file
    output_csv = "/Users/alliej/Documents/cafe/scrape_airports_wikipedia/example data/airports_missouri_coords.csv"
    
    process_airport_csv(input_csv, output_csv)

    
