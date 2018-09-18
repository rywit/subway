from Subway.Segments.Segment import *


class RideLinkSegment(RideSegment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)

    def __str__(self):
        num_stops = self.get_num_stops()

        if num_stops == 1:
            return "Ride 1 stop: %s to %s" % (self.get_from_station(), self.get_to_station())
        else:
            return "Ride %d stops: %s to %s" % (num_stops, self.get_from_station(), self.get_to_station())

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
