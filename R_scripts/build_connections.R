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
stop.diffs <- weekday.trips %>%
  inner_join( weekday.trips, by = "trip_id" ) %>%
  filter( stop_sequence.x < stop_sequence.y ) %>%
  mutate( stop_diff = stop_sequence.y - stop_sequence.x ) %>%
  select( stop_id.x, stop_id.y, stop_diff ) %>%
  rename( "from_stop_id" = "stop_id.x", "to_stop_id" = "stop_id.y" ) %>%
  group_by( from_stop_id, to_stop_id ) %>%
  summarise( stop_diff = max( stop_diff ) ) %>%
  ungroup()

links <- connections %>%
  inner_join( stop.diffs, by = c( "from_stop_id", "to_stop_id" ) ) %>%
  filter( stop_diff == 1 ) %>%
  select( from_stop_id, to_stop_id ) %>%
  distinct()

write.csv( links, "data/links.txt", quote = F, row.names = F )


