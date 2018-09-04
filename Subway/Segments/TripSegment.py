from Subway.Segments.Segment import *


class RideTripSegment(RideSegment):

    def __init__(self, from_stop, to_stop, trip):
        super().__init__(from_stop, to_stop)
        self.trip = trip

    def get_trip(self):
        return self.trip

    def get_route(self):
        return self.get_trip().get_route()

    def get_direction_id(self):
        return self.get_trip().get_direction_id()

    def is_same_trip(self, other):
        return self.get_trip() == other.get_trip()

    def __str__(self):
        return "Ride: [%s] %s to %s" % (self.get_route(), self.get_from_station(), self.get_to_station())


class TransferTripSegment(TransferSegment):

    def __init__(self, from_stop, to_stop, connection_time):
        super().__init__(from_stop, to_stop)
        self.connection_time = connection_time

    def get_connection_time(self):
        return self.connection_time
