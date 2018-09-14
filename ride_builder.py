from Subway import *


def main():

    def station_filter(station):
        return station.get_borough() == "M" or station.get_borough() == "Bx"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)
    # to_visit = set([station for station in system.get_stations() if station.get_borough() == "Bx"])

    system.calc_segment_distances()

    stations = [system.get_station(station_id) for station_id in ["210", "215", "218"]]

    ride = SubwayRide.build_ride(stations)

    print(ride.print())


if __name__ == "__main__":
    main()