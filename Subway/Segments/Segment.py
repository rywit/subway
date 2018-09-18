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

    def reset_to_stop(self, to_stop):
        self.to_stop = to_stop
        return self


class StartingSegment(Segment):

    def __init__(self, stop):
        super().__init__(stop, stop)

    def __str__(self):
        return "Start: %s" % self.get_from_stop()


class RideSegment(Segment):

    def __init__(self, from_stop, to_stop, num_stops=1):
        super().__init__(from_stop, to_stop)
        self.num_stops = num_stops

    def __hash__(self):
        return hash(self.get_id())

    def __eq__(self, other):
        return isinstance(other, RideSegment) and self.get_id() == other.get_id()

    def get_id(self):
        return "%s/%s" % (self.get_from_stop().get_id(), self.get_to_stop().get_id())

    def get_distance_km(self):
        return self.get_from_stop().get_distance_km(self.get_to_stop())

    def get_num_stops(self):
        return self.num_stops

    def reset_num_stops(self, other_num_stops):
        self.num_stops += other_num_stops
        return self


class TransferSegment(Segment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)

    def get_id(self):
        return "%s/%s" % (self.get_from_stop().get_id(), self.get_to_stop().get_id())

    def get_distance_km(self):
        return 0

    def __hash__(self):
        return hash(self.get_id())

    def __eq__(self, other):
        return isinstance(other, TransferSegment) and self.get_id() == other.get_id()

    def merge(self, other):
        return self.reset_to_stop(other.get_to_stop())


class StationTransferSegment(TransferSegment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)

    def is_station_transfer(self):
        return True

    def __str__(self):
        from_station_name = self.get_from_station().get_name()
        to_station_name = self.get_to_station().get_name()

        from_stop_id = self.get_from_stop().get_id()
        to_stop_id = self.get_to_stop().get_id()

        if from_station_name == to_station_name:
            return "Station Transfer: %s (%s to %s)" % (from_station_name, from_stop_id, to_stop_id)
        else:
            return "Station Transfer: %s (%s) to %s (%s)" % (from_station_name, from_stop_id, to_station_name, to_stop_id)


class StopTransferSegment(TransferSegment):

    def __init__(self, from_stop, to_stop):
        super().__init__(from_stop, to_stop)

    def is_station_transfer(self):
        return False

    def __str__(self):
        station = self.get_from_station()
        from_stop = self.get_from_stop()
        to_stop = self.get_to_stop()
        return "Stop Transfer: %s (%s to %s)" % (station.get_name(), from_stop.get_id(), to_stop.get_id())


class EndingSegment(Segment):

    def __init__(self, stop):
        super().__init__(stop, stop)

    def __str__(self):
        return "End: %s" % self.get_to_station()


class ErrorSegment(Segment):

    def __init__(self, stop):
        super().__init__(stop, stop)

    def __str__(self):
        return "ERROR: %s" % self.get_to_station()
