from Subway import *
import pandas as pd
import numpy as np


def main():

    def station_filter(station):
        return True
        # return station.get_borough() == "Bk"

    # Load the data from disk
    system = SubwayLinkSystem("data", station_filter)

#    stations = sorted(filter(lambda x: x.get_borough() == "Bk", system.get_stations()))
    stations = sorted(system.get_stations())

    for station in stations:
        print("Calculating: %s" % station)
        station.calc_distances_km()

    rows = []

    for station1 in stations:
        row = []
        for station2 in stations:
            row.append(station1.get_distance_km(station2))

        rows.append(row)

    station_ids = [x.get_name() for x in stations]

    a = np.asarray(rows)
    df = pd.DataFrame(a)
    df.to_csv("data/distances.csv", index=False, header=station_ids)

    print("Done!")


if __name__ == "__main__":
    main()
