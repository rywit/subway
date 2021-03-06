library( tidyr )
library( dplyr )

radians <- function( deg ) {
  deg * pi / 180
}

calc.distance <- function( lat1, lon1, lat2, lon2 ) {
  
  # approximate radius of earth in km
  R <- 6373.0
  
  lat1 <- radians( lat1 )
  lon1 <- radians( lon1 )
  lat2 <- radians( lat2 )
  lon2 <- radians( lon2 )

  dlon <- lon2 - lon1
  dlat <- lat2 - lat1
  
  a <- sin( dlat / 2 ) ** 2 + cos( lat1 ) * cos( lat2 ) * sin( dlon / 2 ) ** 2
  c <- 2 * atan2( sqrt( a ), sqrt( 1 - a ) )
  
  return( R * c )
}

# Read the data from disk
trips <- read.csv( "data/trips.txt", stringsAsFactors = F )
shapes <- read.csv( "data/shapes.txt", stringsAsFactors = F )
stops <- read.csv( "data/stops.txt", stringsAsFactors = F )
stop.times <- read.csv( "data/stop_times.txt", stringsAsFactors = F )
stations <- read.csv( "data/stations.txt", stringsAsFactors = F )
transfers <- read.csv( "data/transfers.txt", stringsAsFactors = F )

# Add station_id to our stop data
stops <- stops %>%
  left_join( select( stations, station_id, gtfs_stop_id, complex_id ), by = c( "parent_station" = "gtfs_stop_id" ) )

# Insert correct coordinates for Aqueduct Racetrack
stops[ stops$parent_station == "H01", "stop_lat" ] <- 40.672086
stops[ stops$parent_station == "H01", "stop_lon" ] <- -73.835914

# Calculate the distance (in km) between pairs of shape sequence points
distances <- shapes %>%
  select( -c( shape_dist_traveled ) ) %>%
  mutate( next_pt_sequence = shape_pt_sequence + 1 ) %>%
  rename( "lat1" = "shape_pt_lat", "lon1" = "shape_pt_lon" ) %>%
  left_join( shapes, by = c( "shape_id", "next_pt_sequence" = "shape_pt_sequence" ) ) %>%
  rename( "lat2" = "shape_pt_lat", "lon2" = "shape_pt_lon" ) %>%
  select( -c( next_pt_sequence, shape_dist_traveled ) ) %>%
  mutate( dist = calc.distance( lat1, lon1, lat2, lon2 ) ) %>%
  group_by( shape_id ) %>%
  mutate( cum_dist = lag(cumsum( dist ), default = 0 ) ) %>%
  rename( "stop_lat" = "lat1", "stop_lon" = "lon1" ) %>%
  select( c( shape_id, stop_lat, stop_lon, shape_pt_sequence, dist, cum_dist ) )

# Interpolate the location of the stations within the shapes
stop.locations <- stop.times %>%
  inner_join( trips, by = "trip_id" ) %>%
  select( stop_id, shape_id ) %>%
  distinct() %>%
  inner_join( stops, by = "stop_id" ) %>%
  select( stop_id, shape_id, stop_lat, stop_lon ) %>%
  inner_join( shapes, by = "shape_id" ) %>%
  select( stop_id, shape_id, stop_lat, stop_lon, shape_pt_lat, shape_pt_lon, shape_pt_sequence ) %>%
  filter( abs( stop_lat - shape_pt_lat ) < 0.01, abs( stop_lon - shape_pt_lon ) < 0.01 ) %>%
  mutate( dist = ( stop_lat - shape_pt_lat ) ^ 2 + ( stop_lon - shape_pt_lon ) ^ 2 ) %>%
  group_by( stop_id, shape_id ) %>%
  top_n( -1, dist ) %>%
  ungroup() %>%
  select( stop_id, shape_id, shape_pt_sequence )

# Get the cumulative trip distance for each stop on each trip
stop.dist <- trips %>%
  filter( grepl( "Weekday", service_id ) ) %>%
  select( route_id, trip_id, shape_id ) %>%
  inner_join( stop.times, by = c( "trip_id" ) ) %>%
  select( c( route_id, shape_id, stop_id, stop_sequence ) ) %>%
  inner_join( stop.locations, by = c( "stop_id", "shape_id" ) ) %>%
  select( route_id, shape_id, stop_id, stop_sequence, shape_pt_sequence ) %>%
  inner_join( distances, by = c( "shape_id", "shape_pt_sequence" ) ) %>%
  select( -c( dist, shape_pt_sequence ) ) %>%
  mutate( next_stop_sequence = stop_sequence + 1 ) %>%
  distinct()

# Calculate the distance between consecutive stops
shape.dist <- stop.dist %>%
  inner_join( stop.dist, by = c( "route_id", "shape_id", "next_stop_sequence" = "stop_sequence" ) ) %>%
  rename( "from_stop_id" = "stop_id.x", "to_stop_id" = "stop_id.y" ) %>%
  mutate( dist = cum_dist.y - cum_dist.x ) %>%
  select( route_id, shape_id, from_stop_id, to_stop_id, dist )

# Find the minimum distance between pairs of stops
shortest.rides <- shape.dist %>%
  group_by( from_stop_id, to_stop_id ) %>%
  summarise( dist_km = min( dist ) ) %>%
  as.data.frame()

# Convert stop distances back to station distances
by.station <- shortest.rides %>%
  inner_join( stops, by = c( "from_stop_id" = "stop_id" ) ) %>%
  rename( "from_station_id" = "station_id" ) %>%
  select( from_station_id, to_stop_id, dist_km ) %>%
  inner_join( stops, by = c( "to_stop_id" = "stop_id" ) ) %>%
  rename( "to_station_id" = "station_id" ) %>%
  select( from_station_id, to_station_id, dist_km ) %>%
  group_by( from_station_id, to_station_id ) %>%
  summarise( dist_km = min( dist_km ) ) %>%
  ungroup()

# Calculate "as the crow flies" distances pairs of troublesome stations
trouble.stops <- stops %>%
  filter( station_id %in% c( "42", "139", "141", "142", "468", "469", "196", "197", "192", "330", "23" ) ) %>%
  select( station_id, stop_lat, stop_lon ) %>%
  distinct()

straight.dist <- trouble.stops %>%
  rename( "from_station_id" = "station_id", "lat1" = "stop_lat", "lon1" = "stop_lon" ) %>%
  crossing( trouble.stops ) %>%
  rename( "to_station_id" = "station_id", "lat2" = "stop_lat", "lon2" = "stop_lon" ) %>%
  mutate( dist_km = calc.distance(lat1, lon1, lat2, lon2 ) ) %>%
  select( from_station_id, to_station_id, dist_km ) %>%
  as.data.frame()

# Set distances within complexes to be straight-line distance
transfer.dist <- transfers %>%
  filter( from_stop_id != to_stop_id ) %>%
  inner_join( stations, by = c( "from_stop_id" = "gtfs_stop_id" ) ) %>%
  rename( "from_station_id" = "station_id", "from_lat" = "latitude", "from_lon" = "longitude" ) %>%
  select( from_station_id, to_stop_id, from_lat, from_lon ) %>%
  inner_join( stations, by = c( "to_stop_id" = "gtfs_stop_id" ) ) %>%
  rename( "to_station_id" = "station_id", "to_lat" = "latitude", "to_lon" = "longitude" ) %>%
  select( from_station_id, to_station_id, from_lat, from_lon, to_lat, to_lon ) %>%
  filter( from_station_id != to_station_id ) %>%
  mutate( dist_km = calc.distance(from_lat, from_lon, to_lat, to_lon ) ) %>%
  select( from_station_id, to_station_id, dist_km ) %>%
  distinct()

same.station <- stops %>%
  filter( !is.na( station_id ) ) %>%
  select( station_id ) %>%
  distinct() %>%
  mutate( from_station_id = station_id, to_station_id = station_id, dist_km = 0.0 ) %>%
  select( -station_id )

# Merge "true" distances with "as the crow flies" distances
shortest.routes <- rbind( by.station, straight.dist, transfer.dist, same.station )

# Write to disk
write.csv( shortest.routes, "data/distances.txt", quote = F, na = "", row.names = F )
