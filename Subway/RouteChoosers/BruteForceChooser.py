from Subway.Segments import *


class BruteForceChooser:

    def __init__(self, to_visit):
        self.to_visit = to_visit

    def get_to_visit(self):
        return self.to_visit


class AllStationChooser(BruteForceChooser):

    def __init__(self, to_visit):
        super().__init__(to_visit)

    def