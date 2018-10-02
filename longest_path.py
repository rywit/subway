from Subway import *
import collections


def build_longest_path(start_station, reset_limit, reset_frac):

    print("%s (%d/%.2f)" % (start_station, reset_limit, reset_frac))

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

        if len(q) >= reset_limit:
            sample_size = int(reset_limit * reset_frac)
            subset = sorted(random.sample(range(len(q)), sample_size))
            q = collections.deque([q[i] for i in subset])

    return longest_path


def main():

    def station_filter(station):
        return True
#        return station.get_borough() == "M"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)

    longest = []

    while len(longest) <= 271:

        reset_limit = random.randint(1, 100000)
        reset_frac = random.uniform(0.1, 0.9)
        station = system.get_station(209)

        longest_path = build_longest_path(station, reset_limit, reset_frac)

        print("%s: %d" % (station, len(longest_path)))

        if len(longest_path) > len(longest):
            longest = longest_path

            print("---------------------")

            for station in longest:
                print("%s (%d)" % (station.get_name(), station.get_id()))


if __name__ == "__main__":
    main()
