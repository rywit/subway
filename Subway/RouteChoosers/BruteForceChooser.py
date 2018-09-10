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

        available = rides.copy()

        if not ride.just_transferred() and not ride.is_beginning():
            available += station_trans
            available += stop_trans

        # If we can't go anywhere
        if len(available) == 0:
            LongestPathChooser.NUM_RUNS += 1

            if LongestPathChooser.NUM_RUNS % 100000 == 0:
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


class ShortestPathChooser:

    def __init__(self, length_limit):
        super().__init__()
        self.length_limit = length_limit

    def reset_limit(self, limit):
        self.length_limit = limit

    def get_limit(self):
        return self.length_limit

    def get_route(self, starting_stop, to_visit):

        print("Finding shortest route from %s" % starting_stop)
        ride = SubwayRide(StartingSegment(starting_stop))

        return self.get_shortest_path(ride, to_visit)

    @staticmethod
    def distance_to_unvisited(cur_station, unvisited):
        return min([cur_station.get_distance_segments(station) for station in unvisited])

    @staticmethod
    def get_available_segments(ride, unvisited):

        cur_station = ride.get_current_station()
        cur_stop = ride.get_current_stop()
        segments = ride.get_segments()

        # Distance to closest unvisited station
        cur_dist = ShortestPathChooser.distance_to_unvisited(cur_station, unvisited)

        rides = []

        for ride in cur_stop.get_ride_segments():
            if ride not in segments:
                dist = ShortestPathChooser.distance_to_unvisited(ride.get_to_station(), unvisited)

                if dist < cur_dist:
                    rides.append(ride)

        station_trans = []

        for tran in cur_stop.get_station_transfer_segments():
            if tran not in segments:
                dist = ShortestPathChooser.distance_to_unvisited(tran.get_to_station(), unvisited)

                if dist < cur_dist:
                    station_trans.append(tran)

        stop_trans = cur_stop.get_stop_transfer_segments()

        return rides, station_trans, stop_trans

    def get_shortest_path(self, ride, to_visit):

        # We've exceeded our threshold
        if ride.get_length() > self.get_limit():
            return ride.add_segment(ErrorSegment(ride.get_current_stop()))

        # We've visited every station
        visited = ride.get_visited_stations()
        unvisited = to_visit - visited

        if len(unvisited) == 0:
            path_len = ride.get_length()
            print("Found path: %d" % path_len)

            if path_len < self.get_limit():
                self.reset_limit(path_len)

            return ride.add_segment(EndingSegment(ride.get_current_stop()))

        # Get available segments (ride, station transfer and stop transfer)
        rides, station_trans, stop_trans = self.get_available_segments(ride, unvisited)

        available = rides.copy()

        if not ride.just_transferred() and not ride.is_beginning():
            available.extend(station_trans)
            available.extend(stop_trans)

        # If we can't go anywhere
        if len(available) == 0:
            return ride.add_segment(ErrorSegment(ride.get_current_stop()))

        lengths = []

        for seg in available:
            new_ride = ride.clone()
            new_ride.add_segment(seg)

            longest = self.get_shortest_path(new_ride, to_visit)

            if longest is not None and not longest.is_error():
                lengths.append(longest)

        # Sort by ride length
        lengths.sort(key=lambda x: x.get_length())

        if len(lengths) == 0:
            return None
        else:
            return lengths[0]
