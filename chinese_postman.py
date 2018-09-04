from Subway import *


def get_shortest_pair(stations):

    distances = []

    for from_station in stations:
        for to_station in stations:

            if from_station == to_station:
                continue

            dist = from_station.get_distance_km(to_station)

            distances.append({"from_station": from_station, "to_station": to_station, "dist": dist})

    distances.sort(key=lambda x: x["dist"])

    return distances[0]


def main():

    # Load the data from disk
    system = SubwayLinkSystem("data")

    for station in system.get_stations():
        print("Calculating: %s" % station)
        station.calc_distances_km()

    nodes = {}

    for from_station in system.get_stations():
        for to_station in from_station.get_connecting_stations():
            nodes.setdefault(from_station, set()).add(to_station)
            nodes.setdefault(to_station, set()).add(from_station)

    odd_vertices = [station for station in nodes if len(nodes[station]) % 2 == 1]

    print("Num odd stations: %d of %d" % (len(odd_vertices), len(nodes)))

    while len(odd_vertices) > 0:
        shortest = get_shortest_pair(odd_vertices)

        from_station = shortest["from_station"]
        to_station = shortest["to_station"]

        nodes[from_station].add(to_station)
        nodes[to_station].add(from_station)

        odd_vertices = [station for station in nodes if len(nodes[station]) % 2 == 1]

        print("Num odd stations: %d of %d" % (len(odd_vertices), len(nodes)))

    dist_total = 0

    for from_station in nodes:
        for to_station in nodes[from_station]:
            dist_total += from_station.get_distance_km(to_station)

    print("Total path length: %.2f" % dist_total)

    print("Done!")


if __name__ == "__main__":
    main()