from Subway.SubwayRide import *


class BruteForceChooser:

    def __init__(self, to_visit):
        self.to_visit = to_visit

    def get_to_visit(self):
        return self.to_visit


class LongestPathChooser:

    @staticmethod
    def get_route(starting_stop):

        ride = SubwayRide(StartingSegment(starting_stop))

        return LongestPathChooser.get_longest_path(ride)

    @staticmethod
    def get_longest_path(ride):

        visited = ride.get_visited_stations()
        cur_stop = ride.get_current_stop()

        rides = [seg for seg in cur_stop.get_ride_segments() if seg.get_to_station() not in visited]
        station_trans = [seg for seg in cur_stop.get_station_transfer_segments() if seg.get_to_station() not in visited]
        stop_trans = cur_stop.get_stop_transfer_segments()

        available = rides

        if not ride.just_transferred():
            available += station_trans
            available += stop_trans

        # If we can't go anywhere
        if len(available) == 0:
            print("Ended ride: %d" % ride.get_num_stations())
            return ride.add_segment(EndingSegment(cur_stop))

        lengths = []

        for seg in available:
            new_ride = ride.clone()
            new_ride.add_segment(seg)

            longest = LongestPathChooser.get_longest_path(new_ride)
            lengths.append(longest)

        # Sort by ride length
        lengths.sort(key=lambda x: x.get_num_stations(), reverse=True)

        return lengths[0]
