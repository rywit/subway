// C++ program to illustrate the
// iterators in vector
#include <iostream>
#include <vector>
#include <set>
#include <map>
#include <stack>
#include <fstream>
#include <string>
#include <bitset>
#include <sstream>
#include <cstring>
#include <cstdlib>

using namespace std;

class Location {

  unsigned long long loc[8];

  public:

  Location(const int & bin, const int & bit) {

    memset( loc, 0, sizeof( loc ) );

    loc[bin] |= ( 1 << bit );
  }

  // copy constructor
  Location( Location & other ) {
    memcpy( loc, other.loc, sizeof( loc ) );
  }

  void set( const int & bin, const int & bit ) {
    loc[bin] |= ( 1 << bit );
  }

  const bool match( const int & bin, const int & bit ) {
    return loc[bin] & ( 1 << bit );
  }
};

class Station {
  int stationNumber;

  vector<Station *> rideStations;
  vector<Station *> transStations;

  unsigned int numRides;
  unsigned int numTrans;

  int _bin;
  int _bit;

  public:

  Station(int id) {
    stationNumber = id;
    rideStations = vector<Station *>();
    transStations = vector<Station *>();
    numRides = 0;
    numTrans = 0;

    _bin = id / 64;
    _bit = id % 64;
  }

  const int & getStationNumber() const {
    return stationNumber;
  }

  const int & getBin() const {
    return _bin;
  }

  const int & getBit() const {
    return _bit;
  }

  void addRideStation(Station * ride) {
    rideStations.push_back(ride);
    numRides++;
  }

  void addTransferStation(Station * trans) {
    transStations.push_back(trans);
    numTrans++;
  }

  const unsigned int getNumRides() {
    return numRides;
  }

  const unsigned int getNumTransfers() {
    return numTrans;
  }

  const vector<Station *>& getRideStations() const {
    return rideStations;
  }

  const vector<Station *>& getTransferStations() const {
    return transStations;
  }

  const bool hasLinks() const {
    return rideStations.size() > 0;
  }
};

class Path {

  Location * visited;
  Station * curStation;
  Station * prevStation;
  bool justTransferred;
  int numVisited;

  public:

  //Default Constructor
  Path(Station * cur) {
    curStation = cur;
    prevStation = 0;
    justTransferred = true;
    visited = new Location(cur->getBin(), cur->getBit());
    numVisited = 1;
  }

  Path( Location * v, Station * station, Station * prev, const bool trans, const int num ) {
    curStation = station;
    prevStation = prev;
    justTransferred = trans;
    numVisited = num;

    visited = new Location( *v );
    visited->set( curStation->getBin(), curStation->getBit() );
  }

  ~Path() {
    delete visited;
  }

  Path * clone( Station * newStation, const bool trans ) const {
    return new Path(visited, newStation, curStation, trans, numVisited + 1);
  }

  Station * getCurrentStation() const {
    return curStation;
  }

  Station * getPreviousStation() const {
    return prevStation;
  }

  const bool didJustTransfer() const {
    return justTransferred;
  }

  const bool hasVisited(Station * station) const {

    if ( station == prevStation ) {
      return true;
    }

    return visited->match(station->getBin(), station->getBit());
  }

  const int getNumVisited() const {
    return numVisited;
  }
};

class Results {

  int numPaths;
  int maxLength;

  public:

  Results(int paths, int len) {
    numPaths = paths;
    maxLength = len;
  }

  const int & getNumPaths() const {
    return numPaths;
  }

  const int & getMaxLength() const {
    return maxLength;
  }
};

Results calcLongest(Station * startStation)
{

  Path * q[100] = {};
  int idx = 0;

  // Build starting path
  q[ 0 ] = new Path( startStation );
  idx++;

  int numChecked = 0;
  int maxLength = 0;

  while ( idx > 0 ) {

    Path * curPath = q[ idx - 1 ];
    idx--;

    numChecked++;

    if ( numChecked % 100000000 == 0 ) {
      cout << "Checked " << numChecked << " (queue: " << idx << ")\n";
    }

    if ( curPath->getNumVisited() > maxLength ) {
      maxLength = curPath->getNumVisited();
    }

    Station * curStation = curPath->getCurrentStation();

    const vector<Station *> & rideStations = curStation->getRideStations();
    const unsigned int & numRides = curStation->getNumRides();

    for ( unsigned int i = 0; i < numRides; i++ ) {
      if ( !curPath->hasVisited( rideStations[i] ) ) {
        q[idx++] = curPath->clone( rideStations[i], false );
      }
    }

    if ( !curPath->didJustTransfer() ) {

      const vector<Station *> & transStations = curStation->getTransferStations();
      const unsigned int & numTrans = curStation->getNumTransfers();

      for ( unsigned int i = 0; i < numTrans; i++ ) {
        if ( !curPath->hasVisited( transStations[i] ) ) {
          q[idx++] = curPath->clone( transStations[i], true );
        }
      }
    }

    delete curPath;
  }

  return Results(numChecked, maxLength);
}

vector< vector<int> > parseCSV(string fileName) {

  ifstream file(fileName.c_str());

  vector< vector<int> > results;

  string line;

  // Iterate through each line and split the content using delimeter
  while ( getline( file, line ) ) {

    stringstream ss(line);
    vector<int> res;

    while (ss.good()) {
      string substr;
      getline( ss, substr, ',' );

      res.push_back( atoi( substr.c_str() ) );
    }

    results.push_back( res );
  }

  // Close the File
  file.close();

  return results;
}

void loadRideConnections(string fileName, map<int, Station *> stations) {

  vector< vector<int> > links = parseCSV( fileName );

  for ( vector< vector<int> >::iterator it = links.begin(); it != links.end(); it++ ) {
    vector<int> ids = *it;

    Station * station1 = stations[ids[0]];
    Station * station2 = stations[ids[1]];

    station1->addRideStation(station2);
  }
}

void loadTransferConnections(string fileName, map<int, Station *> stations) {

  vector< vector<int> > links = parseCSV( fileName );

  for ( vector< vector<int> >::iterator it = links.begin(); it != links.end(); it++ ) {
    vector<int> ids = *it;

    Station * station1 = stations[ids[0]];
    Station * station2 = stations[ids[1]];

    station1->addTransferStation(station2);
  }
}

int main()
{
  map<int, Station *> stations;

  for ( int i = 1; i <= 477; i++ ) {
    stations.insert(pair<int, Station *>(i, new Station(i)));
  }

  loadRideConnections( "/u1/rwitko/links.csv", stations );
  loadTransferConnections( "/u1/rwitko/trans.csv", stations );

  cout << "Finished loading links and transfers\n";

  int totalChecked = 0;
  int totalLongest = 0;

  for ( map<int, Station *>::iterator it = stations.begin(); it != stations.end(); it++ ) {
    Station * station = it->second;

    if ( station->hasLinks() ) {
      Results res = calcLongest( station );
      cout << "Station ID: " << it->first << " Num checked: " << res.getNumPaths() << " Longest: " << res.getMaxLength() << "\n";

      totalChecked += res.getNumPaths();

      if ( res.getMaxLength() > totalLongest ) {
        totalLongest = res.getMaxLength();
      }

      break;
    }
  }

  cout << "Total checked: " << totalChecked << " Max: " << totalLongest << "\n";

  return 0;
}
