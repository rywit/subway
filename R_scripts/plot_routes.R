library( ggmap )
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


stations <- read.csv( "data/stations.txt", stringsAsFactors = F )
shapes <- read.csv( "data/shapes.txt", stringsAsFactors = F )
routes <- read.csv( "data/routes.txt", stringsAsFactors = F )
trips <- read.csv( "data/trips.txt", stringsAsFactors = F )

colors <- trips %>%
  filter( shape_id != "" ) %>%
  inner_join( routes, by = "route_id" ) %>%
  select( shape_id, route_id, route_color ) %>%
  distinct() %>%
  mutate( route_color = sprintf( "#%s", route_color ) )

shape <- shapes %>%
  inner_join( colors, by = "shape_id" ) %>%
  rename( "lat" = "shape_pt_lat", "lon" = "shape_pt_lon" )

station.set <- stations %>%
  filter( borough != "SI" ) %>%
#  filter( borough %in% c( "M" ) ) %>%
  rename( "lat" = "latitude", "lon" = "longitude" ) %>%
  select( lat, lon, stop_name )

## Function to add stations to plot
add.stations <- function( g, stations, size = 1.5, alpha = 0.5 ) {
  p + geom_point( aes( x = lon, y = lat ), data = stations, colour = "#333333", size = size, alpha = alpha )
}
  

route.n <- shape %>% filter( shape_id == "N..N20R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )

route.r.a <- shape %>% filter( shape_id == "R..N93R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence <= 21 )

route.r.b <- shape %>% filter( shape_id == "R..N93R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence >= 519 )

route.q.a <- shape %>% filter( shape_id == "Q..N16R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence <= 381 )

route.q.b <- shape %>% filter( shape_id == "Q..N16R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence >= 573 )

route.a.a <- shape %>% filter( shape_id == "A..N54R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  mutate( x = ifelse( shape_pt_sequence > 597, x - 0.0005, x ),
          y = ifelse( shape_pt_sequence > 597, y + 0.0005, y ) ) %>%
  mutate( x = ifelse( shape_pt_sequence > 720, x + 0.0005, x ),
          y = ifelse( shape_pt_sequence > 720, y - 0.0005, y ) )

route.a.b <- shape %>% filter( shape_id == "A..N55R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence <= 261 )

route.e.a <- shape %>% filter( shape_id == "E..N66R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence <= 18 )

route.e.b <- shape %>% filter( shape_id == "E..N66R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence >= 108 )

route.d <- shape %>% filter( shape_id == "D..N07R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )

route.b <- shape %>% filter( shape_id == "B..N46R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence <= 299 )

route.f.a <- shape %>% filter( shape_id == "F..N69R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )

route.f.b <- shape %>% filter( shape_id == "F..N69R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence >= 697 )

route.m.a <- shape %>% filter( shape_id == "M..N20R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence <= 282 )

route.m.b <- shape %>% filter( shape_id == "M..N20R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence >= 357 & shape_pt_sequence <= 445 )

route.m.c <- shape %>% filter( shape_id == "M..N20R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence >= 474 & shape_pt_sequence <= 542 )

route.m <- shape %>% filter( shape_id == "M..N20R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence <= 282 )

route.l <- shape %>% filter( shape_id == "L..N01R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )

route.j <- shape %>% filter( shape_id == "J..N41R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )

route.g <- shape %>% filter( shape_id == "G..N14R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )

route.h <- shape %>% filter( shape_id == "H..N21R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )






build.tails <- function( route.1, route.2 ) {
 
  route.1 <- route.1 %>%
    mutate( dummy = 1 )
  
  route.2 <- route.2 %>%
    mutate( dummy = 1 )
  
  overlaps.2 <- route.2 %>%
    inner_join( route.1, by = "dummy" ) %>%
    mutate( dist = calc.distance( lat.x, lon.x, lat.y, lon.y ) ) %>%
    group_by( shape_pt_sequence.x ) %>%
    summarise( min.dist = min( dist ) ) %>%
    mutate( non.zero = min.dist > 0 )
  
  route.2.a <- route.2 %>%
    filter( shape_pt_sequence <= min( which( overlaps.2$non.zero == FALSE ) ) )
  
  route.2.b <- route.2 %>%
    filter( shape_pt_sequence >= max( which( overlaps.2$non.zero == FALSE ) ) )
  
   return( list( route.2.a, route.2.b ) )
}

build.red.lines <- function( shape ) {
  
  route.1 <- shape %>% filter( shape_id == "1..N03R" )
  route.2 <- shape %>% filter( shape_id == "2..N01R" )
  route.3 <- shape %>% filter( shape_id == "3..N01R" )
    
  tails.2 <- build.tails( route.1, route.2 )
  tails.3 <- build.tails( route.2, route.3 )

  return( list( route.1, tails.2[[1]], tails.2[[2]], tails.3[[1]], tails.3[[2]] ) )  
}

build.green.lines <- function( shape ) {
  
  route.6 <- shape %>% filter( shape_id == "6..N01R" )
  route.4 <- shape %>% filter( shape_id == "4..N06R" )
  route.5 <- shape %>% filter( shape_id == "5..N71R" )
  
  tails.2 <- build.tails( route.6, route.4 )
  tails.3 <- build.tails( route.4, route.5 )
  
  return( list( route.6, tails.2[[1]], tails.2[[2]], tails.3[[1]], tails.3[[2]] ) )  
}

build.purple.lines <- function( shape ) {
  
  route.7 <- shape %>% filter( shape_id == "7..N97R")
  
  return( list( route.7 ) )
}

# Build plot
p <- qmplot( lon, lat, data = station.set, maptype = "toner-lite", geom = "blank" )

for ( path in build.red.lines( shape ) ) {
  p <- p + geom_path(aes( x = lon, y = lat ), size = 2, alpha = 0.6, data = path, colour = "#EE352E" )
}

for ( path in build.green.lines( shape ) ) {
  p <- p + geom_path(aes( x = lon, y = lat ), size = 2, alpha = 0.6, data = path, colour = "#00933C" )
}

for ( path in build.purple.lines( shape ) ) {
  p <- p + geom_path(aes( x = lon, y = lat ), size = 2, alpha = 0.6, data = path, colour = "#B933AD" )
}

p <- add.stations( p, station.set, size = 1.5, alpha = 0.75 )

ggsave("testplot.jpg", p, height = 6, width = 7, units = "in" )
