import requests
from bs4 import BeautifulSoup

def main():
    page = requests.get("https://www.mbta.com/stops/place-harsq")
    if page.status_code != 200:
        print("There was an error with the web request. Status code: " + str(page.status_code))
        pass
    
    soup = BeautifulSoup(page.content, "html.parser")

    route = soup.find(class_="c-link-block h3 m-tnm-sidebar__route-name u-bg--red-line").parent
    directions = route.find_all(class_="m-tnm-sidebar__direction")
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

    print("\nFor the Harvard T station...")

    for direction in all_trains:
        print("-" * 60)
        print(direction + " Trains:")
        print("-" * 60)

        for terminus in all_trains[direction]:
            for i in range(len(all_trains[direction][terminus])):
                time = all_trains[direction][terminus][i]
                minute = " minute." if time == "1" else " minutes."
                if time == "arriving" and i == 0:
                    print("The next train to " + terminus + " is now arriving.")
                elif i == 0:
                    print("The next train to " + terminus + " arrives in " + time + minute)
                else:
                    print ("The following train to " + terminus + " arrives in " + time + minute)
            print("\n")

main()      