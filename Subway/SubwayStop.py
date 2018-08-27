from Subway.Transfer import *
from Subway.StopConnection import *


class SubwayStop:

    def __init__(self, id, parent_station):
        self.id = id
        self.parent_station = parent_station
        self.connections = {}
        self.stop_transfers = []
        self.station_transfers = []

    def get_id(self):
        return self.id

    def get_station(self):
        return self.parent_station

    def get_station_name(self):
        return self.get_station().get_name()

    def add_connection(self, to_stop, route):
        key = "%s/%s" % (to_stop.get_id(), route.get_id())

        if key not in self.connections:
            self.connections[key] = StopConnection(self, to_stop, route)

        return self

    def get_connections(self):
        return self.connections.values()

    def add_transfer(self, to_stop, transfer_type, min_transfer_time):

        if self.get_station() == to_stop.get_station():
            self.stop_transfers.append(StopTransfer(self, to_stop, transfer_type, min_transfer_time))
        else:
            self.station_transfers.append(StationTransfer(self, to_stop, transfer_type, min_transfer_time))

        return self

    def get_stop_transfers(self):
        return self.stop_transfers

    def get_station_transfers(self):
        return self.station_transfers

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def __str__(self):
        return "%s (%s)" % (self.get_id(), self.get_station())
