from Subway import *
from Subway.RouteChoosers import *
import random


def main():

    # Load the data from disk
    system = SubwayLinkSystem("data")

    starting_stop = random.sample(system.get_stops(), 1)[0]

    longest = LongestPathChooser.get_route(starting_stop)

    print(longest.get_ride_summary())


if __name__ == "__main__":
    main()