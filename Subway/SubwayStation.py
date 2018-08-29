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
        self.stops = []
        self.distances = {}

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
        self.stops.append(stop)
        return self

    def get_stops(self):
        return self.stops

    def get_connecting_stations(self):
        stations = set()

        for stop in self.get_stops():
            for conn in stop.get_connections():
                stations.add(conn.get_to_station())

            for trans in stop.get_station_transfers():
                stations.add(trans.get_to_station())

        return stations

    def calc_distances(self):
        self.distances = SubwayStation.calc_station_distances({self})
        return self

    def get_distance(self, to_station):
        return self.distances[to_station]

    def is_terminal(self):

        for stop in self.get_stops():
            if stop.is_terminal():
                return True

        return False

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

    @staticmethod
    def calc_station_distances(stations, depth=0, distances=None):

        if distances is None:
            distances = {}

        to_visit = set()

        # Set the distance for each of the stations
        for station in stations:
            distances[station] = depth

        # Pull out the neighbors of each of the stations (that we haven't visited yet)
        for station in stations:
            for neighbor in station.get_connecting_stations():
                if neighbor not in distances:
                    to_visit.add(neighbor)

        if len(to_visit) > 0:
            SubwayStation.calc_station_distances(to_visit, depth + 1, distances)

        return distances
