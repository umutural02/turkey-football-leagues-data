import requests
from bs4 import BeautifulSoup
import csv

base_url = "https://www.transfermarkt.com.tr/super-lig/stadien/wettbewerb/"
leagues = ["TR1", "TR2", "TR3A", "TR3B"]
detailSelector = "/plus/1"
column_headers = ["Name", "City", "Capacity", "UndersoilHeating", "LodgeAmount"]

urls = [base_url + league + detailSelector for league in leagues]

# Initialize an empty list to store the extracted data
stadium_data = []

for url in urls:

    # Send a request and get the page content
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table with class "items"
        table = soup.find("table", class_="items")

        if table:
            # Extract table data
            rows = table.find("tbody").find_all("tr")

            for row in rows:
                columns = row.find_all("td")
                row_data = {}  # Initialize with Name and City

                # Extract the Name of the Stadium from the first column's second a tag's title
                inner_table = columns[0].find("table", class_="inline-table")
                inner_table_rows = []
                if inner_table:
                    inner_table_rows = inner_table.find_all("tr")
                    
                
                if(len(inner_table_rows) < 2):
                    continue

                try:
                    stadium_name = inner_table_rows[0].find_all("td")[1].a.text.strip()
                    row_data["Name"] = stadium_name
                except:
                    print(f"There was an error finding the name of the stadium in url {url}")

                

                try:
                    city_info = inner_table_rows[1].find_all("td")[0].text.strip()
                    city = city_info.split('/')[-1].strip() if '/' in city_info else city_info
                    row_data["City"] = city
                except:
                    print(f"There was an error finding the City of the stadium in url {url}")

                # Extract the Capacity information from the second column
                try:
                    capacity = int(columns[4].text.replace('.', '').strip())
                except:
                    capacity = None
                row_data["Capacity"] = capacity

                # Extract the UndersoilHeating information from the fourth column
                deneme = columns[6].text.strip().lower()
                undersoil_heating = True if columns[6].text.strip().lower() == "evet" else None
                undersoil_heating = False if columns[6].text.strip().lower() == "hayır" else undersoil_heating
                row_data["UndersoilHeating"] = undersoil_heating

                # Extract the LodgeAmount information from the fifth column
                try:
                    lodge_amount = int(columns[7].text.replace('.', '').strip())
                except:
                    lodge_amount = None
                row_data["LodgeAmount"] = lodge_amount

                # Append the stadium data to the list
                stadium_data.append(row_data)
        else:
            print(f"Table not found for URL: {url}")
    else:
        print(f"Failed to retrieve the webpage for URL: {url}. Status code: {response.status_code}")

# Create a CSV file and write all the data
with open("stadium_info.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=column_headers)
    
    # Write header row
    writer.writeheader()

    for row_data in stadium_data:
        writer.writerow(row_data)

print("CSV file 'stadium_info.csv' created successfully.")

