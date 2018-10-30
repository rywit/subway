from Subway import *
import collections


def main():

    def station_filter(station):
#        return True
        return station.get_borough() == "M"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)

    link_file = open("data/links.csv", "w")
    trans_file = open("data/trans.csv", "w")

    for station in system.get_stations():
        station_id = station.get_id()

        # Print ride connections
        for conn in station.get_connecting_ride_stations():
            link_file.write("%d,%d\n" % (station_id, conn.get_id()))

        # Print transfer connections
        for conn in station.get_connecting_transfer_stations():
            trans_file.write("%d,%d\n" % (station_id, conn.get_id()))

    print("Done!")


if __name__ == "__main__":
    main()
