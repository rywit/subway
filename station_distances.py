from Subway import *


def distance_in_km(stations):

    distances = []

    for from_station in stations:
        for to_station in stations:
            if to_station <= from_station:
                continue

            dist = from_station.get_distance_km(to_station)

            distances.append({"from": from_station, "to": to_station, "dist": dist})

    sorted_km = sorted(filter(lambda x: x["dist"] > 0, distances), key=lambda x: x["dist"])

    print("By Distance km---")
    print("Closest stations:")

    for i in range(5):
        res = sorted_km[i]
        print("%s to %s: %.2f km" % (res["from"], res["to"], res["dist"]))

    print("Furthest stations:")

    for i in range(-1, -6, -1):
        res = sorted_km[i]
        print("%s to %s: %.2f km" % (res["from"], res["to"], res["dist"]))


def distance_in_segments(stations):

    distances = []

    for from_station in stations:
        for to_station in stations:
            if to_station <= from_station:
                continue

            dist = from_station.get_distance_segments(to_station)

            distances.append({"from": from_station, "to": to_station, "dist": dist})

    sorted_res = sorted(filter(lambda x: x["dist"] > 0, distances), key=lambda x: x["dist"])

    print("By Segments---")
    print("Closest stations:")

    for i in range(5):
        res = sorted_res[i]
        print("%s to %s: %d" % (res["from"], res["to"], res["dist"]))

    print("Furthest stations:")

    for i in range(-1, -6, -1):
        res = sorted_res[i]
        print("%s to %s: %d" % (res["from"], res["to"], res["dist"]))


def distance_in_rides(stations):

    distances = []

    for from_station in stations:
        for to_station in stations:
            if to_station <= from_station:
                continue

            dist = from_station.get_distance_rides(to_station)

            distances.append({"from": from_station, "to": to_station, "dist": dist})

    sorted_res = sorted(filter(lambda x: x["dist"] > 0, distances), key=lambda x: x["dist"])

    print("By Rides---")
    print("Furthest stations:")

    for i in range(-1, -6, -1):
        res = sorted_res[i]
        print("%s to %s: %d" % (res["from"], res["to"], res["dist"]))


def distance_in_transfers(stations):

    distances = []

    for from_station in stations:
        for to_station in stations:
            if to_station <= from_station:
                continue

            dist = from_station.get_distance_transfers(to_station)

            distances.append({"from": from_station, "to": to_station, "dist": dist})

    sorted_res = sorted(filter(lambda x: x["dist"] > 0, distances), key=lambda x: x["dist"])

    print("By Transfers---")
    print("Furthest stations:")

    for i in range(-1, -6, -1):
        res = sorted_res[i]
        print("%s to %s: %d" % (res["from"], res["to"], res["dist"]))


def average_distance_km(stations):

    distances = []

    for from_station in stations:

        cur_dist = []

        for to_station in stations:

            if from_station == to_station:
                continue

            dist = from_station.get_distance_km(to_station)
            cur_dist.append(dist)

        avg = sum(cur_dist) / len(cur_dist)
        distances.append({"station": from_station, "avg_dist": avg})

    sorted_dist = sorted(distances, key=lambda x: x["avg_dist"])

    print("Average Distance km---")
    print("Closest stations:")

    for i in range(5):
        res = sorted_dist[i]
        print("%s: %.2f km" % (res["station"], res["avg_dist"]))

    print("Furthest stations:")

    for i in range(-1, -6, -1):
        res = sorted_dist[i]
        print("%s: %.2f km" % (res["station"], res["avg_dist"]))


def average_distance_km_ridership(stations):

    distances = []

    for from_station in stations:

        cur_dist = []
        total_ridership = 0

        for to_station in stations:

            dist = from_station.get_distance_km(to_station)
            ridership = to_station.get_station_complex().get_proportional_ridership()

            cur_dist.append(dist * ridership)
            total_ridership += ridership

        avg = sum(cur_dist) / total_ridership
        distances.append({"station": from_station, "avg_dist": avg})

    sorted_dist = sorted(distances, key=lambda x: x["avg_dist"])

    print("")
    print("Average Distance km (ridership-weighted)---")
    print("Closest stations:")

    for i in range(10):
        res = sorted_dist[i]
        print("%s: %.2f km" % (res["station"], res["avg_dist"]))

    print("Furthest stations:")

    for i in range(-1, -11, -1):
        res = sorted_dist[i]
        print("%s: %.2f km" % (res["station"], res["avg_dist"]))


def main():

    # Load the data from disk
    system = SubwayLinkSystem("data")

    stations = list(system.get_stations())
    stations.sort()

    for station in stations:
        print("Calculating: %s" % station)
        station.calc_distances_km()

    distance_in_km(stations)

    distance_in_segments(stations)

    distance_in_rides(stations)

    distance_in_transfers(stations)

    average_distance_km(stations)

    average_distance_km_ridership(stations)


if __name__ == "__main__":
    main()