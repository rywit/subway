from Subway import *
from Subway.Segments import *
from Subway.Utils import DistanceType
import pandas as pd
import math


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

    def lookup_route(self, route_name, borough):
        if route_name == "S":
            if borough == "Q":
                return self.get_route("H")
            elif borough == "Bk":
                return self.get_route("FS")
            elif borough == "M":
                return self.get_route("GS")
        else:
            return self.get_route(route_name)

    def load_stations(self, path, file_name):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading station data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        # Filter out staten island stations
        data = data.loc[data["borough"] != "SI"]

        # Convert station IDs to strings (instead of int)
        data["station_id"] = data["station_id"].apply(str)
        data["complex_id"] = data["complex_id"].apply(str)

        stations = {}
        stop_map = {}
        complex_map = {}

        station_filter = self.get_station_filter()

        for idx, row in data.iterrows():

            station_id = row["station_id"]
            stop_id = row["gtfs_stop_id"]
            complex_id = row["complex_id"]

            stop_map[stop_id] = station_id

            # Build set of routes stopping at this station
            borough = row["borough"]
            routes = {self.lookup_route(route_id, borough) for route_id in row["daytime_routes"].split()}

            if station_id in stations:
                stations[station_id].add_routes(routes)
            else:

                station = SubwayStation(station_id, row["stop_name"],
                                        row["latitude"], row["longitude"], borough,
                                        row["structure"], row["line"], row["division"], routes)

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

            # Skip this record if there is no parent stop ID
            if pd.isna(parent_stop_id):
                continue

            try:
                station_id = stop_map[parent_stop_id]
                parent_station = self.get_station(station_id)
            except KeyError:
                continue

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

            try:
                from_station = self.get_station(stop_map[from_stop_id])
                to_station = self.get_station(stop_map[to_stop_id])
            except KeyError:
                continue

            for from_stop in from_station.get_stops():
                for to_stop in to_station.get_stops():

                    # Do not add transfers from a stop to itself
                    if from_stop == to_stop:
                        continue

                    if from_station == to_station:
                        transfer = StopTransferSegment(from_stop, to_stop)
                        from_stop.add_stop_transfer_segment(transfer)
                    else:
                        transfer = StationTransferSegment(from_stop, to_stop)
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

        # Convert station IDs to strings (instead of int)
        data["from_station_id"] = data["from_station_id"].apply(str)
        data["to_station_id"] = data["to_station_id"].apply(str)

        # Iterate through each row in the data set
        for idx, row in data.iterrows():

            try:
                from_station = self.get_station(row["from_station_id"])
                to_station = self.get_station(row["to_station_id"])
            except KeyError:
                continue

            from_station.set_distance(to_station, DistanceType.KM, row["dist_km"])

    def load_ridership(self, path, file_name):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading ridership data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        # Convert complex IDs to strings (instead of int)
        data["complex_id"] = data["complex_id"].apply(str)

        # Iterate through each row in the data set
        for idx, row in data.iterrows():

            try:
                station_complex = self.get_complex(row["complex_id"])
            except KeyError:
                continue

            ridership_2017 = row["ridership_2017"]

            # Treat missing ridership data as zero (e.g. new stations and Cortlandt St)
            if math.isnan(ridership_2017):
                ridership_2017 = 0.0

            station_complex.set_ridership(ridership_2017)

    def calc_distances(self, method):

        print("Calculating station distances")

        for station in sorted(self.get_stations()):
            station.calc_distances(method)

    def load_basic_data(self, path):

        # Load route data
        self.load_routes(path, "routes.txt")

        # Load stations, station complexes and mapping to stop IDs
        stop_map = self.load_stations(path, "stations.txt")

        # Load stop data
        self.load_stops(path, "stops.txt", stop_map)

        # Load distance between each pair of connecting stops
        self.load_distances(path, "distances.txt")

        # Load transfer data
        self.load_transfers(path, "transfers.txt", stop_map)

        # Load ridership data
        self.load_ridership(path, "ridership.txt")

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

            try:
                from_stop = self.get_stop(row["from_stop_id"])
                to_stop = self.get_stop(row["to_stop_id"])
            except KeyError:
                continue

            from_stop.add_ride_segment(RideLinkSegment(from_stop, to_stop))

    def load_link_data(self, path):

        # Build link data
        self.load_links(path, "links.txt")


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

        # Iterate through each row in the data set
        for idx, row in data.iterrows():

            try:
                from_stop = self.get_stop(row["from_stop_id"])
                to_stop = self.get_stop(row["to_stop_id"])
                route = self.get_route(row["route_id"])
            except KeyError:
                continue

            from_stop.add_ride_segment(RideConnectionSegment(from_stop, to_stop, route))

    def load_connection_data(self, path):

        # Build connection data
        self.load_connections(path, "connections.txt")


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

    def load_trips(self, path, file_name):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk
        print("Loading trip data from '%s'" % full_path)
        data = pd.read_csv(full_path)

        trips = {}

        for idx, row in data.iterrows():
            trip_id = row["trip_id"]

            try:
                route = self.get_route(row["route_id"])
            except KeyError:
                continue

            trips[trip_id] = SubwayTrip(route, row["service_id"], trip_id, row["trip_headsign"], row["direction_id"])

        self.trips.update(trips)

        return self

    def load_stop_times(self, path, file_name):

        # Build full path to file
        full_path = "/".join([path, file_name])

        # Read data from disk and then sort by trip and stop sequence
        print("Loading stop time data from '%s'" % full_path)
        data = pd.read_csv(full_path).sort_values(by=["trip_id", "stop_sequence"])

        for idx, row in data.iterrows():

            try:
                stop = self.get_stop(row["stop_id"])
                trip = self.get_trip(row["trip_id"])
            except KeyError:
                continue

            # Build a new StopTime object, with links to the trip and the stop
            stop_time = SubwayStopTime(trip, row["arrival_time"], row["departure_time"],
                                       stop, row["stop_sequence"])

            # Add this stop time to the given trip
            trip.add_stop_time(stop_time)

        return self

    def load_trip_data(self, path):

        # Load trip dada
        self.load_trips(path, "trips.txt")

        # Load stop time data
        self.load_stop_times(path, "stop_times_weekday.txt")

        return self
