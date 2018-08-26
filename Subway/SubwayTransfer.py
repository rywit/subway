class SubwayTransfer:

    def __init__(self, from_station, to_station, transfer_type, min_transfer_time):
        self.from_station = from_station
        self.to_station = to_station
        self.transfer_type = transfer_type
        self.min_transfer_time = min_transfer_time

    def get_from_station(self):
        return self.from_station

    def get_to_station(self):
        return self.to_station

    def get_type(self):
        return self.transfer_type

    def get_min_time(self):
        return self.min_transfer_time
