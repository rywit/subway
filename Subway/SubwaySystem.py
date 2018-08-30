from gc import __loader__

from Subway import *
import pandas as pd


class SubwaySystem:

    def __init__(self, path, load_times = True):
        self.__load(path, load_times)

    @staticmethod
    def load_routes(path, file_name):

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
    def load_stations(path, file_name):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading station data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        # Filter out staten island stations
        data = data.loc[data["borough"] != "SI"]

        stations = {}
        stop_map = {}
        complex_map = {}

        for idx, row in data.iterrows():

            station_id = str(row["station_id"])
            stop_id = row["gtfs_stop_id"]
            complex_id = str(row["complex_id"])

            if station_id not in stations:
                station = SubwayStation(station_id, row["stop_name"],
                                        row["latitude"], row["longitude"], row["borough"],
                                        row["structure"], row["line"], row["division"])

                stations[station_id] = station
                complex_map.setdefault(complex_id, set()).add(station)

            stop_map[stop_id] = station_id

        # Manually add South Ferry Loop
        stop_map["140"] = "330"

        complexes = {}

        # Build station complexes and link to stations
        for complex_id, station_set in complex_map.items():

            # Create new station complex, linking to underlying stations
            station_complex = StationComplex(complex_id, station_set)

            # Add complex to our final set of complexes
            complexes[complex_id] = station_complex

            # Link station to complex
            for station in station_set:
                station.set_station_complex(station_complex)

        return stations, complexes, stop_map

    @staticmethod
    def load_stops(path, file_name, stations, stop_map):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading stop data from '%s'" % full_path)
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
    def load_trips(path, file_name, routes):

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
    def load_stop_times(path, file_name, trips, stops):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk and then sort by trip and stop sequence
        print("Loading stop time data from '%s'" % full_path)
        data = pd.read_csv(full_path).sort_values(by=["trip_id", "stop_sequence"])

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
    def add_stop_transfer(station):

        for from_stop in station.get_stops():
            if len(from_stop.get_stop_transfers()) == 0:
                for to_stop in station.get_stops():
                    if from_stop != to_stop:
                        print("Adding stop transfer from %s to %s (%s)" %
                              (from_stop.get_id(), to_stop.get_id(), to_stop.get_station()))
                        from_stop.add_transfer(to_stop, 2, 180)

    @staticmethod
    def add_manual_transfers(stations, stop_map):

        # Manually add transfer at South Ferry to Whitehall (and vice-versa)
        south_ferry = stations[stop_map["142"]]
        whitehall = stations[stop_map["R27"]]

        for sf_stop in south_ferry.get_stops():
            for wh_stop in whitehall.get_stops():
                sf_stop.add_transfer(wh_stop, 2, 120)
                wh_stop.add_transfer(sf_stop, 2, 120)

    @staticmethod
    def load_transfers(path, file_name, stations, stop_map):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading transfer data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        # Iterate through each row in the data set
        for idx, row in data.iterrows():

            # Pull out the GTFS station ID for the two stations in the transfer
            from_stop_id = row["from_stop_id"]
            to_stop_id = row["to_stop_id"]
            transfer_type = row["transfer_type"]
            min_transfer_time = row["min_transfer_time"]

            from_station = stations[stop_map[from_stop_id]]
            to_station = stations[stop_map[to_stop_id]]

            for from_stop in from_station.get_stops():
                for to_stop in to_station.get_stops():

                    # Do not add transfers from a stop to itself
                    if from_stop == to_stop:
                        continue

                    from_stop.add_transfer(to_stop, transfer_type, min_transfer_time)

        # Add missing stop transfers
        for station in stations.values():
            SubwaySystem.add_stop_transfer(station)

        # Add manual transfers
        SubwaySystem.add_manual_transfers(stations, stop_map)

    @staticmethod
    def load_distances(path, file_name, stops):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading stop distance data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        # Iterate through each row in the data set
        for idx, row in data.iterrows():
            from_stop_id = row["from_stop_id"]
            to_stop_id = row["to_stop_id"]

            from_stop = stops[from_stop_id]
            to_stop = stops[to_stop_id]

            from_stop.set_distance(to_stop, row["dist_km"])

        return stops

    @staticmethod
    def load_connections(path, file_name, stops, routes):
        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading connection data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        # Iterate through each row in the data set
        for idx, row in data.iterrows():

            from_stop_id = row["from_stop_id"]
            to_stop_id = row["to_stop_id"]
            route_id = row["route_id"]

            from_stop = stops[from_stop_id]
            to_stop = stops[to_stop_id]
            route = routes[route_id]

            from_stop.add_connection(to_stop, route)

    @staticmethod
    def calc_station_distances(stations):
        for station in stations:
            station.calc_distances()

    def __load(self, path, load_times):

        # Load route data
        routes = self.load_routes(path, "routes.txt")

        stations, complexes, stop_map = self.load_stations(path, "stations.txt")

        # Load stop data
        stops = self.load_stops(path, "stops.txt", stations, stop_map)

        # Build connection data
        self.load_connections(path, "connections.txt", stops, routes)

        # Load transfer data
        self.load_transfers(path, "transfers.txt", stations, stop_map)

        # Calculate distance between pairs of stations
        self.calc_station_distances(stations.values())

        self.load_distances(path, "distances.txt", stops)

        if load_times:

            # Load trip dada
            trips = self.load_trips(path, "trips.txt", routes)

            # Load stop time data
            self.load_stop_times(path, "stop_times_weekday.txt", trips, stops)

            # Load time table to look up available segments
            self.timetable = TimeTable(trips)
            self.trips = trips

        # Save output into instance
        self.routes = routes
        self.stations = stations
        self.complexes = complexes
        self.stops = stops

    def get_routes(self):
        return set(self.routes.values())

    def get_route(self, route_id):
        return self.routes[route_id]

    def get_stations(self):
        return set(self.stations.values())

    def get_station(self, station_id):
        return self.stations[station_id]

    def get_complexes(self):
        return set(self.complexes.values())

    def get_complex(self, complex_id):
        return self.complexes[complex_id]

    def get_stops(self):
        return set(self.stops.values())

    def get_stop(self, stop_id):
        return self.stops[stop_id]

    def get_trips(self):
        return set(self.trips.values())

    def get_trip(self, trip_id):
        return self.trips[trip_id]

    def get_timetable(self):
        return self.timetable
