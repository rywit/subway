from Subway import *
import random


def run_simulation(ride, chooser):

    chooser.init_ride(ride)

    while not chooser.is_complete():
        chooser.iterate()

    return chooser.get_ride()


def get_children(ride):
    ride_len = ride.get_length()

    if ride_len == 1:
        return ride
    else:
        return [ride.get_subset(x) for x in range(1, ride_len)]


def run_evolution(ride, chooser):

    children = get_children(ride)

    longest_ride = ride

    for child in children:

        # Run 100 simulations for this child
        runs = [run_simulation(child, chooser) for x in range(250)]

        # Sort in descending order of distinct stations
        runs.sort(key=lambda x: x.get_num_stations(), reverse=True)

        if runs[0].get_num_stations() > longest_ride.get_num_stations():
            longest_ride = runs[0]

    return longest_ride


def run_test(stop, chooser):

    ride = SubwayRide(StartingConnection(stop))

    # Seed our simulation
    longest_ride = run_simulation(ride, chooser)

    lengths = [longest_ride.get_num_stations()]

    # Run 10 evolutions
    for i in range(20):
        longest_ride = run_evolution(longest_ride, chooser)
        lengths.append(longest_ride.get_num_stations())

    # Keep running if the length increases
    while lengths[-1] > lengths[-11]:
        longest_ride = run_evolution(longest_ride, chooser)
        lengths.append(longest_ride.get_num_stations())

    print("Length: %d" % longest_ride.get_num_stations())

    return longest_ride


def get_valid_stations(stops):

    brooklyn_stations = set()

    for stop in stops:
        if stop.get_station().get_structure() == "Open Cut":
            brooklyn_stations.add(stop.get_station())

    return brooklyn_stations


def get_random_stop(stations):
    stops = []

    for station in stations:
        for stop in station.get_stops():
            stops.append(stop)

    return stops[random.randint(0, len(stops) - 1)]


def main():

    # Load the data from disk
    loader = DataLoader("data")

    # Get the list of all subway stops
    all_stops = loader.get_stops().values()

    # pull out Brooklyn stops
    valid_stations = get_valid_stations(all_stops)

    # Get a random starting stop
    starting_stop = get_random_stop(valid_stations)
    print("Starting at %s" % starting_stop)

    # Build a route chooser
    chooser = UniqueConnectionChooser(valid_stations)

    # Run one simulation
    longest_ride = None

    # Run more
    for station in valid_stations:
        for starting_stop in station.get_stops():
            print("Running test from %s" % starting_stop)
            longest = run_test(starting_stop, chooser)

            if longest_ride is None or longest.get_num_stations() > longest_ride.get_num_stations():
                longest_ride = longest

    print("\nSummary:\n")
    print("\n".join(map(str, longest_ride.get_segments())))

    print("\nDistinct Stations: %d of %d" % (longest_ride.get_num_stations(), len(valid_stations)))


if __name__ == "__main__":
    main()
