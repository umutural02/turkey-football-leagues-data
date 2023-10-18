import requests
from bs4 import BeautifulSoup
import csv
import re

months = {
    "Oca": 1,
    "Şub": 2,
    "Mar": 3,
    "Nis": 4,
    "May": 5,
    "Haz": 6,
    "Tem": 7,
    "Ağu": 8,
    "Eyl": 9,
    "Eki": 10,
    "Kas": 11,
    "Ara": 12
}

base_url = "https://www.transfermarkt.com.tr/super-lig/spieltag/wettbewerb/"
leagues = ["TR1", "TR2", "TR3A", "TR3B"]
weeks = [str(i) for i in range(1, 39)]  # 1,38 included.
seasonSelector = "/plus/?saison_id=2023"
weekSelector = "&spieltag="

urls = [base_url + league + seasonSelector + weekSelector + week for league in leagues for week in weeks]

# Initialize an empty list to store the extracted data
all_data = []

for url in urls:
    # Send a request and get the page content
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all match divs
        match_divs = soup.find_all("div", class_="box")

        for match_div in match_divs:

            if match_div == match_divs[0] or match_div == match_divs[-1]:
                continue

            # Initialize data for each match
            match_data = {}

            # Get League info
            league_info = soup.find("div", class_="data-header__headline-wrapper").text.strip()
            match_data["League"] = league_info

            # Get HomeTeam, AwayTeam, HomeTeamGoals, AwayTeamGoals, and IsPlayed
            try:
                match_info = match_div.find("table").find_all("td")
            except:
                continue

            try:
                match_rows = match_div.find("table").find_all("tr")
            except:
                match_rows = None

            if(match_rows):
                try:
                    matchDate = match_rows[1].td.a.text.strip()
                    matchDateList = matchDate.split(' ')
                    matchDateList[1] = months[matchDateList[1]]
                    matchDate = str(matchDateList[0]) + "/" + str(matchDateList[1]) + "/" + str(matchDateList[2])
                    match_data["MatchDate"] = matchDate
                except:
                    continue
                

            # Get HomeTeam
            home_team_tag = match_info[0].a
            away_team_tag = match_info[7].a
            if home_team_tag == None or away_team_tag == None:
                continue

            match_data["HomeTeam"] = home_team_tag["title"]
            match_data["AwayTeam"] = away_team_tag["title"]


            # Extract HomeTeamGoals and AwayTeamGoals from the score

            try:
                score_span = match_info[4].span.a.span
            except:
                score_span = None

            
            if score_span and "finished" in score_span["class"]:
                home_goals, away_goals = map(int, score_span.text.strip().split(":"))
                match_data["HomeTeamGoals"] = home_goals
                match_data["AwayTeamGoals"] = away_goals
                match_data["IsPlayed"] = True

            else:
                match_data["HomeTeamGoals"] = None
                match_data["AwayTeamGoals"] = None
                match_data["IsPlayed"] = False


            # Get MatchWeek from the URL
            matches = re.search(r'=(\d+)$', url)

            if matches:
                match_data["MatchWeek"] = int(matches.group(1)) 
            else:
                match_data["MatchWeek"] = None

            # Append match data to the list
            all_data.append(match_data)
            
    else:
        print(f"Failed to retrieve the webpage for URL: {url}. Status code: {response.status_code}")

    print("Link: " + url + " is done.", end="\n")

# Create a CSV file and write all the data
with open("match_results.csv", "w", newline="", encoding='utf-8') as csvfile:
    fieldnames = ["League", "HomeTeam", "AwayTeam", "HomeTeamGoals", "AwayTeamGoals", "IsPlayed", "MatchDate", "MatchWeek"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write header row
    writer.writeheader()

    for match_data in all_data:
        writer.writerow(match_data)

print("CSV file 'match_results.csv' created successfully.")
