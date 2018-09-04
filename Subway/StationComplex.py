class StationComplex:

    def __init__(self, complex_id, stations):
        self.complex_id = complex_id
        self.stations = stations

    def get_id(self):
        return self.complex_id

    def get_stations(self):
        return self.stations

    def get_stops(self):
        stops = set()

        for station in self.get_stations():
            for stop in station.get_stops():
                stops.add(stop)

        return stops

    def get_connections(self):
        connections = set()

        for stop in self.get_stops():
            for connection in stop.get_ride_segments():
                connections.add(connection)

        return connections

    def get_name(self):
        return "/".join(map(str, self.get_stations()))

    def __hash__(self):
        return hash(self.get_id())

    def __str__(self):
        return self.get_name()
