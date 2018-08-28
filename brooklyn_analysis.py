from Subway import *


def run_simulation(ride, chooser):

    chooser.init_ride(ride)

    while not chooser.is_complete():
        chooser.iterate()

    return chooser.get_ride()


def get_children(ride, num_children):

    children = []

    for i in range(num_children):
        cut = random.randint(1, ride.get_length())
        children.append(ride.get_subset(cut))

    return children


def run_evolution(ride, chooser):

    children = get_children(ride, 25)

    shortest_ride = ride

    for child in children:
        child_ride = run_simulation(child, chooser)

        if child_ride.get_ride_length() < shortest_ride.get_ride_length():
            shortest_ride = child_ride

    return shortest_ride


def run_test(stop, chooser):

    ride = SubwayRide(StartingConnection(stop))

    # Seed our simulation
    shortest_ride = run_simulation(ride, chooser)

    lengths = [shortest_ride.get_length()]

    # Run 10 evolutions
    for i in range(12):
        shortest_ride = run_evolution(shortest_ride, chooser)
        lengths.append(shortest_ride.get_ride_length())

    # Keep running if the length increases
    while lengths[-1] < lengths[-6]:
        shortest_ride = run_evolution(shortest_ride, chooser)
        lengths.append(shortest_ride.get_length())

    print("Length: %d" % shortest_ride.get_length())

    return shortest_ride


def main():

    # Load the data from disk
    loader = DataLoader("data")

    valid_stations = set()

    for stop in loader.get_stops().values():
        # if stop.get_station().get_borough() == "M":
        valid_stations.add(stop.get_station())

    chooser = VisitAllConnectionChooser(valid_stations, valid_stations)

    # Run one simulation
    shortest_ride = None

    # Run more
    for station in valid_stations:

        # Only begin at a terminal stop
        if not station.is_terminal():
            continue

        for starting_stop in station.get_stops():

            if starting_stop.is_terminal():
                continue

            print("Running test from %s" % starting_stop)
            shortest = run_test(starting_stop, chooser)

            if shortest_ride is None:
                shortest_ride = shortest

            if shortest.get_length() < shortest_ride.get_length():
                shortest_ride = shortest

    print("\nSummary:\n")
    print("\n".join(map(str, shortest_ride.get_segments())))

    print("\nDistinct Stations: %d of %d" % (shortest_ride.get_length(), len(valid_stations)))


if __name__ == "__main__":
    main()
