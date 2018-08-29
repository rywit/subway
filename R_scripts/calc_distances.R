radians <- function( deg ) {
  deg * pi / 180
}

calc.distance <- function(lat1, lon1, lat2, lon2) {
  
  # approximate radius of earth in km
  R <- 6373.0
  
  lat1 <- radians(lat1)
  lon1 <- radians(lon1)
  lat2 <- radians(lat2)
  lon2 <- radians(lon2)
  
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

# Get the cumulative trip distance for each stop on each trip
stop.dist <- trips %>%
  filter( grepl( "Weekday", service_id ) ) %>%
  select( route_id, trip_id, shape_id ) %>%
  inner_join( stop.times, by = c( "trip_id" ) ) %>%
  select( c( route_id, shape_id, stop_id, stop_sequence ) ) %>%
  inner_join( stops, by = "stop_id" ) %>%
  select( c( route_id, shape_id, stop_id, stop_sequence, stop_name, stop_lat, stop_lon ) ) %>%
  inner_join( distances, by = c( "shape_id", "stop_lat", "stop_lon" ) ) %>%
  select( -c( dist, shape_pt_sequence ) ) %>%
  mutate( next_stop_sequence = stop_sequence + 1 ) %>%
  distinct()

# Calculate the distance between consecutive stops
shape.dist <- stop.dist %>%
  inner_join( stop.dist, by = c( "route_id", "shape_id", "next_stop_sequence" = "stop_sequence" ) ) %>%
  rename( "from_stop_id" = "stop_id.x", "to_stop_id" = "stop_id.y" ) %>%
  mutate( dist = cum_dist.y - cum_dist.x ) %>%
  select( route_id, shape_id, from_stop_id, to_stop_id, stop_name.x, stop_name.y, dist )

# Find the minimum distance between pairs of stops
shortest.rides <- shape.dist %>%
  group_by( from_stop_id, to_stop_id ) %>%
  summarise( dist_km = min( dist ) )

# Calculate "as the crow flies" distances between all pairs of stops
straight.dist <- stops %>%
  filter( location_type == "0" ) %>%
  select( stop_id, stop_lat, stop_lon, location_type ) %>%
  rename( "from_stop_id" = "stop_id", "lat1" = "stop_lat", "lon1" = "stop_lon" ) %>%
  inner_join( stops, by = "location_type" ) %>%
  rename( "to_stop_id" = "stop_id", "lat2" = "stop_lat", "lon2" = "stop_lon" ) %>%
  select( from_stop_id, to_stop_id, lat1, lon1, lat2, lon2 ) %>%
  mutate( dist_km = calc.distance(lat1, lon1, lat2, lon2 ) )

# Merge "true" distances with "as the crow flies" distances
shortest.routes <- straight.dist %>%
  left_join( shortest.rides, by = c( "from_stop_id", "to_stop_id" ) ) %>%
  mutate( dist = ifelse( is.na( dist_km.y ), dist_km.x, dist_km.y ) ) %>%
  head()

# Write to disk
write.csv(shortest.routes, "data/distances.txt", quote = F, na = "", row.names = F)
