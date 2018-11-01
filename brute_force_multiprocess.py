from Subway import *
import collections
import argparse
import multiprocessing as mp

# Define an output queue
output = mp.Queue()


def build_starting_branches(start_station_id, start_loc, ride_connections, trans_connections, q_limit=4):

    max_visited = 0

    q = collections.deque()
    q.append((start_station_id, True, start_loc, 1))

    num_paths = 0

    while q and len(q) < q_limit:

        cur = q.popleft()
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

    return max_visited, num_paths, q


def build_longest_path(start_paths, ride_connections, trans_connections, output):

    max_visited = 0

    q = collections.deque(start_paths)

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

        if num_paths % 10000000 == 0:
            print(num_paths)

    print("Num checked: %d" % num_paths)

    output.put((max_visited, num_paths))


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

    # Parameter for writing output to file
    parser.add_argument('-cpu', action='store', dest='cpu', type=int,
                        default=4, help='How many CPUs to use')

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
    cpus = args.cpu

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
        station_loc = 1 << id_map[station_id]

        max_len, num_paths, q = build_starting_branches(station_id, station_loc, ride_connections, trans_connections, 100)

        # Shuffle queue and partition
        random.shuffle(q)
        q_list = list(q)
        sets = [q_list[i::cpus] for i in range(cpus)]

        # Setup a list of processes that we want to run
        processes = [mp.Process(target=build_longest_path, args=(x, ride_connections, trans_connections, output)) for x in sets]

        # Run processes
        for p in processes:
            p.start()

        # Exit the completed processes
        for p in processes:
            p.join()

        # Get process results from the output queue
        for p in processes:
            visited, paths = output.get()

            if visited > max_len:
                max_len = visited

            num_paths += paths

        print("%s: %d" % (station, max_len))

        with open(args.out_file, "a") as out_file:
            out_file.write("%s (%d): %d, %d\n" % (station.get_name(), station.get_id(), max_len, num_paths))


if __name__ == "__main__":
    main()
