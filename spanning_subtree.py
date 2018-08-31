from Subway import *


def main():

    # Load the data from disk
    system = SubwaySystem("data", load_times=False)

    complex_map = {}
    i = 0

    for station_complex in system.get_complexes():
        complex_map[station_complex] = i
        i += 1

    connections = []

    for from_stop in system.get_stops():
        for connection in from_stop.get_connections():
            connections.append(connection)

    for conn in connections:
        print("Conn: %s to %s" % (conn.get_from_stop(), conn.get_to_stop()))
        print("Dist: %.2f" % conn.get_distance())

    connections.sort(key=lambda x: x.get_distance())

    num_trees = len(complex_map)
    spanning_tree = []

    while num_trees > 1 and len(connections) > 0:
        conn = connections.pop(0)

        from_complex = conn.get_from_complex()
        to_complex = conn.get_to_complex()

        from_tree = complex_map[from_complex]
        to_tree = complex_map[to_complex]

        if from_tree != to_tree:
            # Move the "from" complex to the "to" complex tree
            complex_map[from_complex] = to_tree

            spanning_tree.append(conn)
            num_trees -= 1

    print("Found %d connections to span %d complexes" % (len(spanning_tree), len(system.get_complexes())))

    sum_distance = 0
    counts = {}

    for seg in spanning_tree:
        sum_distance += seg.get_distance()

        from_complex = seg.get_from_complex()
        to_complex = seg.get_to_complex()

        counts.setdefault(from_complex, 0)
        counts.setdefault(to_complex, 0)

        counts[from_complex] += 1
        counts[to_complex] += 1

    print("Total distance %.2f km" % sum_distance)

    counted = [(station_complex, count) for station_complex, count in counts.items()]

    counted.sort(key=lambda x: x[1], reverse=True)

    for station_complex, count in counted:
        print("%s: %d" % (station_complex, count))

    print("Done!")


if __name__ == "__main__":
    main()