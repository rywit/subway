from Subway import *
import collections


def build_longest_path(station):

    q = collections.deque()
    q.append(([station], True))

    num_rides = 0
    longest_path = []

    while q:

        cur = q.pop()
        num_rides += 1

        cur_path = cur[0]
        just_transferred = cur[1]
        cur_station = cur_path[-1]

        if len(cur_path) > len(longest_path):
            longest_path = cur_path.copy()

        for conn_station in cur_station.get_connecting_ride_stations():
           if conn_station not in cur_path:
               new_path = cur_path.copy()
               new_path.append(conn_station)
               q.append((new_path, False))

        if just_transferred is False:
            for conn_station in cur_station.get_connecting_transfer_stations():
                if conn_station not in cur_path:
                    new_path = cur_path.copy()
                    new_path.append(conn_station)
                    q.append((new_path, False))

    return longest_path, num_rides


def main():

    def station_filter(station):
        return station.get_borough() == "M" or station.get_borough() == "XX"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)

    station_map = {}

    for station in system.get_stations():
        station_id = station.get_id()
        station_map[station_id] = int(station_id)

    longest_path = []
    total_rides = 0

    term_stations = [station for station in system.get_stations() if station.is_terminal()]
    num_stations = len(term_stations)
    station_num = 1

    print("Num stations: %d" % num_stations)

    for station in sorted(term_stations):

        path, num_rides = build_longest_path(station)

        print("(%d/%d) %s: %d (%d rides)" % (station_num, num_stations, station, len(path), num_rides))

        if len(path) > len(longest_path):
            longest_path = path.copy()

        station_num += 1
        total_rides += num_rides

    print("Total rides: %d" % total_rides)
    print("Longest: %d" % len(longest_path))

    for station in longest_path:
        print("%s (%s)" % (station, station.get_id()))


if __name__ == "__main__":
    main()