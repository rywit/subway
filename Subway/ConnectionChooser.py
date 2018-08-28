from Subway.Segment import *
from Subway.Transfer import *
from Subway.StopConnection import *
import random


class ConnectionChooser:

    def __init__(self):
        self.ride = None

    def init_ride(self, ride):
        self.ride = ride

    def get_ride(self):
        return self.ride

    def is_complete(self):
        return self.get_ride().is_complete()

    def iterate(self):
        connection = self.choose_connection()
        self.get_ride().add_segment(connection)
        return connection

    @staticmethod
    def build_ending(stop):
        return EndingConnection(stop)


class RandomConnectionChooser(ConnectionChooser):

    @staticmethod
    def get_random_segment(segments):

        if len(segments) == 1:
            return segments[0]

        rand = random.randint(0, len(segments) - 1)
        return segments[rand]


class UniqueConnectionChooser(RandomConnectionChooser):

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
        connections = ride.get_current_stop().get_connections()

        # Filter for valid destinations
        available = [seg for seg in connections if seg.get_to_station() in valid_stations]

        # Filter for those rides that go to a new station
        return [seg for seg in available if seg.get_to_station() not in visited_stations]

    def get_available_transfers(self, ride):

        # Stations we can go to
        valid_stations = self.get_station_set()

        cur_stop = ride.get_current_stop()
        visited_stations = ride.get_stations()

        stop_transfers = cur_stop.get_stop_transfers()

        # Filter for valid destinations
        available = [seg for seg in cur_stop.get_station_transfers() if seg.get_to_station() in valid_stations]

        # Filter for those transfers that go to a new station
        station_transfers = [seg for seg in available if seg.get_to_station() not in visited_stations]

        return stop_transfers, station_transfers

    @staticmethod
    def build_random_segment(segments):

        # Randomly pick one of the available segments
        seg = RandomConnectionChooser.get_random_segment(segments)

        if isinstance(seg, Transfer):
            return TransferConnection(seg.get_from_stop(), seg.get_to_stop())
        elif isinstance(seg, StopConnection):
            return RideConnection(seg.get_from_stop(), seg.get_to_stop(), seg.get_route())

    def choose_connection(self):

        ride = self.get_ride()

        cur_stop = ride.get_current_stop()

        # Get available rides from the current stop
        rides = self.get_available_rides(ride)

        # Get available transfers from the current stop
        stop_transfers, station_transfers = self.get_available_transfers(ride)

        # If we just transferred, ride or end
        if ride.just_transferred():
            if len(rides) == 0:
                return ConnectionChooser.build_ending(cur_stop)
            else:
                return UniqueConnectionChooser.build_random_segment(rides)

        # If there are no rides left, try to transfer
        if len(rides) == 0:
            if len(station_transfers) > 0:
                return UniqueConnectionChooser.build_random_segment(station_transfers)
            elif len(stop_transfers) > 0:
                return UniqueConnectionChooser.build_random_segment(stop_transfers)
            else:
                return ConnectionChooser.build_ending(cur_stop)

        # Randomly ride or transfer
        return UniqueConnectionChooser.build_random_segment(rides + station_transfers)


class VisitAllConnectionChooser(RandomConnectionChooser):

    MAX_DIST = 500

    def __init__(self, valid_stations, to_visit):
        super().__init__()
        self.valid_stations = valid_stations
        self.to_visit = to_visit

    def get_valid_stations(self):
        return self.valid_stations

    def get_stations_to_visit(self):
        return self.to_visit

    @staticmethod
    def get_unvisited_distance(station, unvisited):
        return min([station.get_distance(v) for v in unvisited])


    @staticmethod
    def get_available_rides(ride, unvisited):

        # Get available connections
        connections = ride.get_current_stop().get_connections()

        min_segs = set()
        min_dist = VisitAllConnectionChooser.MAX_DIST

        for seg in connections:
            to_station = seg.get_to_station()

            dist = VisitAllConnectionChooser.get_unvisited_distance(to_station, unvisited)

            if dist == min_dist:
                min_segs.add(seg)
            elif dist < min_dist:
                min_dist = dist
                min_segs = {seg}

        return list(min_segs), min_dist

    @staticmethod
    def get_available_stop_transfers(ride, unvisited):

        cur_stop = ride.get_current_stop()

        transfers = cur_stop.get_stop_transfers()

        min_segs = set()
        min_dist = VisitAllConnectionChooser.MAX_DIST

        for seg in transfers:
            to_station = seg.get_to_station()

            dist = VisitAllConnectionChooser.get_unvisited_distance(to_station, unvisited)

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
        transfers = cur_stop.get_station_transfers()

        min_segs = set()
        min_dist = VisitAllConnectionChooser.MAX_DIST

        for seg in transfers:
            to_station = seg.get_to_station()

            dist = VisitAllConnectionChooser.get_unvisited_distance(to_station, unvisited)

            if dist == min_dist:
                min_segs.add(seg)
            elif dist < min_dist:
                min_dist = dist
                min_segs = {seg}

        return list(min_segs), min_dist

    @staticmethod
    def build_random_segment(segments):

        # Randomly pick one of the available segments
        seg = RandomConnectionChooser.get_random_segment(segments)

        if isinstance(seg, Transfer):
            return TransferConnection(seg.get_from_stop(), seg.get_to_stop())
        elif isinstance(seg, StopConnection):
            return RideConnection(seg.get_from_stop(), seg.get_to_stop(), seg.get_route())

    def choose_connection(self):

        ride = self.get_ride()

        to_visit = self.get_stations_to_visit()
        visited_stations = ride.get_stations() & to_visit
        unvisited = to_visit - visited_stations

        cur_stop = ride.get_current_stop()

        if ride.get_length() > 1000:
            print("We're stuck")

        # We've visited every station in our list
        if len(unvisited) == 0:
            return ConnectionChooser.build_ending(cur_stop)

        # Get available rides from the current stop
        rides, ride_dist = self.get_available_rides(ride, unvisited)

        # Get available transfers from the current stop
        stop_transfers, stop_transfer_dist = self.get_available_stop_transfers(ride, unvisited)

        # Get available station transfers
        station_transfers, station_transfer_dist = self.get_available_station_transfers(ride, unvisited)

        min_dist = min([ride_dist, stop_transfer_dist, station_transfer_dist])

        options = []

        if ride_dist == min_dist:
            options.extend(rides)

        if stop_transfer_dist == min_dist:
            options.extend(stop_transfers)

        if station_transfer_dist == min_dist:
            options.extend(station_transfers)

        return self.build_random_segment(options)
