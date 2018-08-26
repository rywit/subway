class Segment:

    def __init__(self, from_stop, to_stop, start_time_ts, stop_time_ts, seg_type):
        self.from_stop = from_stop
        self.to_stop = to_stop
        self.start_time_ts = start_time_ts
        self.stop_time_ts = stop_time_ts
        self.seg_type = seg_type

    def get_from_stop(self):
        return self.from_stop

    def get_to_stop(self):
        return self.to_stop

    def get_from_station(self):
        return self.get_from_stop().get_station()

    def get_to_station(self):
        return self.get_to_stop().get_station()

    def get_start_time_ts(self):
        return self.start_time_ts

    def get_stop_time_ts(self):
        return self.stop_time_ts

    def get_type(self):
        return self.seg_type

    def get_time_length(self):
        return self.get_stop_time_ts() - self.get_start_time_ts()

    def get_route(self):
        return None

    def get_direction_id(self):
        return None


class StartingSegment(Segment):

    def __init__(self, stop, time_ts):
        super().__init__(stop, stop, time_ts, time_ts, "Start")

    def __str__(self):
        return "%s: %s" % (self.get_type(), self.get_from_station())


class EndingSegment(Segment):

    def __init__(self, stop, time_ts):
        super().__init__(stop, stop, time_ts, time_ts, "End")

    def __str__(self):
        return "%s: %s" % (self.get_type(), self.get_from_station())


class RideSegment(Segment):

    def __init__(self, from_stop, to_stop, start_time_ts, end_time_ts, trip):
        super().__init__(from_stop, to_stop, start_time_ts, end_time_ts, "Ride")
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
        return "%s: [%s] %s to %s" % (self.get_type(), self.get_route(),
                                      self.get_from_station(), self.get_to_station())

    def merge(self, other):
        return RideSegment(self.get_from_stop(), other.get_to_stop(),
                           self.get_start_time_ts(), other.get_stop_time_ts(), self.get_trip())


class TransferSegment(Segment):

    def __init__(self, from_stop, to_stop, start_time_ts, end_time_ts):
        super().__init__(from_stop, to_stop, start_time_ts, end_time_ts, "Transfer")

    def is_station_transfer(self):
        return self.get_from_station() != self.get_to_station()

    def __str__(self):
        return "%s: %s to %s" % (self.get_type(), self.get_from_stop(), self.get_to_stop())


class StartingConnection(Segment):

    def __init__(self, stop):
        super().__init__(stop, stop, 0, 0, "Start")


class RideConnection(RideSegment):

    def __init__(self, from_stop, to_stop, route):
        super().__init__(from_stop, to_stop, 0, 0, None)
        self.route = route

    def get_route(self):
        return self.route

    def merge(self, other):
        return RideConnection(self.get_from_stop(), other.get_to_stop(), self.get_route())

    def __str__(self):
        return "%s: [%s] %s to %s" % (self.get_type(), self.get_route(),
                                      self.get_from_station(), self.get_to_station())


class TransferConnection(TransferSegment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop, 0, 0)

    def __str__(self):
        return "%s: %s to %s" % (self.get_type(), self.get_from_stop(), self.get_to_stop())


class EndingConnection(EndingSegment):

    def __init__(self, stop):
        super().__init__(stop, 0)

    def __str__(self):
        return "%s: %s" % (self.get_type(), self.get_from_station())
