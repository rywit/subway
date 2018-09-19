from Subway.Segments.Segment import *
from Subway.Utils import DistanceType


class SubwayRide:

    def __init__(self, segments=None, stations=None):
        if segments is None:
            self.segments = []
        elif isinstance(segments, Segment):
            self.segments = [segments]
        else:
            self.segments = segments.copy()

        if stations is None:
            self.stations = set()

            for seg in self.segments:
                self.stations.add(seg.get_from_station())
                self.stations.add(seg.get_to_station())
        else:
            self.stations = stations.copy()

    def clone(self):
        return SubwayRide(self.get_segments(), self.get_visited_stations())

    def get_segments(self):
        return self.segments

    def get_visited_stations(self, to_visit=None):

        if to_visit is None:
            return self.stations
        else:
            return set([station for station in self.stations if station in to_visit])

    def get_num_visited_stations(self, to_visit=None):
        return len(self.get_visited_stations(to_visit))

    def get_subset(self, n):
        segments = self.get_segments()[:n]
        return SubwayRide(segments)

    def get_ride_segments(self):
        return [seg for seg in self.get_segments() if isinstance(seg, RideSegment)]

    def get_transfer_segments(self):
        return [seg for seg in self.get_segments() if isinstance(seg, TransferSegment)]

    def get_station_transfer_segments(self):
        return [seg for seg in self.get_segments() if isinstance(seg, StationTransferSegment)]

    def get_stop_transfer_segments(self):
        return [seg for seg in self.get_segments() if isinstance(seg, StopTransferSegment)]

    def add_segment(self, segment):
        self.segments.append(segment)
        self.stations.add(segment.get_from_station())
        self.stations.add(segment.get_to_station())
        return self

    def get_first_segment(self):
        return self.get_segments()[0]

    def get_last_segment(self):
        return self.get_segments()[-1]

    def get_current_stop(self):
        return self.get_last_segment().get_to_stop()

    def get_current_station(self):
        return self.get_last_segment().get_to_station()

    def is_beginning(self):
        return isinstance(self.get_last_segment(), StartingSegment)

    def is_complete(self):
        return isinstance(self.get_last_segment(), EndingSegment)

    def just_transferred(self):
        return isinstance(self.get_last_segment(), TransferSegment)

    def get_length(self):
        return len(self.get_segments())

    def get_distance_rides(self):
        return sum([seg.get_num_stops() for seg in self.get_ride_segments()])

    def get_distance_station_transfers(self):
        return sum([seg.get_num_stops() for seg in self.get_station_transfer_segments()])

    def get_distance_stop_transfers(self):
        return sum([seg.get_num_stops() for seg in self.get_stop_transfer_segments()])

    def get_distance_transfers(self):
        return self.get_distance_station_transfers() + self.get_distance_stop_transfers()

    def get_distance_segments(self):
        return self.get_distance_rides() + self.get_distance_station_transfers()

    def get_distance_km(self):
        return sum([seg.get_distance_km() for seg in self.get_ride_segments()])

    def get_ride_summary(self):
        return "\n".join([
            "Start: %s" % self.get_first_segment().get_from_station(),
            "End: %s" % self.get_last_segment().get_to_station(),
            "Segments: %d" % self.get_distance_segments(),
            "Rides: %d" % self.get_distance_rides(),
            "Station Transfers: %d" % self.get_distance_station_transfers(),
            "Stop Transfers: %d" % self.get_distance_stop_transfers(),
            "Stations Visited: %d" % self.get_num_visited_stations(),
            "Distance: %.2f km" % self.get_distance_km()])

    def simplify_ride(self):

        segments = self.get_segments()

        for i in reversed(range(len(segments)-1)):
            segment1 = segments[i]
            segment2 = segments[i+1]

            both_rides = isinstance(segment1, RideSegment) and isinstance(segment2, RideSegment)
            both_transfers = isinstance(segment1, TransferSegment) and isinstance(segment2, TransferSegment)

            if both_rides or both_transfers:
                segments[i] = segment1.merge(segment2)
                del segments[i+1]

    def print(self):
        return "\n".join(map(str, self.get_segments()))

    @staticmethod
    def build_ride_from_links(stations, method=DistanceType.Segments):
        segments = []

        # Build basic ride segments
        for from_station, to_station in zip(stations, stations[1:]):

            path = from_station.get_path(method, to_station)

            for from_station2, to_station2 in zip(path, path[1:]):
                segments.append(from_station2.get_segment_to_station(to_station2))

        # Fill in stop transfers
        for i in range(len(segments)-1, 2, -1):
            seg1 = segments[i-1]
            seg2 = segments[i]

            if isinstance(seg1, RideSegment) and isinstance(seg2, RideSegment):
                if seg1.get_to_stop() != seg2.get_from_stop():
                    stop_trans = StopTransferSegment(seg1.get_to_stop(), seg2.get_from_stop())
                    segments.insert(i, stop_trans)

        starting_stop = segments[0].get_from_stop()
        segments.insert(0, StartingSegment(starting_stop))

        ending_stop = segments[-1].get_to_stop()
        segments.append(EndingSegment(ending_stop))

        return SubwayRide(segments=segments)


