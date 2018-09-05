from Subway import *


def get_shortest_pair(stations):

    distances = []

    for from_station in stations:
        for to_station in stations:

            if from_station == to_station:
                continue

            dist_km = from_station.get_distance_km(to_station)
            dist_rides = from_station.get_distance_rides(to_station)
            dist_trans = from_station.get_distance_transfers(to_station)

            distances.append({"from_station": from_station, "to_station": to_station,
                              "dist_km": dist_km, "dist_rides": dist_rides, "dist_trans": dist_trans})

    min_rides = min([x["dist_km"] for x in distances])
    shortest = [x for x in distances if x["dist_km"] == min_rides]

    shortest.sort(key=lambda x: x["dist_rides"])

    return shortest[0]


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

    total_rides = 0
    total_trans = 0
    total_km = 0
    total_segments = 0

    for from_station in nodes:
        for to_station in nodes[from_station]:
            total_km += from_station.get_distance_km(to_station)
            total_rides += from_station.get_distance_rides(to_station)
            total_trans += from_station.get_distance_transfers(to_station)
            total_segments += from_station.get_distance_segments(to_station)

    print("System:")
    print("Rides: %d" % (total_rides / 2.0))
    print("Transfers: %d" % (total_trans / 2.0))
    print("Segments: %d" % (total_segments / 2.0))
    print("Distance: %.2f km" % (total_km / 2.0))

    while len(odd_vertices) > 0:
        shortest = get_shortest_pair(odd_vertices)

        from_station = shortest["from_station"]
        to_station = shortest["to_station"]

        nodes[from_station].append(to_station)
        nodes[to_station].append(from_station)

        odd_vertices = [station for station in nodes if len(nodes[station]) % 2 == 1]

    dist_total_km = 0
    dist_total_trans = 0
    dist_total_rides = 0
    dist_total_segs = 0

    for from_station in nodes:
        for to_station in nodes[from_station]:
            dist_total_km += from_station.get_distance_km(to_station)
            dist_total_rides += from_station.get_distance_rides(to_station)
            dist_total_trans += from_station.get_distance_transfers(to_station)
            dist_total_segs += from_station.get_distance_segments(to_station)

    print("\n")
    print("Shortest circuit:")
    print("Rides: %d" % (dist_total_rides / 2.0))
    print("Transfers: %d" % (dist_total_trans / 2.0))
    print("Segments: %d" % (dist_total_segs / 2.0))
    print("Distance: %.2f km" % (dist_total_km / 2.0))


if __name__ == "__main__":
    main()
