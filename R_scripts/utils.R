':=' <- function(lhs, rhs) {
  frame <- parent.frame()
  lhs <- as.list(substitute(lhs))
  if (length(lhs) > 1)
    lhs <- lhs[-1]
  if (length(lhs) == 1) {
    do.call(`=`, list(lhs[[1]], rhs), envir=frame)
    return(invisible(NULL)) 
  }
  if (is.function(rhs) || is(rhs, 'formula'))
    rhs <- list(rhs)
  if (length(lhs) > length(rhs))
    rhs <- c(rhs, rep(list(NULL), length(lhs) - length(rhs)))
  for (i in 1:length(lhs))
    do.call(`=`, list(lhs[[i]], rhs[[i]]), envir=frame)
  return(invisible(NULL)) 
}

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
