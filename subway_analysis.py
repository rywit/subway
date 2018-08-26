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
        runs = [run_simulation(child, ride_chooser) for x in range(100)]

        # Sort in descending order of distinct stations
        runs.sort(key=lambda x: x.get_num_stations(), reverse=True)

        if runs[0].get_num_stations() > longest_ride.get_num_stations():
            longest_ride = runs[0]

    return longest_ride


def run_test(ride_chooser, start_station, start_time):

    # Seed our simulation
    longest_ride = SubwayRide(start_station, start_time)
    run_simulation(longest_ride, ride_chooser)

    print("Seed length: %d" % longest_ride.get_num_stations())

    # Run evolution
    for i in range(15):
        longest_ride = run_evolution(longest_ride, ride_chooser)
        print("Generation %d - length: %d" % (i, longest_ride.get_num_stations()))

    return longest_ride


def main():

    # Load the data from disk
    loader = DataLoader("data")

    far_rockaway = "H11N"
    # pelham_bay = "601S"

    # Start each simulation at this station
    start_station = loader.get_stops()[far_rockaway]
    start_time = 4 * 3600

    ride_chooser = UniqueRide(loader.get_timetable(), 250)

    # Run one simulation
    longest_ride = run_test(ride_chooser, start_station, start_time)

    # Run more
    for i in range(10):
        print("Running test %d" % i)
        longest = run_test(ride_chooser, start_station, start_time)

        if longest.get_num_stations() > longest_ride.get_num_stations():
            longest_ride = longest

    print("\nDistinct Stations (%d):\n" % longest_ride.get_num_stations())

    print("\nSummary:\n")
    print("\n".join(map(str, longest_ride.get_summary_segments())))


if __name__ == "__main__":
    main()
