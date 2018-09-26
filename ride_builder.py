from Subway import *
from Subway.Utils import DistanceType
import json


def main():

    def station_filter(station):
        return station.get_division() == "IRT"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)

    system.calc_distances(DistanceType.Segments)

    with open("data/longest_path.json") as f:
        station_ids = json.load(f)

    stations = [system.get_station(station_id) for station_id in station_ids]

    for station in stations:
        print("%s %s: %s" % (station.get_id(), station.get_borough(), station))

#    ride = SubwayRide.build_ride_from_links(stations, DistanceType.Segments)

    # print("----------------")
    # print(ride.get_ride_summary())
    # print(ride.print())


if __name__ == "__main__":
    main()
