from Subway import *
from Subway.RouteChoosers import *


def main():

    def station_filter(station):
        return station.get_borough() == "Bk"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)

    rides = [LongestPathChooser.get_route(x) for x in system.get_stops()]

    rides.sort(key=lambda x: x.get_length(), reverse=True)

    print("Num available stations: %d" % len(system.get_stations()))
    print("Longest Brooklyn ride:")
    print(rides[0].get_ride_summary())

    for seg in rides[0].get_segments():
        print(seg)


if __name__ == "__main__":
    main()