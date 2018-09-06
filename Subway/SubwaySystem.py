from Subway import *
from Subway.Segments import *
import pandas as pd


class SubwaySystem:

    def __init__(self, station_filter):
        self.routes = {}
        self.complexes = {}
        self.stations = {}
        self.stops = {}
        self.station_filter = station_filter

    def get_station_filter(self):
        return self.station_filter

    def load_routes(self, path, file_name):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading route data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        routes = {}

        for idx, row in data.iterrows():
            route_id = row["route_id"]
            routes[route_id] = SubwayRoute(route_id, row["route_short_name"], row["route_long_name"])

        self.routes = routes

    def load_stations(self, path, file_name):

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

        station_filter = self.get_station_filter()

        for idx, row in data.iterrows():

            station_id = str(row["station_id"])
            stop_id = row["gtfs_stop_id"]
            complex_id = str(row["complex_id"])

            stop_map[stop_id] = station_id

            if station_id not in stations:
                station = SubwayStation(station_id, row["stop_name"],
                                        row["latitude"], row["longitude"], row["borough"],
                                        row["structure"], row["line"], row["division"])

                # Run station filter
                if station_filter(station):
                    stations[station_id] = station
                    complex_map.setdefault(complex_id, set()).add(station)

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

        self.stations = stations
        self.complexes = complexes

        return stop_map

    def load_stops(self, path, file_name, stop_map):

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

                station_id = stop_map[parent_stop_id]

                # Skip this stop if its parent station isn't in our included set
                if not self.is_valid_station(station_id):
                    continue

                # Find the parent station for this stop
                parent_station = self.get_station(station_id)

                stop_id = row["stop_id"]
                stop = SubwayStop(stop_id, parent_station)

                stops[stop_id] = stop
                parent_station.add_stop(stop)

        self.stops = stops

    @staticmethod
    def add_stop_transfer(station):

        for from_stop in station.get_stops():
            if len(from_stop.get_stop_transfer_segments()) == 0:
                for to_stop in station.get_stops():
                    if from_stop != to_stop:
                        print("Adding stop transfer from %s to %s (%s)" %
                              (from_stop.get_id(), to_stop.get_id(), to_stop.get_station()))
                        from_stop.add_stop_transfer_segment(TransferSegment(from_stop, to_stop))

    def add_manual_transfers(self, stop_map):

        south_ferry_id = stop_map["142"]
        whitehall_id = stop_map["R27"]

        # If we are excluding either south ferry or whitehall, leave
        if not self.is_valid_station(south_ferry_id) or not self.is_valid_station(whitehall_id):
            return

        # Manually add transfer at South Ferry to Whitehall (and vice-versa)
        south_ferry = self.get_station(south_ferry_id)
        whitehall = self.get_station(whitehall_id)

        for sf_stop in south_ferry.get_stops():
            for wh_stop in whitehall.get_stops():
                sf_stop.add_station_transfer(TransferSegment(sf_stop, wh_stop))
                wh_stop.add_station_transfer(TransferSegment(wh_stop, sf_stop))

    def load_transfers(self, path, file_name, stop_map):

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

            from_station_id = stop_map[from_stop_id]
            to_station_id = stop_map[to_stop_id]

            # Skip this transfer if it involves a station not in our included set
            if not self.is_valid_station(from_station_id) or not self.is_valid_station(to_station_id):
                continue

            from_station = self.get_station(from_station_id)
            to_station = self.get_station(to_station_id)

            for from_stop in from_station.get_stops():
                for to_stop in to_station.get_stops():

                    # Do not add transfers from a stop to itself
                    if from_stop == to_stop:
                        continue

                    if from_station == to_station:
                        transfer = TransferSegment(from_stop, to_stop)
                        from_stop.add_stop_transfer_segment(transfer)
                    else:
                        transfer = TransferSegment(from_stop, to_stop)
                        from_stop.add_station_transfer(transfer)

        # Add missing stop transfers
        for station in self.get_stations():
            SubwaySystem.add_stop_transfer(station)

        # Add manual transfers
        self.add_manual_transfers(stop_map)

    def load_distances(self, path, file_name):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading stop distance data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        # Iterate through each row in the data set
        for idx, row in data.iterrows():
            from_stop_id = row["from_stop_id"]
            to_stop_id = row["to_stop_id"]

            # Skip this stop if it's not in our included set
            if not self.is_valid_stop(from_stop_id) or not self.is_valid_stop(to_stop_id):
                continue

            from_stop = self.get_stop(from_stop_id)
            to_stop = self.get_stop(to_stop_id)

            from_stop.set_distance_km(to_stop, row["dist_km"])

    @staticmethod
    def calc_distances(stations):
        for station in stations:
            station.calc_distances_transfers()
            station.calc_distances_rides()
            station.calc_distances_segments()

    def load_basic_data(self, path):

        # Load route data
        self.load_routes(path, "routes.txt")

        # Load stations, station complexes and mapping to stop IDs
        stop_map = self.load_stations(path, "stations.txt")

        # Load stop data
        self.load_stops(path, "stops.txt", stop_map)

        # Load transfer data
        self.load_transfers(path, "transfers.txt", stop_map)

        # Load distance between each pair of connecting stops
        self.load_distances(path, "distances.txt")

        # Save output into instance

    def get_routes(self):
        return set(self.routes.values())

    def get_route(self, route_id):
        return self.routes[route_id]

    def get_stations(self):
        return set(self.stations.values())

    def get_station(self, station_id):
        return self.stations[station_id]

    def is_valid_station(self, station_id):
        return station_id in self.stations

    def get_complexes(self):
        return set(self.complexes.values())

    def get_complex(self, complex_id):
        return self.complexes[complex_id]

    def is_valid_complex(self, complex_id):
        return complex_id in self.complexes

    def get_stops(self):
        return set(self.stops.values())

    def get_stop(self, stop_id):
        return self.stops[stop_id]

    def is_valid_stop(self, stop_id):
        return stop_id in self.stops


class SubwayLinkSystem(SubwaySystem):

    def __init__(self, path, station_filter=lambda x: True):
        super().__init__(station_filter)
        self.load_basic_data(path)
        self.load_link_data(path)

    def load_links(self, path, file_name):
        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading link data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        # Iterate through each row in the data set
        for idx, row in data.iterrows():

            from_stop_id = row["from_stop_id"]
            to_stop_id = row["to_stop_id"]

            # Skip this link if one or both of the stops is not in our available set
            if not self.is_valid_stop(from_stop_id) or not self.is_valid_stop(to_stop_id):
                continue

            from_stop = self.get_stop(from_stop_id)
            to_stop = self.get_stop(to_stop_id)

            from_stop.add_ride_segment(RideLinkSegment(from_stop, to_stop))

    def load_link_data(self, path):

        # Build link data
        self.load_links(path, "links.txt")

        # Calculate distance between pairs of stations
        self.calc_distances(self.get_stations())


class SubwayConnectionSystem(SubwaySystem):

    def __init__(self, path, station_filter=lambda x: True):
        super().__init__(station_filter)
        self.load_basic_data(path)
        self.load_connection_data(path)

    def load_connections(self, path, file_name):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading connection data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        stops = self.get_stops()

        # Iterate through each row in the data set
        for idx, row in data.iterrows():

            from_stop_id = row["from_stop_id"]
            to_stop_id = row["to_stop_id"]
            route_id = row["route_id"]

            if not self.is_valid_stop(from_stop_id) or not self.is_valid_stop(to_stop_id):
                continue

            from_stop = self.get_stop(from_stop_id)
            to_stop = self.get_stop(to_stop_id)
            route = self.get_route(route_id)

            from_stop.add_ride_segment(RideConnectionSegment(from_stop, to_stop, route))

    def load_connection_data(self, path):

        # Build connection data
        self.load_connections(path, "connections.txt")

        # Calculate distance between pairs of stations
        self.calc_distances(self.get_stations())


class SubwayTripSystem(SubwaySystem):

    def __init__(self, path, station_filter=lambda x: True):
        super().__init__(station_filter)
        self.trips = {}
        self.timetable = None
        self.load_basic_data(path)
        self.load_trip_data(path)

    def get_trip(self, trip_id):
        return self.trips[trip_id]

    def get_trips(self):
        return self.trips

    def get_timetable(self):
        return self.timetable

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

    def load_trip_data(self, path):

        # Load trip dada
        trips = self.load_trips(path, "trips.txt", self.get_routes())

        # Load stop time data
        self.load_stop_times(path, "stop_times_weekday.txt", trips, self.get_stops())

        # Save output into instance
        self.trips = trips
        self.timetable = TimeTable(trips)
