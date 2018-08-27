class SubwayStation:

    def __init__(self, station_id, name, lat, lon, borough, structure, line):
        self.station_id = station_id
        self.name = name
        self.lat = lat
        self.lon = lon
        self.borough = borough
        self.structure = structure
        self.line = line
        self.stops = []

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

    def add_stop(self, stop):
        self.stops.append(stop)
        return self

    def get_stops(self):
        return self.stops

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def __str__(self):
        return "%s (%s)" % (self.get_name(), self.get_id())

    def __hash__(self):
        return hash(self.get_id())
