library("TSP")

concorde_path("C:\\cygwin32\\home\\Witko PC\\tsp")

# Path to file of distances between stations
dist.file <- "data/distances.csv"

# Read file from disk and turn into a matrix
df <- read.csv(dist.file)
mat <- as.matrix(df)
rownames( mat ) <- colnames( mat )

# Ensure that the matrix is symmetric
mat[lower.tri(mat)] = t(mat)[lower.tri(mat)]

# Create a TSP object to be solved
tsp <- TSP( mat )

# Add a dummy station with zero distance to all other stations
tsp <- insert_dummy( tsp, label = "cut" )

# Solve for the optimal tour
ctour <- solve_TSP( tsp, method = "concorde" )

# Print the length of the tour
tour_length( ctour )

# Reassemble the tour around the cut point
path <- cut_tour( ctour, "cut" )

# Print the ordered labels
labels( path )





