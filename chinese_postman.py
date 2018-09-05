from Subway import *


def summarise(nodes):
    dist = {"segments": 0, "km": 0}

    for from_station in nodes:
        for to_station in nodes[from_station]:
            dist["km"] += from_station.get_distance_km(to_station)
            dist["segments"] += from_station.get_distance_segments(to_station)

    print("Stations: %d" % len(nodes))
    print("Segments: %d" % (dist["segments"] / 2.0))
    print("Distance: %.2f km" % (dist["km"] / 2.0))


def get_shortest_pair(stations):

    distances = []

    for from_station in stations:
        for to_station in stations:

            if from_station == to_station:
                continue

            dist_km = from_station.get_distance_km(to_station)
            dist_segs = from_station.get_distance_segments(to_station)

            distances.append({"from_station": from_station, "to_station": to_station,
                              "dist_km": dist_km, "dist_segs": dist_segs})

    distances.sort(key=lambda x: (x["dist_km"], x["dist_segs"]))

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
        for to_station in from_station.get_connecting_ride_stations():
            nodes.setdefault(from_station, [])
            nodes.setdefault(to_station, [])

            if to_station not in nodes[from_station]:
                nodes[from_station].append(to_station)

            if from_station not in nodes[to_station]:
                nodes[to_station].append(from_station)

    odd_vertices = [station for station in nodes if len(nodes[station]) % 2 == 1]

    print("System:")
    summarise(nodes)

    while len(odd_vertices) > 0:
        shortest = get_shortest_pair(odd_vertices)

        from_station = shortest["from_station"]
        to_station = shortest["to_station"]

        nodes[from_station].append(to_station)
        nodes[to_station].append(from_station)

        odd_vertices = [station for station in nodes if len(nodes[station]) % 2 == 1]

    print("Circuit:")
    summarise(nodes)


if __name__ == "__main__":
    main()
