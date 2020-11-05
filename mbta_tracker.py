import sys
import requests
from bs4 import BeautifulSoup

LINES = ["Red Line", "Blue Line", "Orange Line", "Green Line B", "Green Line C", "Green Line D", "Green Line E"]

def main():
    if len(sys.argv) != 2:
        print("Usage: harvard_t.py \"station_name\"\nIf the station name has spaces, put quotes around it.")
        sys.exit(2)

    hub_page = requests.get("https://www.mbta.com/stops/subway")
    if hub_page.status_code != 200:
        print("There was an error with the web request. Status code: " + str(hub_page.status_code))
        pass
    
    hub_document = BeautifulSoup(hub_page.content, "html.parser")
    results = hub_document.findAll(attrs={"data-name":sys.argv[1]})
    if results == []:
        print("Couldn't find a station with that name.")
        sys.exit(1)

    link = results[0]["href"]
    # print(results[0]["href"])

    page = requests.get("https://www.mbta.com" + link)
    if page.status_code != 200:
        print("There was an error with the web request. Status code: " + str(page.status_code))
        pass
    
    document = BeautifulSoup(page.content, "html.parser")

    routes = document.findAll(class_="c-link-block__inner")
    lines = {}
    for route in routes:
        if route.span.getText() in LINES:
            lines.update({route.parent.parent:route.span.getText()})
    
    all_lines = {}
    for line in lines:
        directions = line.find_all(class_="m-tnm-sidebar__direction")
        all_trains = {}

        for direction in directions:
            schedules = direction.find_all(class_="m-tnm-sidebar__headsign-schedule")

            trains = {}
            for schedule in schedules:
                end_name = schedule.find(class_="m-tnm-sidebar__headsign-name m-tnm-sidebar__headsign-name--large").getText()
                times = schedule.findAll(class_="m-tnm-sidebar__time-number")
                arrivals = []
                for time in times:
                    arrivals.append(time.getText())
                trains.update({end_name: arrivals})

            all_trains.update({list(direction.children)[0].getText(): trains})

        all_lines.update({lines[line]:all_trains})
    
    # print(all_lines)

    print(f"\nFor the {sys.argv[1]} T station...")

    for line in all_lines:
        print("=" * 60)
        print(line.upper())
        print("=" * 60)
        for direction in all_lines[line]:
            print(direction + " Trains")
            print("-" * 60)

            for terminus in all_lines[line][direction]:
                for i in range(len(all_lines[line][direction][terminus])):
                    time = all_lines[line][direction][terminus][i]
                    minute = " minute." if time == "1" else " minutes."
                    if time == "arriving" and i == 0:
                        print("The next train to " + terminus + " is now arriving.")
                    elif i == 0:
                        print("The next train to " + terminus + " arrives in " + time + minute)
                    elif time.isnumeric():
                        print("The following train to " + terminus + " arrives in " + time + minute)
                    else:
                        print("Status of next train: " + time)
                print("-" * 60)
                
    print()

main()      