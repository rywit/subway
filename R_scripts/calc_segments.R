locations <- stop.locations %>%
  inner_join( stops, by = "stop_id" ) %>%
  select( parent_station, shape_id, shape_pt_sequence, stop_lat, stop_lon ) %>%
  group_by( shape_id ) %>%
  mutate( counter = seq_along( parent_station ) ) %>%
  mutate( next_counter = counter + 1 )

legs <- locations %>%
  inner_join( locations, by = c( "shape_id", "next_counter" = "counter" ) ) %>%
  select( parent_station.x, parent_station.y, shape_id, shape_pt_sequence.x, shape_pt_sequence.y ) %>%
  rename( "from_station" = "parent_station.x", "to_station" = "parent_station.y" ) %>%
  rename( "from_pt" = "shape_pt_sequence.x", "to_pt" = "shape_pt_sequence.y" ) %>%
  group_by( from_station, to_station ) %>%
  top_n( 1, wt = shape_id ) %>%
  ungroup()


get.segment <- function( from, to ) {
  
  segment <- legs %>%
    filter( from_station == from, to_station == to )
  
  if ( nrow( segment ) > 0 ) {
    res <- segment %>%
      inner_join( shapes, by = "shape_id" ) %>%
      filter( shape_pt_sequence >= from_pt, shape_pt_sequence <= to_pt ) %>%
      arrange( shape_pt_sequence ) %>%
      select( shape_pt_sequence, shape_pt_lat, shape_pt_lon )
    
    return( res )
  }
  else {
    res <- rbind( station1, station2 ) %>%
      rename( "shape_pt_lat" = "latitude", "shape_pt_lon" = "longitude" ) %>%
      mutate( shape_pt_sequence = seq_along( shape_pt_lat ) )
    
    return( res )
  }
}