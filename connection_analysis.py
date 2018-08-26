from Subway import *


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


def main():

    # Load the data from disk
    loader = DataLoader("data")

    far_rockaway = "H11N"
    # pelham_bay = "601S"

    # Start each simulation at this station
    stop = loader.get_stops()[far_rockaway]
    chooser = UniqueConnectionChooser()

    # Run one simulation
    longest_ride = run_test(stop, chooser)

    # Run more
    for i in range(10):
        print("Running test %d" % i)
        longest = run_test(stop, chooser)

        if longest.get_num_stations() > longest_ride.get_num_stations():
            longest_ride = longest

    print("\nDistinct Stations (%d):\n" % longest_ride.get_num_stations())

    print("\nSummary:\n")
    print("\n".join(map(str, longest_ride.get_segments())))


if __name__ == "__main__":
    main()
