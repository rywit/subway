from Subway import *
import collections
import argparse


def build_longest_path(start_station_id, start_loc, ride_connections, trans_connections):

    max_visited = 0

    q = collections.deque()
    q.append((start_station_id, True, start_loc, 1))

    num_paths = 0

    while q:

        cur = q.pop()
        num_paths += 1

        cur_station_id = cur[0]
        just_transferred = cur[1]
        visited = cur[2]
        num_visited = cur[3]

        if num_visited > max_visited:
            max_visited = num_visited

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


def parse_args():
    parser = argparse.ArgumentParser(description="Brute-force route-calculating script")

    # Parameter for filtering by borough (M, Bx, Q, Bk)
    parser.add_argument('-b', action='append', dest='borough',
                        default=[], help='Which borough(s) to operate on')

    # Parameter for filtering by station ID
    parser.add_argument('-s', action='append', dest='station_ids', type=int,
                        default=[], help='Which station(s) to operate on')

    # Parameter for writing output to file
    parser.add_argument('-f', action='store', dest='out_file',
                        default="results/brute_force.txt", help='Where to write results')

    return parser.parse_args()


def build_connection_maps(system):

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

        rides = station.get_connecting_ride_stations()
        trans = station.get_connecting_transfer_stations()

        ride_connections[station_id] = [(conn.get_id(), 1 << id_map[conn.get_id()]) for conn in rides]
        trans_connections[station_id] = [(conn.get_id(), 1 << id_map[conn.get_id()]) for conn in trans]

    return id_map, ride_connections, trans_connections


def get_station_set(system, args):

    if len(args.station_ids):
        return [station for station in system.get_stations() if station.get_id() in args.station_ids]

    return system.get_stations()


def main():

    args = parse_args()

    def station_filter(station):
        for borough in args.borough:
            if station.get_borough() == borough:
                return True

        return False

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)

    # Build maps to make connection lookups faster
    id_map, ride_connections, trans_connections = build_connection_maps(system)

    station_set = get_station_set(system, args)

    for station in station_set:

        print(station)
        station_id = station.get_id()

        longest_path, num_paths = build_longest_path(station_id, 1 << id_map[station_id], ride_connections, trans_connections)

        print("%s: %d" % (station, longest_path))

        with open(args.out_file, "a") as out_file:
            out_file.write("%s (%d): %d, %d\n" % (station.get_name(), station.get_id(), longest_path, num_paths))


if __name__ == "__main__":
    main()
