from Subway import *


def get_shortest_pair(stations):

    distances = []

    for from_station in stations:
        for to_station in stations:

            if from_station == to_station:
                continue

            dist = from_station.get_distance_hops(to_station)

            distances.append({"from_station": from_station, "to_station": to_station, "dist": dist})

    distances.sort(key=lambda x: x["dist"])

    return distances[0]


def main():

    # Load the data from disk
    system = SubwayLinkSystem("data")

    stations = list(system.get_stations())
    stations.sort()

    for station in stations:
        print("Calculating: %s" % station)
        station.calc_distances_km()

    nodes = {}

    for from_station in system.get_stations():
        for to_station in from_station.get_connecting_stations():
            nodes.setdefault(from_station, [])
            nodes.setdefault(to_station, [])

            if to_station not in nodes[from_station]:
                nodes[from_station].append(to_station)

            if from_station not in nodes[to_station]:
                nodes[to_station].append(from_station)

    odd_vertices = [station for station in nodes if len(nodes[station]) % 2 == 1]

    total_hops = 0
    total_km = 0

    for from_station in nodes:
        for to_station in nodes[from_station]:
            total_km += from_station.get_distance_km(to_station)
            total_hops += from_station.get_distance_hops(to_station)

    print("Num hops in system: %d" % (total_hops / 2.0))
    print("Length of system: %.2f" % (total_km / 2.0))

    while len(odd_vertices) > 0:
        shortest = get_shortest_pair(odd_vertices)

        from_station = shortest["from_station"]
        to_station = shortest["to_station"]

        print("Adding edge: %.2f" % shortest["dist"])

        nodes[from_station].append(to_station)
        nodes[to_station].append(from_station)

        odd_vertices = [station for station in nodes if len(nodes[station]) % 2 == 1]

    dist_total_km = 0
    dist_total_hops = 0

    for from_station in nodes:
        for to_station in nodes[from_station]:
            dist_total_km += from_station.get_distance_km(to_station)
            dist_total_hops += from_station.get_distance_hops(to_station)

    print("Shortest circuit: %d" % (dist_total_hops / 2.0))
    print("Length of circuit (km): %.2f" % (dist_total_km / 2.0))

    print("Done!")


if __name__ == "__main__":
    main()
