from Subway.Segments import *
import random


class LinkChooser:

    def __init__(self):
        self.ride = None

    def init_ride(self, ride):
        self.ride = ride

    def get_ride(self):
        return self.ride

    def is_complete(self):
        return self.get_ride().is_complete()

    def iterate(self):
        segment = self.choose_segment()
        self.get_ride().add_segment(segment)
        return segment


class RandomLinkChooser(LinkChooser):

    @staticmethod
    def get_random_segment(segments):

        if len(segments) == 1:
            return segments[0]

        rand = random.randint(0, len(segments) - 1)
        return segments[rand]


class UniqueLinkChooser(RandomLinkChooser):

    def __init__(self, station_set):
        super().__init__()
        self.station_set = station_set

    def get_station_set(self):
        return self.station_set

    def get_available_rides(self, ride):

        # Stations we've already been to on this trip
        visited_stations = ride.get_stations()

        # Stations we can go to
        valid_stations = self.get_station_set()

        # Get available connections
        ride_segments = ride.get_current_stop().get_ride_segments()

        # Filter for valid destinations
        available = [seg for seg in ride_segments if seg.get_to_station() in valid_stations]

        # Filter for those rides that go to a new station
        return [seg for seg in available if seg.get_to_station() not in visited_stations]

    def get_available_station_transfers(self, ride):

        # Stations we can go to
        valid_stations = self.get_station_set()

        cur_stop = ride.get_current_stop()
        visited_stations = ride.get_stations()

        station_transfers = cur_stop.get_station_transfer_segments()

        # Filter for valid destinations
        available = [seg for seg in station_transfers if seg.get_to_station() in valid_stations]

        # Filter for those transfers that go to a new station
        return [seg for seg in available if seg.get_to_station() not in visited_stations]

    def choose_segment(self):

        ride = self.get_ride()

        cur_stop = ride.get_current_stop()

        # Get available rides from the current stop
        rides = self.get_available_rides(ride)

        # Get available stop transfers
        stop_transfers = cur_stop.get_stop_transfer_segments()

        # Get available transfers from the current stop
        station_transfers = self.get_available_station_transfers(ride)

        # If we just transferred, ride or end
        if ride.just_transferred():
            if len(rides) == 0:
                return EndingSegment(cur_stop)
            else:
                return self.get_random_segment(rides)

        # If there are no rides left, try to transfer
        if len(rides) == 0:
            if len(station_transfers) > 0:
                return self.get_random_segment(station_transfers)
            elif len(stop_transfers) > 0:
                return self.get_random_segment(stop_transfers)
            else:
                return EndingSegment(cur_stop)

        # Randomly ride or transfer
        return self.get_random_segment(rides + station_transfers)


class VisitAllLinkChooser(RandomLinkChooser):

    MAX_DIST = 500

    def __init__(self, station_set):
        super().__init__()
        self.station_set = station_set

    def get_station_set(self):
        return self.station_set

    @staticmethod
    def get_unvisited_distance(station, unvisited):
        return min([station.get_distance(v) for v in unvisited])

    @staticmethod
    def get_available_rides(ride, unvisited):

        # Get available connections
        rides = ride.get_current_stop().get_ride_segments()

        min_segs = set()
        min_dist = VisitAllLinkChooser.MAX_DIST

        for seg in rides:
            to_station = seg.get_to_station()

            dist = VisitAllLinkChooser.get_unvisited_distance(to_station, unvisited)

            if dist == min_dist:
                min_segs.add(seg)
            elif dist < min_dist:
                min_dist = dist
                min_segs = {seg}

        return list(min_segs), min_dist

    @staticmethod
    def get_available_station_transfers(ride, unvisited):

        cur_stop = ride.get_current_stop()

        # Filter for valid destinations
        transfers = cur_stop.get_station_transfer_segments()

        min_segs = set()
        min_dist = VisitAllLinkChooser.MAX_DIST

        for seg in transfers:
            to_station = seg.get_to_station()

            dist = VisitAllLinkChooser.get_unvisited_distance(to_station, unvisited)

            if dist == min_dist:
                min_segs.add(seg)
            elif dist < min_dist:
                min_dist = dist
                min_segs = {seg}

        return list(min_segs), min_dist

    def choose_segment(self):

        ride = self.get_ride()

        to_visit = self.get_stations_to_visit()
        visited_stations = ride.get_stations() & to_visit
        unvisited = to_visit - visited_stations

        cur_stop = ride.get_current_stop()

        if ride.get_length() > 1000:
            print("We're stuck")

        # We've visited every station in our list
        if len(unvisited) == 0:
            return EndingSegment(cur_stop)

        # Get available rides from the current stop
        rides, ride_dist = self.get_available_rides(ride, unvisited)

        # Get available transfers from the current stop
        stop_transfers = cur_stop.get_stop_transfer_segments()

        # Get available station transfers
        station_transfers, station_transfer_dist = self.get_available_station_transfers(ride, unvisited)

        min_dist = min([ride_dist, station_transfer_dist])

        options = []

        if ride_dist == min_dist:
            options.extend(rides)

        if station_transfer_dist == min_dist:
            options.extend(station_transfers)

        if len(options) > 0:
            return self.get_random_segment(options)
        else:
            return self.get_random_segment(stop_transfers)
