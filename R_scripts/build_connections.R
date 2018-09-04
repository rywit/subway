library(dplyr)

# Read stop time data from disk
stop.times <- read.csv( "data/stop_times.txt", stringsAsFactors = F )

# Read trip data from disk
trips <- read.csv( "data/trips.txt", stringsAsFactors = F )

# Read stop data from disk
stops <- read.csv( "data/stops.txt", stringsAsFactors = F )

# Filter for routes during 8AM-6PM weekdays
weekday.trips <- stop.times %>%
  filter( grepl( "Weekday", trip_id ) ) %>%
  filter( arrival_time >= "08:00:00", arrival_time <= "18:00:00" ) %>%
  select( trip_id, stop_id, stop_sequence ) %>%
  inner_join( trips, by = "trip_id" ) %>%
  filter( route_id != "SI" ) %>%
  select( trip_id, stop_id, stop_sequence, route_id )

# Find conscutive stops
connections <- weekday.trips %>%
  mutate( next_stop_sequence = stop_sequence + 1 ) %>%
  rename( "from_stop_id" = "stop_id" ) %>%
  inner_join( weekday.trips, by = c( "trip_id", "route_id", "next_stop_sequence" = "stop_sequence" ) ) %>%
  rename( "to_stop_id" = "stop_id" ) %>%
  select( -c( trip_id, stop_sequence, next_stop_sequence ) ) %>%
  distinct()

write.csv( connections, "connections.txt", quote = F, row.names = F )

# Direct connections between stops (i.e. remove express trains)
direct <- connections %>%
  select( from_stop_id, to_stop_id ) %>%
  distinct() %>%
  inner_join( stops, by = c( "from_stop_id" = "stop_id" ) ) %>%
  select( from_stop_id, to_stop_id, stop_lat, stop_lon ) %>%
  rename( "from_stop_lat" = "stop_lat", "from_stop_lon" = "stop_lon" ) %>%
  inner_join( stops, by = c( "to_stop_id" = "stop_id" ) ) %>%
  rename( "to_stop_lat" = "stop_lat", "to_stop_lon" = "stop_lon" ) %>%
  select( from_stop_id, to_stop_id, from_stop_lat, from_stop_lon, to_stop_lat, to_stop_lon ) %>%
  mutate( dist = calc.distance( from_stop_lat, from_stop_lon, to_stop_lat, to_stop_lon ) ) %>%
  group_by( from_stop_id ) %>%
  top_n( -1, wt = dist ) %>%
  ungroup() %>%
  select( from_stop_id, to_stop_id )

write.csv( direct, "data/links.txt", quote = F, row.names = F )

