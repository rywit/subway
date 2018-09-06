from Subway.Segments.Segment import *


class RideLinkSegment(RideSegment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)

    def __str__(self):
        return "Ride: %s to %s" % (self.get_from_station(), self.get_to_station())


class TransferLinkSegment(TransferSegment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)

    def __str__(self):
        return "Transfer: %s to %s" % (self.get_from_stop(), self.get_to_stop())
