library( ggmap )
library( dplyr )

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
  inner_join( colors, by = "shape_id" )

station.set <- stations %>%
  filter( borough != "SI" ) %>%
#  filter( borough %in% c( "Bx" ) ) %>%
  rename( "lat" = "latitude", "lon" = "longitude" ) %>%
  select( lat, lon, stop_name )

## Function to add stations to plot
add.stations <- function( g, stations, size = 1.5, alpha = 0.5 ) {
  p + geom_point( aes( x = lon, y = lat ), data = stations, colour = "#333333", size = size, alpha = alpha )
}
  
## Function to add colored routes to a plot
add.routes <- function(g, size = 1.5, alpha = 0.5) {

  g +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.1, colour = "#EE352E" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.2.a, colour = "#EE352E" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.2.b, colour = "#EE352E" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.3.a, colour = "#EE352E" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.3.b, colour = "#EE352E" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.4, colour = "#00933C" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.5.a, colour = "#00933C" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.5.b, colour = "#00933C" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.6, colour = "#00933C" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.7, colour = "#B933AD" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.n, colour = "#FCCC0A" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.r.a, colour = "#FCCC0A" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.r.b, colour = "#FCCC0A" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.q.a, colour = "#FCCC0A" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.q.b, colour = "#FCCC0A" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.a.a, colour = "#2850AD" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.a.b, colour = "#2850AD" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.e.a, colour = "#2850AD" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.e.b, colour = "#2850AD" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.b, colour = "#FF6319" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.d, colour = "#FF6319" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.f.a, colour = "#FF6319" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.f.b, colour = "#FF6319" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.m.a, colour = "#FF6319" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.m.b, colour = "#FF6319" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.m.c, colour = "#FF6319" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.l, colour = "#A7A9AC" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.j, colour = "#996633" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.g, colour = "#6CBE45" ) +
    geom_path(aes( x = x, y = y ), size = size, alpha = alpha, data = route.h, colour = "#808183" )
}

route.1 <- shape %>% filter( shape_id == "1..N03R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )

route.2.a <- shape %>% filter( shape_id == "2..N01R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence <= 191 )

route.2.b <- shape %>% filter( shape_id == "2..N01R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence >= 296 )

route.3.a <- shape %>% filter( shape_id == "3..N01R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence <= 40 )

route.3.b <- shape %>% filter( shape_id == "3..N01R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence >= 334 )

route.4 <- shape %>% filter( shape_id == "4..N06R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )

route.5.a <- shape %>% filter( shape_id == "5..N71R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence <= 39 )

route.5.b <- shape %>% filter( shape_id == "5..N71R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence >= 404 )

route.6 <- shape %>% filter( shape_id == "6..N01R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" ) %>%
  filter( shape_pt_sequence >= 208 )

route.7 <- shape %>% filter( shape_id == "7..N97R") %>%
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )

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
  rename( "y" = "shape_pt_lat", "x" = "shape_pt_lon" )

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


## Build charts
p <- qmplot( lon, lat, data = station.set, maptype = "toner-lite", geom = "blank" )
p <- add.routes( p, size = 2, alpha = 0.6 )
p <- add.stations( p, station.set, size = 1.5, alpha = 0.75 )

p

ggsave("testplot.jpg", p, height = 6, width = 7, units = "in" )

