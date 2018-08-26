from Subway.Segment import *
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

    @staticmethod
    def __get_available_rides(ride):

        # Get available connections
        connections = ride.get_current_stop().get_connections()

        # Filter for those rides that go to a new station
        available = [seg for seg in connections if seg.get_to_station() not in ride.get_stations()]

        return [RideConnection(x.get_from_stop(), x.get_to_stop(), x.get_route()) for x in available]

    @staticmethod
    def __get_available_transfers(ride):

        cur_stop = ride.get_current_stop()
        visited_stations = ride.get_stations()

        stop_transfers = []
        station_transfers = []

        # Iterate through each available transfer
        for transfer in cur_stop.get_station().get_transfers():

            # Go through each available stop at this station
            for to_stop in transfer.get_to_station().get_stops():

                # Do not "transfer" to your current stop
                if to_stop == cur_stop:
                    continue

                to_station = to_stop.get_station()

                if cur_stop.get_station() == to_station:
                    stop_transfers.append(TransferConnection(cur_stop, to_stop))
                elif to_station not in visited_stations:
                    station_transfers.append(TransferConnection(cur_stop, to_stop))

        return stop_transfers, station_transfers

    def choose_connection(self):

        ride = self.get_ride()

        cur_stop = ride.get_current_stop()

        # Get available rides from the current stop
        rides = UniqueConnectionChooser.__get_available_rides(ride)

        # Get available transfers from the current stop
        stop_transfers, station_transfers = UniqueConnectionChooser.__get_available_transfers(ride)

        # If we just transferred, ride or end
        if ride.just_transferred():
            if len(rides) == 0:
                return ConnectionChooser.build_ending(cur_stop)
            else:
                return UniqueConnectionChooser.get_random_segment(rides)

        # If there are no rides left, try to transfer
        if len(rides) == 0:
            if len(station_transfers) > 0:
                return UniqueConnectionChooser.get_random_segment(station_transfers)
            elif len(stop_transfers) > 0:
                return UniqueConnectionChooser.get_random_segment(stop_transfers)
            else:
                return ConnectionChooser.build_ending(cur_stop)

        # Randomly ride or transfer
        return UniqueConnectionChooser.get_random_segment(rides + station_transfers)


class AllStationChooser(RandomConnectionChooser):

    def __init__(self, stations_to_visit):
        super().__init__()
        self.stations_to_visit = stations_to_visit

        print("Initialized AllStationChooser with %d stations" % len(stations_to_visit))

    def get_stations_to_visit(self):
        return self.stations_to_visit

    @staticmethod
    def __get_available_rides(ride, to_visit):

        # Get available connections
        connections = ride.get_current_stop().get_connections()

        new_rides = []
        old_rides = []

        for seg in connections:

            # Build a new connection
            connection = RideConnection(seg.get_from_stop(), seg.get_to_stop(), seg.get_route())

            if seg.get_to_station() in to_visit:
                new_rides.append(connection)
            else:
                old_rides.append(connection)

        return new_rides, old_rides

    @staticmethod
    def __get_available_transfers(ride):

        cur_stop = ride.get_current_stop()

        stop_transfers = []
        station_transfers = []

        # Iterate through each available transfer
        for transfer in cur_stop.get_station().get_transfers():

            # Go through each available stop at this station
            for to_stop in transfer.get_to_station().get_stops():

                # Do not "transfer" to your current stop
                if to_stop == cur_stop:
                    continue

                to_station = to_stop.get_station()

                if cur_stop.get_station() == to_station:
                    stop_transfers.append(TransferConnection(cur_stop, to_stop))
                elif len(to_stop.get_connections()) > 0:
                    station_transfers.append(TransferConnection(cur_stop, to_stop))

        return stop_transfers, station_transfers

    def choose_connection(self):

        ride = self.get_ride()
        cur_stop = ride.get_current_stop()
        to_visit = self.get_stations_to_visit()

        # How many stations have we visited in our list?
        matches = [x for x in ride.get_stations() if x in to_visit]

        # If we've visited every station, we're done
        if len(matches) == len(to_visit):
            return ConnectionChooser.build_ending(cur_stop)

        # Get available rides from the current stop
        new_rides, old_rides = AllStationChooser.__get_available_rides(ride, to_visit)

        # Get available transfers from the current stop
        stop_transfers, station_transfers = AllStationChooser.__get_available_transfers(ride)

        # If we just transferred, ride or end
        if ride.just_transferred():
            if len(new_rides) > 0:
                return UniqueConnectionChooser.get_random_segment(new_rides)
            else:
                return RandomConnectionChooser.build_ending(cur_stop)

        # If there are no rides left, try to transfer
        if len(new_rides) == 0 and len(old_rides) == 0:
            if len(station_transfers) > 0:
                return UniqueConnectionChooser.get_random_segment(station_transfers)
            elif len(stop_transfers) > 0:
                return UniqueConnectionChooser.get_random_segment(stop_transfers)
            else:
                return RandomConnectionChooser.build_ending(cur_stop)

        # Randomly ride or transfer
        if len(new_rides) > 0:
            return UniqueConnectionChooser.get_random_segment(new_rides + station_transfers)

