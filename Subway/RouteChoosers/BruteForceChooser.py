from Subway.SubwayRide import *


class BruteForceChooser:

    def __init__(self, to_visit):
        self.to_visit = to_visit

    def get_to_visit(self):
        return self.to_visit


class LongestPathChooser:

    NUM_RUNS = 0

    @staticmethod
    def get_route(starting_stop):

        print("Finding longest route from %s" % starting_stop)
        ride = SubwayRide(StartingSegment(starting_stop))

        return LongestPathChooser.get_longest_path(ride)

    @staticmethod
    def get_available_segments(ride):

        visited = ride.get_visited_stations()
        cur_stop = ride.get_current_stop()

        rides = [seg for seg in cur_stop.get_ride_segments() if seg.get_to_station() not in visited]
        station_trans = [seg for seg in cur_stop.get_station_transfer_segments() if seg.get_to_station() not in visited]
        stop_trans = cur_stop.get_stop_transfer_segments()

        return rides, station_trans, stop_trans

    @staticmethod
    def get_longest_path(ride):

        rides, station_trans, stop_trans = LongestPathChooser.get_available_segments(ride)

        # Keep riding if its our only option
        while len(rides) == 1 and ride.get_current_station().is_passthrough():
            ride.add_segment(rides[0])
            rides, station_trans, stop_trans = LongestPathChooser.get_available_segments(ride)

        available = rides

        if not ride.just_transferred() and not ride.is_beginning():
            available += station_trans
            available += stop_trans

        # If we can't go anywhere
        if len(available) == 0:
            LongestPathChooser.NUM_RUNS += 1

            if LongestPathChooser.NUM_RUNS % 25000 == 0:
                print("Run %d" % LongestPathChooser.NUM_RUNS )

            return ride.add_segment(EndingSegment(ride.get_current_stop()))

        lengths = []

        for seg in available:
            new_ride = ride.clone()
            new_ride.add_segment(seg)

            longest = LongestPathChooser.get_longest_path(new_ride)
            lengths.append(longest)

        # Sort by ride length
        lengths.sort(key=lambda x: x.get_num_stations(), reverse=True)

        return lengths[0]
