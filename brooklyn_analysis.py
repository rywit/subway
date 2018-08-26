from Subway import *


def run_simulation(ride, chooser):

    chooser.init_ride(ride)

    while not chooser.is_complete():
        chooser.iterate()

    return chooser.get_ride()


def get_children(ride, num_children):
    ride_len = ride.get_length()

    children = []

    for i in range(num_children):
        cut = random.randint(1, ride.get_length())
        children.append(ride.get_subset(cut))

    return children


def run_evolution(ride, chooser):

    children = get_children(ride, 10)

    shortest_ride = ride

    for child in children:

        # Run 100 simulations for this child
        child_ride = run_simulation(child, chooser)

        if child_ride.get_ride_length() < shortest_ride.get_ride_length():
            shortest_ride = child_ride

    return shortest_ride


def run_test(stop, chooser):

    ride = SubwayRide(StartingConnection(stop))

    # Seed our simulation
    shortest_ride = run_simulation(ride, chooser)

    lengths = [shortest_ride.get_ride_length()]

    # Run 10 evolutions
    for i in range(2):
        shortest_ride = run_evolution(shortest_ride, chooser)
        lengths.append(shortest_ride.get_ride_length())

    # Keep running if the length increases
    # while lengths[-1] < lengths[-11]:
    #     shortest_ride = run_evolution(shortest_ride, chooser)
    #     lengths.append(shortest_ride.get_ride_length())

    print("Length: %d" % shortest_ride.get_ride_length())

    return shortest_ride


def main():

    # Load the data from disk
    loader = DataLoader("data")

    brooklyn_stations = set()

    for stop in loader.get_stops().values():
        if stop.get_station().get_borough() == "Bk":
            brooklyn_stations.add(stop.get_station())

    bway_jct = "A51N"

    # Start each simulation at this station
    stop = loader.get_stops()[bway_jct]
    chooser = AllStationChooser(brooklyn_stations)

    # Run one simulation
    shortest_ride = run_test(stop, chooser)

    # Run more
    for i in range(10):
        print("Running test %d" % i)
        shortest = run_test(stop, chooser)

        if shortest.get_ride_length() < shortest_ride.get_ride_length():
            shortest_ride = shortest

    print("\nRide Length (%d):\n" % shortest_ride.get_ride_length())

    print("\nSummary:\n")
    print("\n".join(map(str, shortest_ride.get_segments())))


if __name__ == "__main__":
    main()
