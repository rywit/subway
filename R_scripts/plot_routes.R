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

manh <- stations %>%
  filter( borough == "M" ) %>%
  rename( "lat" = "latitude", "lon" = "longitude" ) %>%
  select( lat, lon, stop_name )

qmplot( lon, lat, data = manh, maptype = "toner-lite", color = I( "black" )) +
  geom_path(aes( x = x, y = y ), size = 2, alpha = 0.5, data = route.1, colour = "#EE352E" ) +
  geom_path(aes( x = x, y = y ), size = 2, alpha = 0.5, data = route.2.a, colour = "#EE352E" ) +
  geom_path(aes( x = x, y = y ), size = 2, alpha = 0.5, data = route.2.b, colour = "#EE352E" ) +
  geom_path(aes( x = x, y = y ), size = 2, alpha = 0.5, data = route.3.a, colour = "#EE352E" ) +
  geom_path(aes( x = x, y = y ), size = 2, alpha = 0.5, data = route.3.b, colour = "#EE352E" ) +
  geom_path(aes( x = x, y = y ), size = 2, alpha = 0.5, data = route.4, colour = "#00933C" ) +
  geom_path(aes( x = x, y = y ), size = 2, alpha = 0.5, data = route.5.a, colour = "#00933C" ) +
  geom_path(aes( x = x, y = y ), size = 2, alpha = 0.5, data = route.5.b, colour = "#00933C" ) +
  geom_path(aes( x = x, y = y ), size = 2, alpha = 0.5, data = route.6, colour = "#00933C" ) +
  geom_path(aes( x = x, y = y ), size = 2, alpha = 0.5, data = route.7, colour = "#B933AD" ) +
  #  geom_segment(aes( x = x, y = y, xend = xend, yend = yend ), size = 2, alpha = 0.5, data = blue.paths, colour = "#2850AD", linejoin="mitre", lineend="butt" ) +
#  geom_segment(aes( x = x, y = y, xend = xend, yend = yend ), size = 1.5, alpha = 0.5, data = yellow.paths, colour = "#FCCC0A" ) +
#  geom_segment(aes( x = x, y = y, xend = xend, yend = yend ), size = 1.5, alpha = 0.5, data = orange.paths, colour = "#FF6319" ) +
#  geom_segment(aes( x = x, y = y, xend = xend, yend = yend ), size = 1.5, alpha = 0.5, data = brown.paths, colour = "#996633" ) +
#  geom_segment(aes( x = x, y = y, xend = xend, yend = yend ), size = 1.5, alpha = 0.5, data = grey.paths, colour = "#A7A9AC" ) +
  geom_point( aes( x = lon, y = lat ), data = manh, colour = "#333333", size = 1.5, alpha = 0.75 )

## 1 Route 1..N03R
## 2 Route 2..N01R
## 3 Route 3..N01R

## 4 Route 4..N01R
## 5 Route 5..N71R
## 6 Route 6..N01R
## 7 Route 7..N97R

## Route A: A..N54R
## Route A: A..N55R
## Route C: C..N04R
## Route E: E..N66R

## Route B: B..N46R
## Route D: D..N07R
## Route F: F..N69R
## Route M: M..N20R

## Route N: N..N20R
## Route R: R..N93R
## Route Q: Q..N16R
## Route W: NA

## Route L: L..N01R
## Route J: J..N41R

## Rockaway: H..N21R

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

route.4 <- shape %>% filter( shape_id == "4..N01R") %>%
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

