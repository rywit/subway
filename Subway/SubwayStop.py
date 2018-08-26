class SubwayStop:

    def __init__(self, id, parent_station):
        self.id = id
        self.parent_station = parent_station
        self.connections = set()

    def get_id(self):
        return self.id

    def get_station(self):
        return self.parent_station

    def get_station_name(self):
        return self.get_station().get_name()

    def add_connection(self, connection):
        self.connections.add(connection)
        return self

    def get_connections(self):
        return self.connections

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def __str__(self):
        return "%s (%s)" % (self.get_id(), self.get_station())
