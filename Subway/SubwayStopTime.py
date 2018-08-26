import re


class SubwayStopTime:

    p = re.compile("(\d\d):(\d\d):(\d\d)")

    def __init__(self, trip, arrival_time, departure_time, stop, stop_sequence):
        self.trip = trip
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.stop = stop
        self.stop_sequence = stop_sequence

        m1 = self.p.match(arrival_time).groups()
        self.arrival_ts = int(m1[0]) * 3600 + int(m1[1]) * 60 + int(m1[2])

        m2 = self.p.match(departure_time).groups()
        self.departure_ts = int(m2[0]) * 3600 + int(m2[1]) * 60 + int(m2[2])

    def get_trip(self):
        return self.trip

    def get_arrival_time(self):
        return self.arrival_time

    def get_departure_time(self):
        return self.departure_time

    def get_arrival_ts(self):
        return self.arrival_ts

    def get_departure_ts(self):
        return self.departure_ts

    def get_stop(self):
        return self.stop

    def get_station(self):
        return self.get_stop().get_station()

    def get_stop_sequence(self):
        return self.stop_sequence
