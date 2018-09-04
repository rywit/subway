from Subway.Segments import *

import random


class TripChooser:

    def __init__(self, timetable=None):
        self.timetable = timetable

    def get_time_table(self):
        return self.timetable

    @staticmethod
    def is_continuation(ride, segment):
        return segment.get_direction_id() == ride.get_current_direction_id() and segment.get_route() == ride.get_current_route()


class JustRide(TripChooser):
    """ Just ride in one direction on the same line until the trip ends """

    def __init__(self, timetable):
        super().__init__(timetable)

    def choose_segment(self, ride):

        cur_stop = ride.get_current_stop()
        time_ts = ride.get_current_time_ts()

        rides, transfers = self.get_time_table().get_available_segments(cur_stop, time_ts)

        # If there is nowhere to ride, then our trip is over
        if len(rides) == 0:
            return EndingSegment(cur_stop)

        # If we are at the start, just start riding the first train
        if ride.is_beginning():
            return rides[0]

        # Otherwise keep going in the same direction on the same route
        for segment in rides:

            if JustRide.is_continuation(ride, segment):
                return segment

        # We have nowhere left to ride
        return EndingSegment(cur_stop)


class YoyoRide(TripChooser):
    """ Just keep riding back and forth on the same line """

    def __init__(self, timetable, max_len):
        super().__init__(timetable)
        self.max_len = max_len

    def get_max_length(self):
        return self.max_len

    def choose_segment(self, ride):

        cur_stop = ride.get_current_stop()
        time_ts = ride.get_current_time_ts()

        if ride.get_num_rides() >= self.get_max_length():
            return EndingSegment(cur_stop, time_ts)

        rides, transfers = self.get_time_table().get_available_segments(cur_stop, time_ts)

        # If there is nowhere to ride, then transfer
        if len(rides) == 0:
            return transfers[0]

        # If we are at the start, just start riding the first train
        if ride.is_beginning():
            return rides[0]

        # Otherwise keep going in the same direction on the same route
        for segment in rides:

            # If we just transferred, then start riding
            if ride.just_transferred():
                return segment

            # Keep riding in the same direction
            if YoyoRide.is_continuation(ride, segment):
                return segment

        # We have nowhere left to ride
        return EndingSegment(cur_stop, time_ts)


class RandomRide(TripChooser):
    """ Just keep riding back and forth on the same line """

    def __init__(self, timetable=None, max_len=3600):
        super().__init__(timetable)
        self.max_len = max_len

    def get_max_length(self):
        return self.max_len

    @staticmethod
    def get_random_segment(segments):

        if len(segments) == 1:
            return segments[0]

        rand = random.randint(0, len(segments) - 1)
        return segments[rand]

    @staticmethod
    def get_station_transfers(transfers):
        return list(filter(lambda x: x.is_station_transfer(), transfers))

    def choose_segment(self, ride):

        cur_stop = ride.get_current_stop()
        time_ts = ride.get_current_time_ts()

        if ride.get_num_rides() >= self.get_max_length():
            return EndingSegment(cur_stop, time_ts)

        # Don't wait more than 30 minutes for a transfer
        max_wait = 30 * 60

        rides, transfers = self.get_time_table().get_available_segments(cur_stop, time_ts, max_wait)

        # If there are no rides available (i.e. end of line), transfer
        if len(rides) == 0:
            return RandomRide.get_random_segment(transfers)

        # If we are just beginning or just transferred, start riding
        if ride.is_beginning() or ride.just_transferred():
            return RandomRide.get_random_segment(rides)

        # Pull out those transfers between stations
        station_transfers = RandomRide.get_station_transfers(transfers)

        # Randomly ride or transfer
        return RandomRide.get_random_segment(rides + station_transfers)


class UniqueRide(RandomRide):

    def __init__(self, timetable, max_len):
        super().__init__(timetable, max_len)

    @staticmethod
    def get_available_segments(timetable, ride):
        cur_stop = ride.get_current_stop()
        time_ts = ride.get_current_time_ts()

        rides, all_transfers = timetable.get_available_segments(cur_stop, time_ts, 30 * 60)

        # Filter for those rides that go to a new station
        available_rides = [seg for seg in rides if seg.get_to_station() not in ride.get_stations()]
        stop_transfers = [seg for seg in all_transfers if seg.get_from_station() == seg.get_to_station()]
        station_transfers = [seg for seg in all_transfers if seg.get_to_station() not in ride.get_stations()]

        return available_rides, stop_transfers, station_transfers

    def choose_segment(self, ride):

        cur_stop = ride.get_current_stop()
        time_ts = ride.get_current_time_ts()

        if ride.get_num_rides() >= self.get_max_length():
            return EndingSegment(cur_stop, time_ts)

        rides, stop_transfers, station_transfers = UniqueRide.get_available_segments(self.get_time_table(), ride)

        # If we just transferred, ride or end
        if ride.just_transferred():
            if len(rides) == 0:
                return EndingSegment(cur_stop, time_ts)
            else:
                return UniqueRide.get_random_segment(rides)

        # If there are no rides left, try to transfer
        if len(rides) == 0:
            if len(station_transfers) > 0:
                return UniqueRide.get_random_segment(station_transfers)
            elif len(stop_transfers) > 0:
                return UniqueRide.get_random_segment(stop_transfers)
            else:
                return EndingSegment(cur_stop, time_ts)

        # Randomly ride or transfer
        return UniqueRide.get_random_segment(rides + station_transfers)


