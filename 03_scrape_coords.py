
# Scrape airport coordinates and activation date from SkyVector

import csv
import requests
from bs4 import BeautifulSoup
import re
import os

# Function to clean up the airport name for the URL format
def clean_airport_name(name):
    # Remove anything inside parentheses or brackets, and special characters
    name = re.sub(r"[\(\)\[\]]", "", name)
    name = name.replace("&", "%20")
    name = re.sub(r"\s+", "-", name)  # Replace spaces and other separators with dashes
    return name.strip()

def scrape_skyvector(airport_url):

    # First URL attempt
    url1 = f"{airport_url}"

    response = requests.get(url1)
    if response.status_code != 200:
        print(f"Error: Could not retrieve data for airport code {airport_url}")
        return None, None, 9999, None, None
        
        
    soup = BeautifulSoup(response.text, 'html.parser')


    # Try to obtain the lat/lon and put into respective columns
    try:
        coord_text = soup.find(string=re.compile(r'N\d+°\d+')).strip()
        coord_text_clean = re.sub(r"Coordinates:\s*", "", coord_text)
        lat, lon = coord_text_clean.split(' / ')
        lat = lat.strip()
        lon = lon.strip()
    except AttributeError: #If they can't be found, just make both columns empty
        lat, lon = None, None

    # Try to obtain the activation year, airport use, and control tower
    try:
        
        info_table = soup.find_all("table")[0]  # first table is the airport info block
        table_text = info_table.get_text(" ", strip=True)  # all text, spaced

        # Airport Use
        airport_use = re.search(r"Use:\s*([^\n\r]+)", table_text)
        airport_use = airport_use.group(1).strip() if airport_use else None
        airport_use = re.split(r"Activation Date", airport_use)[0].strip()

        # Activation Year
        activation_year = re.search(r"Activation Date:\s*([A-Za-z]*\s*\d{4})", table_text)
        if activation_year:
            activation_year = re.search(r"\d{4}", activation_year.group(1))
            activation_year = activation_year.group(0) if activation_year else 9999
        else:
            activation_year = 9999

        # Control Tower
        control_tower_text = re.search(r"Control Tower:\s*(Yes|No)", table_text, re.IGNORECASE)
        if control_tower_text:
            control_tower_text = control_tower_text.group(1) if control_tower_text else None
        else:
            control_tower_text = 'Unknown'
        
        # Attendance (staffed or unstaffed)
        attendance = re.search(r"Attendance:\s*([^\n\r]+)", table_text, re.MULTILINE)
        if attendance:
            attendance = attendance.group(1).strip()
        else:
            attendance = 'Unknown'
        


    except (AttributeError, IndexError):
        print("Error finding year for this airport")
        activation_year = 9999
        control_tower_text = 'Unknown'
        airport_use = 'Unknown'
        attendance = 'Unknown'
        


    return lat, lon, activation_year, control_tower_text, airport_use, attendance



def process_airport_csv(input_csv, output_csv):

    with open(input_csv, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Latitude', 'Longitude', 'Activation_Year', 'Control_Tower', 'Airport_Use', 'Attendance']

    
        with open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                # Iterate through each row in the input CSV
                for row in reader:
                    airport_code = row['Code']
                    airport_name = row['Airport']
                    airport_url = row['URL']
                    
                    if airport_code:  # Only process if there's a valid code
                        lat, lon, activation_year, control_tower, airport_use, attendance = scrape_skyvector(airport_url)

                        # Add the scraped data to the row
                        row['Latitude'] = lat
                        row['Longitude'] = lon
                        row['Activation_Year'] = activation_year
                        row['Control_Tower'] = control_tower
                        row['Airport_Use'] = airport_use
                        row['Attendance'] = attendance

                    # Write the updated row to the output CSV
                    writer.writerow(row)

    print(f"Data saved to {output_csv}")

if __name__ == "__main__":

    state_name = input("Enter the state name (e.g., Maryland, Minnesota): ")
    input_csv = f'/Users/alliej/Desktop/bu/airports/example_data/{state_name.lower()}_airports_skyv.csv'

    output_csv = f'/Users/alliej/Desktop/bu/airports/example_data/{state_name.lower()}_coords_info_skyv.csv'

    process_airport_csv(input_csv, output_csv)
    print("\a")
    os.system("afplay /System/Library/Sounds/Blow.aiff") #plays a sound when code is done running
    #(mac only)

    