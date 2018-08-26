from Subway import *


def run_simulation(ride, ride_chooser):
    while not ride.is_complete():
        seg = ride_chooser.chooseSegment(ride)
        ride.add_segment(seg)

    return ride


def get_children(ride):
    ride_len = ride.get_length()

    if ride_len == 1:
        return ride
    else:
        return [ride.get_subset(x) for x in range(1, ride_len)]


def run_evolution(ride, ride_chooser):

    children = get_children(ride)

    longest_ride = ride

    for child in children:

        # Run 100 simulations for this child
        runs = [run_simulation(child, ride_chooser) for x in range(250)]

        # Sort in descending order of distinct stations
        runs.sort(key=lambda x: x.get_num_stations(), reverse=True)

        if runs[0].get_num_stations() > longest_ride.get_num_stations():
            longest_ride = runs[0]

    return longest_ride


def run_test(ride_chooser, start_station):

    # Seed our simulation
    longest_ride = SubwayRide(start_station)
    run_simulation(longest_ride, ride_chooser)

    lengths = [longest_ride.get_num_stations()]

    # Run 10 evolutions
    for i in range(20):
        longest_ride = run_evolution(longest_ride, ride_chooser)
        lengths.append(longest_ride.get_num_stations())

    # Keep running if the length increases
    while lengths[-1] > lengths[-11]:
        longest_ride = run_evolution(longest_ride, ride_chooser)
        lengths.append(longest_ride.get_num_stations())

    print("Length: %d" % longest_ride.get_num_stations())

    return longest_ride


def main():

    # Load the data from disk
    loader = DataLoader("data")

    far_rockaway = "H11N"
    # pelham_bay = "601S"

    # Start each simulation at this station
    start_station = loader.get_stops()[far_rockaway]

    ride_chooser = UniqueConnectionRide()

    # Run one simulation
    longest_ride = run_test(ride_chooser, start_station)

    # Run more
    for i in range(100):
        print("Running test %d" % i)
        longest = run_test(ride_chooser, start_station)

        if longest.get_num_stations() > longest_ride.get_num_stations():
            longest_ride = longest

    print("\nDistinct Stations (%d):\n" % longest_ride.get_num_stations())

    print("\nSummary:\n")
    print("\n".join(map(str, longest_ride.get_segments())))


if __name__ == "__main__":
    main()
