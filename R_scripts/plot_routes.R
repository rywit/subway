library( ggmap )
library( dplyr )
library( tidyr )

source( "R_scripts/utils.R")

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
  rename( "lat" = "shape_pt_lat", "lon" = "shape_pt_lon" ) %>%
  select( shape_id, route_id, lat, lon, shape_pt_sequence )

station.set <- stations %>%
  filter( borough != "SI" ) %>%
#  filter( borough %in% c( "M" ) ) %>%
  rename( "lat" = "latitude", "lon" = "longitude" ) %>%
  select( lat, lon, stop_name )

## Function to add stations to plot
add.stations <- function( g, stations, size = 1.5, alpha = 0.5 ) {
  p + geom_point( aes( x = lon, y = lat ), data = stations, colour = "#333333", size = size, alpha = alpha )
}

build.tails <- function( route.1, route.2 ) {
 
  route.1 <- route.1 %>%
    mutate( dummy = 1 )
  
  route.2 <- route.2 %>%
    mutate( dummy = 1 )
  
  distances <- route.2 %>%
    inner_join( route.1, by = "dummy" ) %>%
    mutate( dist = calc.distance( lat.x, lon.x, lat.y, lon.y ) ) %>%
    group_by( shape_pt_sequence.x ) %>%
    summarise( min.dist = min( dist ) ) %>%
    mutate( non.zero = min.dist > 0 ) %>%
    rename( "cur_pt" = "shape_pt_sequence.x" ) %>%
    mutate( next_pt = cur_pt + 1, prev_pt = cur_pt - 1 ) %>%
    select( cur_pt, prev_pt, next_pt, non.zero )

  grouped <- distances %>%
    left_join( distances, by = c( "next_pt" = "cur_pt" ) ) %>%
    select( -c( prev_pt.y, next_pt.y ) ) %>%
    left_join( distances, by = c( "prev_pt.x" = "cur_pt" ) ) %>%
    select( -c( prev_pt, next_pt.y ) ) %>%
    rename( "prev.zero" = "non.zero", "next.zero" = "non.zero.y", "non.zero" = "non.zero.x" ) %>%
    mutate( prev.zero = ifelse( is.na( prev.zero ), non.zero, prev.zero ) ) %>%
    mutate( next.zero = ifelse( is.na( next.zero ), non.zero, next.zero ) ) %>%
    filter( non.zero == T | next.zero == T | prev.zero == T ) %>%
    select( cur_pt ) %>%
    mutate( boundary = c( F, diff( cur_pt ) > 1 ) ) %>%
    mutate( group_num = cumsum( boundary ) ) %>%
    select( cur_pt, group_num ) %>%
    inner_join( route.2, by = c( "cur_pt" = "shape_pt_sequence" ) ) %>%
    rename( "shape_pt_sequence" = "cur_pt" )

  split( grouped, grouped$group_num )
}

dodge.routes <- function( route.1, route.2, dodge.lat, dodge.lon ) {
  
  route.1 <- route.1 %>%
    mutate( dummy = 1 )
  
  route.2 <- route.2 %>%
    mutate( dummy = 1 )
  
  overlaps.1 <- route.1 %>%
    inner_join( route.2, by = "dummy" ) %>%
    mutate( dist = calc.distance( lat.x, lon.x, lat.y, lon.y ) ) %>%
    group_by( shape_pt_sequence.x ) %>%
    summarise( min.dist = min( dist ) ) %>%
    filter( min.dist < 0.01 ) %>%
    rename( "shape_pt_sequence" = "shape_pt_sequence.x" ) %>%
    mutate( dodge.lat = dodge.lat, dodge.lon = dodge.lon ) %>%
    select( shape_pt_sequence, dodge.lat, dodge.lon )

  overlaps.2 <- route.2 %>%
    inner_join( route.1, by = "dummy" ) %>%
    mutate( dist = calc.distance( lat.x, lon.x, lat.y, lon.y ) ) %>%
    group_by( shape_pt_sequence.x ) %>%
    summarise( min.dist = min( dist ) ) %>%
    filter( min.dist < 0.01 ) %>%
    rename( "shape_pt_sequence" = "shape_pt_sequence.x" ) %>%
    mutate( dodge.lat = dodge.lat, dodge.lon = dodge.lon ) %>%
    select( shape_pt_sequence, dodge.lat, dodge.lon )

  route.1 <- route.1 %>%
    left_join( overlaps.1, by = "shape_pt_sequence" ) %>%
    mutate( dodge.lat = ifelse( is.na( dodge.lat ), 0, dodge.lat ) ) %>%
    mutate( dodge.lon = ifelse( is.na( dodge.lon ), 0, dodge.lon ) ) %>%
    mutate( lat = lat + dodge.lat, lon = lon + dodge.lon ) %>%
    select( -c( dodge.lat, dodge.lon, dummy ) )

  route.2 <- route.2 %>%
    left_join( overlaps.2, by = "shape_pt_sequence" ) %>%
    mutate( dodge.lat = ifelse( is.na( dodge.lat ), 0, dodge.lat ) ) %>%
    mutate( dodge.lon = ifelse( is.na( dodge.lon ), 0, dodge.lon ) ) %>%
    mutate( lat = lat - dodge.lat, lon = lon - dodge.lon ) %>%
    select( -c( dodge.lat, dodge.lon, dummy ) )
  
  return( list( route.1, route.2 ) )
}

dodge.lines <- function( lines.1, lines.2, lat = 0.001, lon = 0.001 ) {
  
  for ( i in seq_along( lines.1 ) ) {
    for ( j in seq_along( lines.2 ) ) {
      res <- dodge.routes( lines.1[[i]], lines.2[[j]], lat, lon )
      
      lines.1[[i]] <- res[[1]]
      lines.2[[j]] <- res[[2]]
    }
  }
  
  return( list( lines.1, lines.2 ) )
}

build.red.lines <- function( shape ) {
  
  route.1 <- shape %>% filter( shape_id == "1..N03R" )
  route.2 <- shape %>% filter( shape_id == "2..N01R" )
  route.3 <- shape %>% filter( shape_id == "3..N01R" )
  
  tails.2 <- build.tails( route.1, route.2 )
  tails.3 <- build.tails( route.2, route.3 )
  
  return( c( list( route.1 ), tails.2, tails.3 ) )  
}

build.green.lines <- function( shape ) {
  
  route.6 <- shape %>% filter( shape_id == "6..N01R" )
  route.4 <- shape %>% filter( shape_id == "4..N06R" )
  route.5 <- shape %>% filter( shape_id == "5..N71R" )
  
  tails.4 <- build.tails( route.6, route.4 )
  tails.5 <- build.tails( route.4, route.5 )
  
  return( c( list( route.6 ), tails.4, tails.5 ) )  
}

build.purple.lines <- function( shape ) {
  
  route.7 <- shape %>% filter( shape_id == "7..N97R")
  
  return( list( route.7 ) )
}

build.blue.lines <- function( shape ) {

  route.a <- shape %>% filter( shape_id == "A..N54R")
  route.a.b <- shape %>% filter( shape_id == "A..N55R")
  route.e <- shape %>% filter( shape_id == "E..N66R")
  
  tails.a <- build.tails( route.a, route.a.b )
  tails.e <- build.tails( route.a, route.e )
  
  return( c( list( route.a ), tails.a, tails.e ) )  
}

build.orange.lines <- function( shape ) {

  route.d <- shape %>% filter( shape_id == "D..N07R")
  route.b <- shape %>% filter( shape_id == "B..N46R")
  route.f <- shape %>% filter( shape_id == "F..N69R")
  route.m <- shape %>% filter( shape_id == "M..N20R")
  
  tails.b <- build.tails( route.d, route.b )
  tails.f <- build.tails( route.d, route.f )
  tails.m <- build.tails( route.f, route.m )
  
  return( c( list( route.d ), tails.b, tails.f, tails.m ) )
}

build.yellow.lines <- function( shape ) {
  
  route.n <- shape %>% filter( shape_id == "N..N20R")
  route.r <- shape %>% filter( shape_id == "R..N93R")
  route.q <- shape %>% filter( shape_id == "Q..N16R")
  
  tails.r <- build.tails( route.n, route.r )
  tails.q <- build.tails( route.r, route.q )
  
  return( c( list( route.n ), tails.r, tails.q ) )  
}

build.grey.lines <- function( shape ) {
  
  route.l <- shape %>% filter( shape_id == "L..N01R")
  
  return( list( route.l ) )
}

build.brown.lines <- function( shape ) {
  
  route.j <- shape %>% filter( shape_id == "J..N41R")
  
  return( list( route.j ) )
}

build.lime.lines <- function( shape ) {
  
  route.g <- shape %>% filter( shape_id == "G..N14R")
  
  return( list( route.g ) )
}

build.shuttle.lines <- function( shape ) {
  
  route.h <- shape %>% filter( shape_id == "H..N21R")
  
  return( list( route.h ) )
}


green.lines <- build.green.lines( shape )
red.lines <- build.red.lines( shape )
purple.lines <- build.purple.lines( shape )

blue.lines <- build.blue.lines( shape )
orange.lines <- build.orange.lines( shape )
yellow.lines <- build.yellow.lines( shape )
grey.lines <- build.grey.lines( shape )
brown.lines <- build.brown.lines( shape )
lime.lines <- build.lime.lines( shape )

shuttle.lines <- build.shuttle.lines( shape )

c( green.lines, red.lines ) := dodge.lines( green.lines, red.lines, lat = 0.001, lon = 0.001 )
c( blue.lines, orange.lines ) := dodge.lines( blue.lines, orange.lines, lat = 0.001, lon = 0.002 )
c( orange.lines, lime.lines ) := dodge.lines( orange.lines, lime.lines, lat = 0.001, lon = 0.001 )

lines <- list( list( routes = red.lines, color = "#EE352E" ),
               list( routes = orange.lines, color = "#FF6319" ),
               list( routes = green.lines, color = "#00933C" ),
               list( routes = purple.lines, color = "#B933AD" ),
               list( routes = blue.lines, color = "#2850AD" ),
               list( routes = orange.lines, color = "#FF6319" ),
               list( routes = yellow.lines, color = "#FCCC0A" ),
               list( routes = grey.lines, color = "#A7A9AC" ),
               list( routes = brown.lines, color = "#996633" ),
               list( routes = lime.lines, color = "#6CBE45" ),
               list( routes = shuttle.lines, color = "#808183" ) )

# Build plot
p <- qmplot( lon, lat, data = station.set, maptype = "toner-lite", geom = "blank" )

for ( line in lines ) {
  for ( route in line$routes ) {
    p <- p + geom_path(aes( x = lon, y = lat ), size = 1.5, alpha = 0.6, data = route, colour = line$color )
  }
}

p <- add.stations( p, station.set, size = 1.5, alpha = 0.75 )

p

ggsave("testplot.jpg", p, height = 6, width = 7, units = "in" )



xx <- c( rep( T, 5 ), rep( F, 3 ), rep( T, 6 ), rep( F, 10 ), rep( T, 5 ) )

which( diff( xx ) != 0 )

idx <- cumsum( c( FALSE, diff( xx ) != 0 ) ) + 1

split( xx, idx )


for ( i in seq_along( switches ) ) {
  start <- 
  
  
  yy <- c( yy, list( xx))
}


which( diff( xx ) == 1 )

which( diff( xx ) == -1 )

xx[8]
xx[9]
