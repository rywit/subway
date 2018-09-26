from Subway import *
import pandas as pd
import numpy as np


def main():

    def station_filter(station):
        return True
#        return station.get_division() == "IRT"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)
    system.calc_distances(DistanceType.Segments)

    stations = sorted(system.get_stations())

    by_borough = {}

    # Group by borough and make an ordered list
    for station in stations:
        borough = station.get_borough()
        by_borough.setdefault(borough, []).append(station)

    next_stations = {}

    for borough in by_borough:
        station_list = by_borough[borough]

        for station, next_station in zip(station_list, station_list[1:]):
            next_stations[station] = next_station

        last_station = station_list[-1]
        first_station = station_list[0]
        next_stations[last_station] = first_station

    rows = []

    for station1 in stations:

        row = []
        borough = station1.get_borough()
        next_station = next_stations[station1]

        for station2 in stations:
            if station1 == station2:
                row.append(0)
            elif station2 == next_station:
                row.append(0)
            elif borough == station2.get_borough():
                row.append(None)
            else:
                seg_dist = next_station.get_distance(DistanceType.Segments, station2)
                row.append(seg_dist)

        rows.append(row)

    station_ids = [x.get_id() for x in stations]

    a = np.asarray(rows)
    df = pd.DataFrame(a)
    df.to_csv("data/clustered.csv", index=False, header=station_ids)

    print("Num stations: %d" % len(station_ids))

    print("Done!")


if __name__ == "__main__":
    main()
