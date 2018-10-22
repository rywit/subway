from Subway import *
import collections


def build_longest_path(start_station_id, start_loc, reset_limit, ride_connections, trans_connections):

    max_visited = 0

    q = collections.deque()
    q.append((start_station_id, True, start_loc, 1))

    num_paths = 0

    while q:

        cur = q.popleft() if len(q) > reset_limit else q.pop()
        num_paths += 1

        cur_station_id = cur[0]
        just_transferred = cur[1]
        visited = cur[2]
        num_visited = cur[3]

        if num_visited > max_visited:
            max_visited = num_visited

            if max_visited > 110:
                print("New longest: %d" % max_visited)

        for conn_station_id, loc in ride_connections[cur_station_id]:
            if not visited & loc:
                q.append((conn_station_id, False, visited | loc, num_visited + 1))

        if not just_transferred:
            for conn_station_id, loc in trans_connections[cur_station_id]:
                if not visited & loc:
                    q.append((conn_station_id, True, visited | loc, num_visited + 1))

        if num_paths % 100000000 == 0:
            print(num_paths)

    print("Num checked: %d" % num_paths)

    return max_visited, num_paths


def main():

    def station_filter(station):
#        return True
        return station.get_borough() == "M"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)

    ride_connections = {}
    trans_connections = {}

    id_map = {}
    station_num = 1

    for station in system.get_stations():
        station_id = station.get_id()
        id_map[station_id] = station_num
        station_num += 1

    for station in system.get_stations():
        station_id = station.get_id()

        ride_connections[station_id] = [(conn.get_id(), 1 << id_map[conn.get_id()]) for conn in station.get_connecting_ride_stations()]
        trans_connections[station_id] = [(conn.get_id(), 1 << id_map[conn.get_id()]) for conn in station.get_connecting_transfer_stations()]

    total_paths = 0
    longest = 0

    station_set = [station for station in system.get_stations() if station.get_id() > 100]

    for station in sorted(station_set, key=lambda x: x.get_id()):
        reset_limit = 100000

        print(station)
        station_id = station.get_id()

        longest_path, num_paths = build_longest_path(station_id, 1 << id_map[station_id], reset_limit, ride_connections, trans_connections)

        total_paths += num_paths

        print("%s: %d" % (station, longest_path))

        if longest_path > longest:
            longest = longest_path
            print("---------------------")

    print("Paths: %d, Longest: %d" % (total_paths, longest))


if __name__ == "__main__":
    main()
