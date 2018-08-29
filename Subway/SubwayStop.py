from Subway.Transfer import *
from Subway.StopConnection import *


class SubwayStop:

    def __init__(self, stop_id, parent_station):
        self.stop_id = stop_id
        self.parent_station = parent_station
        self.connections = set()
        self.stop_transfers = set()
        self.station_transfers = set()
        self.distances = {}

    def get_id(self):
        return self.stop_id

    def get_station(self):
        return self.parent_station

    def get_station_name(self):
        return self.get_station().get_name()

    def add_connection(self, to_stop, route):
        self.connections.add(StopConnection(self, to_stop, route))
        return self

    def get_connections(self):
        return self.connections

    def add_transfer(self, to_stop, transfer_type, min_transfer_time):

        if self.get_station() == to_stop.get_station():
            self.stop_transfers.add(StopTransfer(self, to_stop, transfer_type, min_transfer_time))
        else:
            self.station_transfers.add(StationTransfer(self, to_stop, transfer_type, min_transfer_time))

        return self

    def get_stop_transfers(self):
        return self.stop_transfers

    def get_station_transfers(self):
        return self.station_transfers

    def is_terminal(self):
        return len(self.get_connections()) == 0

    def set_distance(self, to_stop, dist_km):
        self.distances[to_stop] = dist_km
        return self

    def get_distance(self, to_stop):
        if to_stop in self.distances:
            return self.distances[to_stop]
        else:
            return None

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def __str__(self):
        return "%s (%s)" % (self.get_id(), self.get_station())

    def __hash__(self):
        return hash(self.get_id())
