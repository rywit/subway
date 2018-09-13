class SubwayStation:

    def __init__(self, station_id, name, lat, lon, borough, structure, line, division):
        self.station_id = station_id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.borough = borough
        self.structure = structure
        self.line = line
        self.division = division
        self.station_complex = None
        self.stops = set()
        self.distances_rides = {}
        self.paths_rides = {}
        self.distances_transfers = {}
        self.paths_transfers = {}
        self.distances_segments = {}
        self.paths_segments = {}
        self.distances_km = {}

    def get_id(self):
        return self.station_id

    def get_name(self):
        return self.name

    def get_latitude(self):
        return self.lat

    def get_longitude(self):
        return self.lon

    def get_borough(self):
        return self.borough

    def get_structure(self):
        return self.structure

    def get_line(self):
        return self.line

    def get_division(self):
        return self.division

    def add_stop(self, stop):
        self.stops.add(stop)
        return self

    def get_stops(self):
        return self.stops

    def get_connecting_stations(self):
        return self.get_connecting_ride_stations() | self.get_connecting_transfer_stations()

    def get_connecting_ride_stations(self):
        stations = set()

        for stop in self.get_stops():
            for conn in stop.get_ride_segments():
                stations.add(conn.get_to_station())

        return stations

    def get_connecting_transfer_stations(self):

        stations = set()

        for stop in self.get_stops():
            for trans in stop.get_station_transfer_segments():
                stations.add(trans.get_to_station())

        return stations

    def calc_distances_rides(self):
        depths, paths = SubwayStation.calc_station_distance_rides(self)
        self.distances_rides = depths
        self.paths_rides = paths
        return self

    def get_distance_rides(self, to_station):
        if isinstance(to_station, SubwayStation):
            return self.distances_rides[to_station]
        else:
            return min([self.distances_rides[station] for station in to_station])

    def get_path_rides(self, to_station):
        if isinstance(to_station, SubwayStation):
            return self.paths_rides[to_station]
        else:
            segs = [self.paths_rides[station] for station in to_station]
            lens = [len(x) for x in segs]
            return segs[lens.index(min(lens))]

    def calc_distances_transfers(self):
        depths, paths = SubwayStation.calc_station_distance_transfers(self)
        self.distances_transfers = depths
        self.paths_transfers = paths
        return self

    def get_distance_transfers(self, to_station):
        if isinstance(to_station, SubwayStation):
            return self.distances_transfers[to_station]
        else:
            return min([self.distances_transfers[station] for station in to_station])

    def get_path_transfers(self, to_station):
        if isinstance(to_station, SubwayStation):
            return self.paths_transfers[to_station]
        else:
            segs = [self.paths_transfers[station] for station in to_station]
            lens = [len(x) for x in segs]
            return segs[lens.index(min(lens))]

    def calc_distances_segments(self):
        depths, paths = SubwayStation.calc_station_distance_segments(self)
        self.distances_segments = depths
        self.paths_segments = paths
        return self

    def get_distance_segments(self, to_station):
        if isinstance(to_station, SubwayStation):
            return self.distances_segments[to_station]
        else:
            return min([self.distances_segments[station] for station in to_station])

    def get_path_segments(self, to_station):
        if isinstance(to_station, SubwayStation):
            return self.paths_segments[to_station]
        else:
            segs = [self.paths_segments[station] for station in to_station]
            lens = [len(x) for x in segs]
            return segs[lens.index(min(lens))]

    def calc_distances_km(self):
        self.distances_km = SubwayStation.calc_station_distance_km(self)
        return self

    def get_distance_km(self, to_station):
        if isinstance(to_station, SubwayStation):
            return self.distances_km[to_station]
        else:
            return min([self.distances_km[station] for station in to_station])

    def is_terminal(self):

        for stop in self.get_stops():
            if stop.is_terminal():
                return True

        return False

    def is_passthrough(self):
        for stop in self.get_stops():
            if not stop.is_passthrough():
                return False

        return True

    def set_station_complex(self, station_complex):
        self.station_complex = station_complex
        return self

    def get_station_complex(self):
        return self.station_complex

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def __str__(self):
        return "%s (%s)" % (self.get_name(), self.get_id())

    def __hash__(self):
        return hash(self.get_id())

    def __lt__(self, other):
        return self.get_id() < other.get_id()

    def __le__(self, other):
        return self.get_id() <= other.get_id()

    @staticmethod
    def calc_station_distance_rides(station, depth=0, depths=None, paths=None, cur_path=None):

        if depths is None:
            depths = {}
            paths = {}
            cur_path = []

        should_recurse = False

        if station not in depths:
            depths[station] = depth
            paths[station] = cur_path
            should_recurse = True
        elif depth < depths[station]:
            depths[station] = depth
            paths[station] = cur_path
            should_recurse = True
        elif depth == depths[station] and len(cur_path) < len(paths[station]):
            depths[station] = depth
            paths[station] = cur_path
            should_recurse = True

        if should_recurse:
            for neighbor in station.get_connecting_ride_stations():
                new_path = cur_path.copy()
                new_path.append(neighbor)
                SubwayStation.calc_station_distance_transfers(neighbor, depth + 1, depths, paths, new_path)

            for neighbor in station.get_connecting_transfer_stations():
                new_path = cur_path.copy()
                new_path.append(neighbor)
                SubwayStation.calc_station_distance_transfers(neighbor, depth, depths, paths, new_path)

        return depths, paths

    @staticmethod
    def calc_station_distance_transfers(station, depth=0, depths=None, paths=None, cur_path=None):

        if depths is None:
            depths = {}
            paths = {}
            cur_path = []

        should_recurse = False

        if station not in depths:
            depths[station] = depth
            paths[station] = cur_path
            should_recurse = True
        elif depth < depths[station]:
            depths[station] = depth
            paths[station] = cur_path
            should_recurse = True
        elif depth == depths[station] and len(cur_path) < len(paths[station]):
            depths[station] = depth
            paths[station] = cur_path
            should_recurse = True

        if should_recurse:
            for neighbor in station.get_connecting_ride_stations():
                new_path = cur_path.copy()
                new_path.append(neighbor)
                SubwayStation.calc_station_distance_transfers(neighbor, depth, depths, paths, new_path)

            for neighbor in station.get_connecting_transfer_stations():
                new_path = cur_path.copy()
                new_path.append(neighbor)
                SubwayStation.calc_station_distance_transfers(neighbor, depth + 1, depths, paths, new_path)

        return depths, paths

    @staticmethod
    def calc_station_distance_segments(station, depth=0, depths=None, paths=None, cur_path=None):

        if depths is None:
            depths = {}
            paths = {}
            cur_path = []

        should_recurse = False

        if station not in depths:
            depths[station] = depth
            paths[station] = cur_path
            should_recurse = True
        elif depth < depths[station]:
            depths[station] = depth
            paths[station] = cur_path
            should_recurse = True

        if should_recurse:
            for neighbor in station.get_connecting_stations():
                new_path = cur_path.copy()
                new_path.append(neighbor)
                SubwayStation.calc_station_distance_segments(neighbor, depth + 1, depths, paths, new_path)

        return depths, paths

    @staticmethod
    def calc_station_distance_km(station, dist=0, distances=None):

        if distances is None:
            distances = {}

        # Set the distance for each of the stations
        if station not in distances or dist < distances[station]:
            distances[station] = dist

            for stop in station.get_stops():

                # Connections to other stations
                for conn in stop.get_ride_segments():
                    new_dist = dist + conn.get_distance_km()
                    SubwayStation.calc_station_distance_km(conn.get_to_station(), new_dist, distances)

                # Transfers to other stations
                for trans in stop.get_station_transfer_segments():
                    new_dist = dist + trans.get_distance_km()
                    SubwayStation.calc_station_distance_km(trans.get_to_station(), new_dist, distances)

        return distances
