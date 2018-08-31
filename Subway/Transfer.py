class Transfer:

    def __init__(self, from_stop, to_stop, transfer_type, min_transfer_time):
        self.from_stop = from_stop
        self.to_stop = to_stop
        self.transfer_type = transfer_type
        self.min_transfer_time = min_transfer_time

    def get_from_stop(self):
        return self.from_stop

    def get_from_station(self):
        return self.get_from_stop().get_station()

    def get_to_stop(self):
        return self.to_stop

    def get_to_station(self):
        return self.get_to_stop().get_station()

    def get_type(self):
        return self.transfer_type

    def get_min_time(self):
        return self.min_transfer_time

    # For now, all transfers will be zero distance
    def get_distance_km(self):
        return 0


class StopTransfer(Transfer):

    def __init__(self, from_stop, to_stop, transfer_type, min_transfer_time):
        super().__init__(from_stop, to_stop, transfer_type, min_transfer_time)

    def __str__(self):
        return "Stop Transfer: %s to %s (%s)" % (self.get_from_stop().get_id(), self.get_to_stop().get_id(),
                                                 self.get_from_station())


class StationTransfer(Transfer):

    def __init__(self, from_stop, to_stop, transfer_type, min_transfer_time):
        super().__init__(from_stop, to_stop, transfer_type, min_transfer_time)

    def __str__(self):
        return "Station Transfer: %s to %s" % (self.get_from_stop(), self.get_to_stop())
