from Subway import *
from Subway.RouteChoosers import *
import random


def get_lengths(chooser, to_visit):

    lens = []

    for station in sorted(to_visit):
        for stop in station.get_stops():
            shortest = chooser.get_route(stop, to_visit)

            if shortest is not None and not shortest.is_error():
                lens.append(shortest)

    return lens


def main():

    def station_filter(station):
        # return station.get_borough() == "Q" or station.get_borough() == "Bk"
        return station.get_borough() == "Bk"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)
    to_visit = set([station for station in system.get_stations() if station.get_borough() == "Bk"])

    chooser = ShortestPathChooser2(500)

    lens = get_lengths(chooser, to_visit)

    lens.sort(key=lambda x: x.get_length())
    shortest = lens[0]

    print("Num available stations: %d" % len(to_visit))
    print("Shortest ride:")
    print(shortest.get_ride_summary())

    for seg in shortest.get_segments():
        print(seg)


if __name__ == "__main__":
    main()
