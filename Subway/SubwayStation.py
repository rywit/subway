from Subway.Utils import DistanceType


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
        self.distances = {}
        self.paths = {}

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
            for to_stop in to_station.get_stops():
                seg = from_stop.get_segment_to_stop(to_stop)

                if seg is not None:
                    return seg

    def set_distance(self, to_station, method, distance):
        self.distances.setdefault(method, {})
        self.distances[method][to_station] = distance

    @staticmethod
    def get_shortest_path(paths, stations):
        segs = [paths[station] for station in stations]
        lens = [len(x) for x in segs]
        return segs[lens.index(min(lens))]

    def calc_distances(self, method):

        # Set defaults for this method, if necessary
        self.distances.setdefault(method, {})
        self.paths.setdefault(method, {})

        if method == DistanceType.Rides:
            depths, paths = SubwayStation.calc_station_distance_rides(self)
            self.distances[method].update(depths)
            self.paths[method].update(paths)
        elif method == DistanceType.Transfers:
            depths, paths = SubwayStation.calc_station_distance_transfers(self)
            self.distances[method].update(depths)
            self.paths[method].update(paths)
        elif method == DistanceType.Segments:
            depths, paths = SubwayStation.calc_station_distance_segments(self)
            self.distances[method].update(depths)
            self.paths[method].update(paths)
        elif method == DistanceType.KM:
            distances, paths = SubwayStation.calc_station_distance_km(self)
            self.distances[method].update(distances)
            self.paths[method].update(paths)

        return self

    def get_distance(self, method, to_station):
        if isinstance(to_station, SubwayStation):
            return self.distances[method][to_station]
        else:
            return min([self.distances[method][station] for station in to_station])

    def get_path(self, method, to_station):
        if isinstance(to_station, SubwayStation):
            return self.paths[method][to_station]
        else:
            return self.get_shortest_path(self.paths[method], to_station)

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
        return "%s" % self.get_name()

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
            cur_path = [station]

        should_recurse = False

        # Is this the optimal path (so far) to this station?
        if station not in depths:
            should_recurse = True
        elif depth < depths[station]:
            should_recurse = True
        elif depth == depths[station] and len(cur_path) < len(paths[station]):
            should_recurse = True

        if should_recurse:

            # Update depth and path to this station
            depths[station] = depth
            paths[station] = cur_path

            # Iterate to ride stations and increment depth
            for neighbor in station.get_connecting_ride_stations():
                new_path = cur_path.copy()
                new_path.append(neighbor)
                SubwayStation.calc_station_distance_rides(neighbor, depth + 1, depths, paths, new_path)

            # Iterate to transfer stations but don't increment depth
            for neighbor in station.get_connecting_transfer_stations():
                new_path = cur_path.copy()
                new_path.append(neighbor)
                SubwayStation.calc_station_distance_rides(neighbor, depth, depths, paths, new_path)

        return depths, paths

    @staticmethod
    def calc_station_distance_transfers(station, depth=0, depths=None, paths=None, cur_path=None):

        if depths is None:
            depths = {}
            paths = {}
            cur_path = [station]

        should_recurse = False

        # Is this the optimal path (so far) to this station?
        if station not in depths:
            should_recurse = True
        elif depth < depths[station]:
            should_recurse = True
        elif depth == depths[station] and len(cur_path) < len(paths[station]):
            should_recurse = True

        if should_recurse:

            # Update depth and path to this station
            depths[station] = depth
            paths[station] = cur_path

            # Iterate to ride stations but don't increment depth
            for neighbor in station.get_connecting_ride_stations():
                new_path = cur_path.copy()
                new_path.append(neighbor)
                SubwayStation.calc_station_distance_transfers(neighbor, depth, depths, paths, new_path)

            # Iterate to transfer stations and increment depth
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
            cur_path = [station]

        should_recurse = False

        # Is this the optimal path (so far) to this station?
        if station not in depths:
            should_recurse = True
        elif depth < depths[station]:
            should_recurse = True

        if should_recurse:

            # Update depth and path to this station
            depths[station] = depth
            paths[station] = cur_path

            # Iterate to connecting stations and increment depth
            for neighbor in station.get_connecting_stations():
                new_path = cur_path.copy()
                new_path.append(neighbor)
                SubwayStation.calc_station_distance_segments(neighbor, depth + 1, depths, paths, new_path)

        return depths, paths

    @staticmethod
    def calc_station_distance_km(station, distance=0, distances=None, paths=None, cur_path=None):

        if distances is None:
            distances = {}
            paths = {}
            cur_path = [station]

        should_recurse = False

        # Is this the optimal path (so far) to this station?
        if station not in distances:
            should_recurse = True
        elif distance < distances[station]:
            should_recurse = True

        if should_recurse:

            # Update depth and path to this station
            distances[station] = distance
            paths[station] = cur_path

            # Iterate to connecting stations and increment distance
            for neighbor in station.get_connecting_stations():
                new_path = cur_path.copy()
                new_path.append(neighbor)
                new_dist = station.get_distance(DistanceType.KM, neighbor)
                SubwayStation.calc_station_distance_km(neighbor, distance + new_dist, distances, paths, new_path)

        return distances, paths
