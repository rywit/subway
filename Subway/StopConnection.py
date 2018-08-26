class StopConnection:

    def __init__(self, from_stop, to_stop, route):
        self.from_stop = from_stop
        self.to_stop = to_stop
        self.route = route
        self.connection_id = "%s/%s/%s" % (from_stop, to_stop, route)

    def get_from_stop(self):
        return self.from_stop

    def get_to_stop(self):
        return self.to_stop

    def get_from_station(self):
        return self.get_from_stop().get_station()

    def get_to_station(self):
        return self.get_to_stop().get_station()

    def get_route(self):
        return self.route

    def get_id(self):
        return self.connection_id

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def __hash__(self):
        return hash(self.get_id())
