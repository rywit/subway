from Subway.Segment import RideSegment


class SubwayTrip:

    def __init__(self, route, service_id, trip_id, trip_headsign, direction_id):
        self.route = route
        self.service_id = service_id
        self.trip_id = trip_id
        self.trip_headsign = trip_headsign
        self.direction_id = direction_id
        self.stop_times = []
        self.segments = []

    def get_route(self):
        return self.route

    def get_service_id(self):
        return self.service_id

    def get_trip_id(self):
        return self.trip_id

    def get_trip_headsign(self):
        return self.trip_headsign

    def get_direction_id(self):
        return self.direction_id

    def add_stop_time(self, stop_time):
        self.stop_times.append(stop_time)

        if len(self.stop_times) > 1:
            from_stop_time = self.stop_times[-2]
            to_stop_time = self.stop_times[-1]

            segment = RideSegment(from_stop_time.get_stop(), to_stop_time.get_stop(),
                                  from_stop_time.get_departure_ts(), to_stop_time.get_arrival_ts(), self)

            self.segments.append(segment)

        return self

    def get_stop_times(self):
        return self.stop_times

    def get_segments(self):
        return self.segments

    def get_segment(self, from_stop):
        for segment in self.segments:
            if segment.get_from_stop() == from_stop:
                return segment

    def __str__(self):
        return "%s (%s) - %s" % (self.get_route(), self.get_trip_headsign(), self.get_trip_id())

    def __eq__(self, other):
        return self.get_trip_id() == other.get_trip_id()
