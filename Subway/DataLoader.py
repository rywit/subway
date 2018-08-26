from Subway import *
import pandas as pd


class DataLoader:

    def __init__(self, path):
        # Load the data from disk
        self.__load(path)

    @staticmethod
    def __load_routes(path, file_name):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading route data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        routes = {}

        for idx, row in data.iterrows():
            route_id = row["route_id"]
            routes[route_id] = SubwayRoute(route_id, row["route_short_name"], row["route_long_name"])

        return routes

    @staticmethod
    def __load_stations(path, file_name):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading station data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        # Filter out staten island stations
        data = data.loc[data["borough"] != "SI"]

        stations = {}
        stop_map = {}

        for idx, row in data.iterrows():

            station_id = str(row["station_id"])
            stop_id = row["gtfs_stop_id"]

            stations[station_id] = SubwayStation(station_id, row["stop_name"], row["latitude"], row["longitude"],
                                                 row["borough"], row["structure"], row["line"])

            stop_map[stop_id] = station_id

        # Manually add South Ferry Loop
        stop_map["140"] = "330"

        return stations, stop_map

    @staticmethod
    def __load_stops(path, file_name, stations, stop_map):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading station data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        stops = {}

        # Iterate through data again
        for idx, row in data.iterrows():

            parent_stop_id = row["parent_station"]

            if not pd.isna(parent_stop_id):

                # Find the parent station for this stop
                parent_station = stations[stop_map[parent_stop_id]]

                stop_id = row["stop_id"]

                stop = SubwayStop(stop_id, parent_station)

                stops[stop_id] = stop
                parent_station.add_stop(stop)

        return stops

    @staticmethod
    def __load_trips(path, file_name, routes):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading trip data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        trips = {}

        for idx, row in data.iterrows():
            trip_id = row["trip_id"]
            route = routes[row["route_id"]]

            trips[trip_id] = SubwayTrip(route, row["service_id"], trip_id, row["trip_headsign"], row["direction_id"])

        return trips

    @staticmethod
    def __load_stop_times(path, file_name, trips, stops):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk and then sort by trip and stop sequence
        print("Loading stop time data from '%s'" % full_path)
        data = pd.read_csv(full_path).query('trip_id.str.contains("Weekday")').sort_values(by=["trip_id", "stop_sequence"])

        stop_times = []

        for idx, row in data.iterrows():
            # Pull out the trip_id and stop_id for this stop time
            trip_id = row["trip_id"]
            stop_id = row["stop_id"]

            # Skip this stop time if we don't have a valid stop (e.g. SIR)
            if stop_id not in stops:
                continue

            # Build a new StopTime object, with links to the trip and the stop
            stop_time = SubwayStopTime(trips[trip_id], row["arrival_time"], row["departure_time"],
                                       stops[stop_id], row["stop_sequence"])

            # Add this stop time to the given trip
            trips[trip_id].add_stop_time(stop_time)

            # Add this stop time to our return set
            stop_times.append(stop_time)

        return stop_times

    @staticmethod
    def __load_transfers(path, file_name, stations, stop_map):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading transfer data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        transfers = []

        # Iterate through each row in the data set
        for idx, row in data.iterrows():

            # Pull out the GTFS station ID for the two stations in the transfer
            from_stop_id = row["from_stop_id"]
            to_stop_id = row["to_stop_id"]

            from_station = stations[stop_map[from_stop_id]]
            to_station = stations[stop_map[to_stop_id]]

            # Build a transfer object
            transfer = SubwayTransfer(from_station, to_station, row["transfer_type"], row["min_transfer_time"])

            # Add transfer to the "from" station
            from_station.add_transfer(transfer)

        for station in stations.values():
            if len(station.get_transfers()) == 0:
                print("Adding self-transfer at %s" % station)
                station.add_transfer(SubwayTransfer(station, station, 2, 180))

        # Manually add transfer at South Ferry
        south_ferry = stations[stop_map["142"]]
        whitehall = stations[stop_map["R27"]]

        # South Ferry to Whitehall
        south_ferry.add_transfer(SubwayTransfer(south_ferry, whitehall, 2, 120))

        # Whitehall to South Ferry
        whitehall.add_transfer(SubwayTransfer(whitehall, south_ferry, 2, 120))

        return transfers

    @staticmethod
    def __link_stops(trips):

        # Iterate through each trip
        for trip in trips.values():

            stop_times = trip.get_stop_times()
            route = trip.get_route()

            for i in range(1, len(stop_times)):
                from_stop = stop_times[i-1].get_stop()
                to_stop = stop_times[i].get_stop()

                connection = StopConnection(from_stop, to_stop, route)
                from_stop.add_connection(connection)

    def __load(self, path):
        # Load route data
        routes = DataLoader.__load_routes(path, "routes.txt")

        stations, stop_map = DataLoader.__load_stations(path, "stations.txt")

        # Load station data
        stops = DataLoader.__load_stops(path, "stops.txt", stations, stop_map)

        # Load trip dada
        trips = DataLoader.__load_trips(path, "trips.txt", routes)

        # Load stop time data
        DataLoader.__load_stop_times(path, "stop_times.txt", trips, stops)

        DataLoader.__link_stops(trips)

        # Load transfer data
        DataLoader.__load_transfers(path, "transfers.txt", stations, stop_map)

        # Load time table to look up available segments
        timetable = TimeTable(trips)

        # Save output into instance
        self.routes = routes
        self.stations = stations
        self.stops = stops
        self.trips = trips
        self.timetable = timetable

    def get_routes(self):
        return self.routes

    def get_stations(self):
        return self.stations

    def get_stops(self):
        return self.stops

    def get_trips(self):
        return self.trips

    def get_timetable(self):
        return self.timetable
