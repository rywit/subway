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
        self.paths_km = {}

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

    def get_segment_to_station(self, to_station):
        for from_stop in self.get_stops():
            for to_stop in to_station.get_stop():
                seg = from_stop.get_segment_to_stop(to_stop)

                if seg is not None:
                    return seg

    @staticmethod
    def get_shortest_path(paths, stations):
        segs = [paths[station] for station in stations]
        lens = [len(x) for x in segs]
        return segs[lens.index(min(lens))]

    def calc_distances_rides(self, save_paths=False):
        depths, paths = SubwayStation.calc_station_distance_rides(self, save_paths)
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
            return self.get_shortest_path(self.paths_rides, to_station)

    def calc_distances_transfers(self, save_paths=False):
        depths, paths = SubwayStation.calc_station_distance_transfers(self, save_paths)
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
            return self.get_shortest_path(self.paths_transfers, to_station)

    def calc_distances_segments(self, save_paths=False):
        depths, paths = SubwayStation.calc_station_distance_segments(self, save_paths)
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
            return self.get_shortest_path(self.paths_transfers, to_station)

    def calc_distances_km(self, save_paths=False):
        distances, paths = SubwayStation.calc_station_distance_km(self, save_paths)
        self.distances_km = distances
        self.paths_km = paths
        return self

    def get_distance_km(self, to_station):
        if isinstance(to_station, SubwayStation):
            return self.distances_km[to_station]
        else:
            return min([self.distances_km[station] for station in to_station])

    def get_path_km(self, to_station):
        if isinstance(to_station, SubwayStation):
            return self.paths_km[to_station]
        else:
            return self.get_shortest_path(self.paths_km, to_station)

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
    def build_new_path(save_paths, cur_path, station):
        if save_paths:
            new_path = cur_path.copy()
            new_path.append(station)
            return new_path
        else:
            return None

    @staticmethod
    def calc_station_distance_rides(station, save_paths, depth=0, depths=None, paths=None, cur_path=None):

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
        elif depth == depths[station] and cur_path is not None and len(cur_path) < len(paths[station]):
            depths[station] = depth
            paths[station] = cur_path
            should_recurse = True

        if should_recurse:
            for neighbor in station.get_connecting_ride_stations():
                new_path = SubwayStation.build_new_path(save_paths, cur_path, neighbor)
                SubwayStation.calc_station_distance_rides(neighbor, save_paths, depth + 1, depths, paths, new_path)

            for neighbor in station.get_connecting_transfer_stations():
                new_path = SubwayStation.build_new_path(save_paths, cur_path, neighbor)
                SubwayStation.calc_station_distance_rides(neighbor, save_paths, depth, depths, paths, new_path)

        return depths, paths

    @staticmethod
    def calc_station_distance_transfers(station, save_paths, depth=0, depths=None, paths=None, cur_path=None):

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
        elif depth == depths[station] and cur_path is not None and len(cur_path) < len(paths[station]):
            depths[station] = depth
            paths[station] = cur_path
            should_recurse = True

        if should_recurse:
            for neighbor in station.get_connecting_ride_stations():
                new_path = SubwayStation.build_new_path(save_paths, cur_path, neighbor)
                SubwayStation.calc_station_distance_transfers(neighbor, save_paths, depth, depths, paths, new_path)

            for neighbor in station.get_connecting_transfer_stations():
                new_path = SubwayStation.build_new_path(save_paths, cur_path, neighbor)
                SubwayStation.calc_station_distance_transfers(neighbor, save_paths, depth + 1, depths, paths, new_path)

        return depths, paths

    @staticmethod
    def calc_station_distance_segments(station, save_paths, depth=0, depths=None, paths=None, cur_path=None):

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
                new_path = SubwayStation.build_new_path(save_paths, cur_path, neighbor)
                SubwayStation.calc_station_distance_segments(neighbor, save_paths, depth + 1, depths, paths, new_path)

        return depths, paths

    @staticmethod
    def calc_station_distance_km(station, save_paths, distance=0, distances=None, paths=None, cur_path=None):

        if distances is None:
            distances = {}
            paths = {}
            cur_path = []

        should_recurse = False

        if station not in distances:
            distances[station] = distance
            paths[station] = cur_path
            should_recurse = True
        elif distance < distances[station]:
            distances[station] = distance
            paths[station] = cur_path
            should_recurse = True

        if should_recurse:
            for neighbor in station.get_connecting_stations():
                new_path = SubwayStation.build_new_path(save_paths, cur_path, neighbor)
                new_dist = station.get_distance_km(neighbor)
                SubwayStation.calc_station_distance_km(neighbor, save_paths, distance + new_dist, distances, paths, new_path)

        return distances, paths
