from Subway.Segments.Segment import *


class RideLinkSegment(RideSegment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)

    def __str__(self):
        num_stops = self.get_num_stops()

        from_station_name = self.get_from_station().get_name()
        to_station_name = self.get_to_station().get_name()

        from_stop_id = self.get_from_stop().get_id()
        to_stop_id = self.get_to_stop().get_id()

        if num_stops == 1:
            return "Ride 1 stop: %s (%s) to %s (%s)" % (from_station_name, from_stop_id, to_station_name, to_stop_id)
        else:
            return "Ride %d stops: %s (%s) to %s (%s)" % (num_stops, from_station_name, from_stop_id, to_station_name, to_stop_id)

    def merge(self, other):
        self.reset_to_stop(other.get_to_stop())
        self.reset_num_stops(other.get_num_stops())
        return self


class TransferLinkSegment(TransferSegment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)

    def __str__(self):
        return "Transfer: %s to %s" % (self.get_from_stop(), self.get_to_stop())

    def merge(self, other):
        return self.reset_to_stop(other.get_to_stop())
