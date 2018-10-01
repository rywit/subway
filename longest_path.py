from Subway import *
import collections


def build_longest_path(start_station):

    longest_path = []

    q = collections.deque()

    q.append(([start_station], True))

    while q:

        cur = q.popleft()

        cur_path = cur[0]
        cur_station = cur_path[-1]
        just_transferred = cur[1]

        if len(cur_path) > len(longest_path):
            longest_path = cur_path.copy()

        for conn_station in cur_station.get_connecting_ride_stations():
            if conn_station not in cur_path:
                new_path = cur_path.copy()
                new_path.append(conn_station)
                q.append((new_path, False))

        if not just_transferred:
            for conn_station in cur_station.get_connecting_transfer_stations():
                if conn_station not in cur_path:
                    new_path = cur_path.copy()
                    new_path.append(conn_station)
                    q.append((new_path, True))

        if len(q) >= 100000:
            subset = sorted(random.sample(range(len(q)), 50000))
            q = collections.deque([q[i] for i in subset])

    return longest_path


def main():

    def station_filter(station):
        return station.get_borough() == "M"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)

    longest = []

    for station in sorted(system.get_stations()):
        longest_path = build_longest_path(station)

        print("%s: %d" % (station, len(longest_path)))

        if len(longest_path) > len(longest):
            longest = longest_path

            for station in longest:
                print("%s (%d)" % (station.get_name(), station.get_id()))


if __name__ == "__main__":
    main()
