class TimeTable:

    def __init__(self, trips):

        by_stop = {}

        # Iterate through each of the trips
        for trip in trips.values():

            # Iterate through each stop on the given trip
            for stop_time in trip.get_stop_times():

                # Get the station ID
                stop_id = stop_time.get_stop().get_id()

                # Add this trip to our mapping by station
                by_stop.setdefault(stop_id, []).append(trip)

        self.trips = trips
        self.by_stop = by_stop

    def __build_ride_segments(self, from_stop, time_ts, max_wait):

        stop_id = from_stop.get_id()

        # First look for upcoming trains at this station
        trips = self.by_stop.get(stop_id, [])

        routes = {}

        # Iterate through each trip stopping at this station
        for trip in trips:

            segment = trip.get_segment(from_stop)

            # The segment will be none if the stop is the end of the trip
            if segment is None:
                continue

            if segment.get_start_time_ts() >= time_ts:
                route_id = trip.get_route().get_id()

                # Add this segment to the set of segments for this route
                routes.setdefault(route_id, []).append(segment)

        next_departures = []

        # Go through the available segments for this route
        for segments in routes.values():

            # Sort the segments by starting time (ascending)
            segments.sort(key=lambda x: x.get_start_time_ts())

            # Get the waiting time until this departure
            next_departure = segments[0]
            wait_time = next_departure.get_start_time_ts() - time_ts

            if max_wait is None or wait_time <= max_wait:
                next_departures.append(next_departure)

        return next_departures

    @staticmethod
    def __build_transfer_segments(from_stop, time_ts):
        transfer_segments = []

        # Go through each available transfer from this station
        for transfer in from_stop.get_station().get_transfers():

            # Go through each available stop at this station
            for to_stop in transfer.get_to_station().get_stops():

                # Do not "transfer" to your current stop
                if to_stop.get_id() == from_stop.get_id():
                    continue

                transfer_time = transfer.get_min_time()

                # Build a new transfer segment
                transfer_segment = TransferTripSegment(from_stop, to_stop, time_ts, time_ts + transfer_time)

                # Add transfer segment to our list of available segments
                transfer_segments.append(transfer_segment)

        return transfer_segments

    def get_available_segments(self, from_stop, time_ts, max_wait=None):

        # Get upcoming rides from this stop
        ride_segments = self.__build_ride_segments(from_stop, time_ts, max_wait)

        # Get available transfers at this stop
        transfer_segments = TimeTable.__build_transfer_segments(from_stop, time_ts)

        # Return rides and transfers
        return ride_segments, transfer_segments
