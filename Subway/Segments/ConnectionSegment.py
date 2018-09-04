from Subway.Segments.LinkSegment import *


class RideConnectionSegment(RideSegment):

    def __init__(self, from_stop, to_stop, route):
        super().__init__(from_stop, to_stop)
        self.route = route

    def get_route(self):
        return self.route

    def __str__(self):
        return "Ride: [%s] %s to %s" % (self.get_route(), self.get_from_station(), self.get_to_station())
