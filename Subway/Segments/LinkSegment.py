from Subway.Segments.Segment import *


class RideLinkSegment(RideSegment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)


class TransferLinkSegment(TransferSegment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)
