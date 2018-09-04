class Segment:

    def __init__(self, from_stop, to_stop):
        self.from_stop = from_stop
        self.to_stop = to_stop

    def get_from_stop(self):
        return self.from_stop

    def get_to_stop(self):
        return self.to_stop

    def get_from_station(self):
        return self.get_from_stop().get_station()

    def get_to_station(self):
        return self.get_to_stop().get_station()


class StartingSegment(Segment):

    def __init__(self, stop):
        super().__init__(stop, stop)

    def __str__(self):
        return "Start: %s" % self.get_from_stop()


class RideSegment(Segment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)

    def get_distance_km(self):
        return self.get_from_stop().get_distance_km(self.get_to_stop())


class TransferSegment(Segment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)

    def is_station_transfer(self):
        return self.get_from_station() != self.get_to_station()

    def get_distance_km(self):
        return 0

    def __str__(self):
        return "Transfer: %s to %s" % (self.get_from_stop(), self.get_to_stop())


class EndingSegment(Segment):

    def __init__(self, stop):
        super().__init__(stop, stop)

    def __str__(self):
        return "End: %s [%d]" % self.get_to_station()
