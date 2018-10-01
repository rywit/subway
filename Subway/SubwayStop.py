class SubwayStop:

    def __init__(self, stop_id, parent_station):
        self.stop_id = stop_id
        self.parent_station = parent_station
        self.ride_segments = set()
        self.stop_transfers = set()
        self.station_transfers = set()
        self.distances_km = {}

    def get_id(self):
        return self.stop_id

    def get_station(self):
        return self.parent_station

    def get_station_name(self):
        return self.get_station().get_name()

    def add_ride_segment(self, ride_seg):
        self.ride_segments.add(ride_seg)
        self.get_station().add_connecting_ride_station(ride_seg.get_to_station())
        return self

    def get_ride_segments(self):
        return self.ride_segments

    def get_segment_to_stop(self, to_stop):
        for ride in self.get_ride_segments():
            if ride.get_to_stop() == to_stop:
                return ride

        for transfer in self.get_station_transfer_segments():
            if transfer.get_to_stop() == to_stop:
                return transfer

    def add_stop_transfer_segment(self, transfer):
        self.stop_transfers.add(transfer)
        return self

    def get_stop_transfer_segments(self):
        return self.stop_transfers

    def add_station_transfer(self, transfer):
        self.station_transfers.add(transfer)
        self.get_station().add_connecting_transfer_station(transfer.get_to_station())
        return self

    def get_station_transfer_segments(self):
        return self.station_transfers

    def get_connecting_stops(self):
        stops = set()

        for seg in self.get_ride_segments():
            stops.add(seg.get_to_stop())

        for seg in self.get_station_transfer_segments():
            stops.add(seg.get_to_stop())

        for seg in self.get_stop_transfer_segments():
            stops.add(seg.get_to_stop())

    def is_terminal(self):
        return len(self.get_ride_segments()) == 0

    def is_passthrough(self):
        return len(self.get_ride_segments()) == 1 and len(self.get_station_transfer_segments()) == 0

    def set_distance_km(self, to_stop, dist_km):

        if to_stop in self.get_connecting_stops():
            self.distances_km[to_stop] = dist_km

        return self

    def get_distance_km(self, to_stop):
        if to_stop in self.distances_km:
            return self.distances_km[to_stop]
        else:
            return None

    def __eq__(self, other):
        return self.get_id() == other.get_id()

    def __str__(self):
        return "%s (%s)" % (self.get_id(), self.get_station())

    def __hash__(self):
        return hash(self.get_id())

    def __lt__(self, other):
        return self.get_id() < other.get_id()
