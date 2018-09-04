from Subway.Segments.Segment import *


class SubwayRide:

    def __init__(self, segments):
        if isinstance(segments, Segment):
            self.segments = [segments]
        else:
            self.segments = segments

        self.stations = set()

        for seg in self.segments:
            self.stations.add(seg.get_from_station())
            self.stations.add(seg.get_to_station())

    def get_segments(self):
        return self.segments

    def get_stations(self):
        return self.stations

    def get_subset(self, n):
        segments = self.get_segments()[:n]
        return SubwayRide(segments)

    def get_ride_segments(self):
        return [seg for seg in self.get_segments() if isinstance(seg, RideSegment)]

    def get_transfer_segments(self):
        return [seg for seg in self.get_segments() if isinstance(seg, TransferSegment)]

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

    def get_current_time_ts(self):
        return self.get_last_segment().get_stop_time_ts()

    def get_current_route(self):
        return self.get_last_segment().get_route()

    def get_current_direction_id(self):
        return self.get_last_segment().get_direction_id()

    def is_beginning(self):
        return isinstance(self.get_last_segment(), StartingSegment)

    def is_complete(self):
        return isinstance(self.get_last_segment(), EndingSegment)

    def just_transferred(self):
        return isinstance(self.get_last_segment(), TransferSegment)

    def get_length(self):
        return len(self.get_segments())

    def get_num_rides(self):
        return len(self.get_ride_segments())

    def get_num_transfers(self):
        return len(self.get_transfer_segments())

    def get_num_stations(self):
        return len(self.get_stations())

    def get_ride_distance_km(self):
        return sum([seg.get_distance_km() for seg in self.get_ride_segments()])

    def get_ride_summary(self):
        return "\n".join([
            "Start: %s" % self.get_first_segment().get_from_station(),
            "End: %s" % self.get_last_segment().get_to_station(),
            "Rides: %d" % self.get_num_rides(),
            "Transfers: %d" % self.get_num_transfers(),
            "Distance: %.2f km" % self.get_ride_distance_km()])

    def simplify_ride(self):

        segments = self.get_segments()

        for i in reversed(range(len(segments)-1)):
            segment1 = segments[i]
            segment2 = segments[i+1]

            if isinstance(segment1, TransferSegment) and isinstance(segment2, TransferSegment):
                segments[i] = segment1.merge(segment2)
                del segments[i+1]

    def get_summary_segments(self):

        summary = []
        cur_ride = None

        for seg in self.get_segments():
            if isinstance(seg, StartingSegment):
                summary.append(seg)
            elif isinstance(seg, EndingSegment):
                summary.append(cur_ride)
                summary.append(seg)
            elif isinstance(seg, RideSegment):
                if cur_ride is None:
                    cur_ride = seg
                elif cur_ride.get_trip() == seg.get_trip():
                    cur_ride = cur_ride.merge(seg)
                else:
                    summary.append(cur_ride)
                    cur_ride = seg
            elif isinstance(seg, TransferSegment):
                summary.append(cur_ride)
                summary.append(seg)
                cur_ride = None

        return summary
