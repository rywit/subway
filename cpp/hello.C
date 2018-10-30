// C++ program to illustrate the 
// iterators in vector 
#include <iostream> 
#include <vector> 
#include <set>
#include <map>
#include <stack>
#include <fstream>
#include <string>
#include <sstream>
#include <cstring>
#include <cstdlib>

using namespace std; 

class Station {
  int stationNumber;
  vector<Station *> rideStations;
  vector<Station *> transStations;

  public:
  
  Station(int id) {
    stationNumber = id;
    rideStations = vector<Station *>();
    transStations = vector<Station *>();  }

  const int getStationNumber() {
    return stationNumber;
  }

  void addRideStation(Station * ride) {
    rideStations.push_back(ride);
  }

  void addTransferStation(Station * trans) {
    transStations.push_back(trans);
  }

  vector<Station *> getRideStations() {
    return rideStations;
  }

  vector<Station *> getTransferStations() {
    return transStations;
  }

  bool hasLinks() {
    return rideStations.size() > 0;
  }
};
  
class Path { 

  bool * visited;
  Station * curStation;
  bool justTransferred;
  int numVisited;

  public: 
      
  //Default Constructor 
  Path(Station * cur) { 
    curStation = cur;
    justTransferred = true;

    visited = new bool[473]();
    visited[cur->getStationNumber()] = true;

    numVisited = 1;
  } 

  // Constructor for cloning
  Path(Station * cur, bool trans, bool * visit, int num) { 
    curStation = cur;
    justTransferred = trans;

    visited = new bool[473]();
    memcpy(visited, visit, 473);

    visited[cur->getStationNumber()] = true;

    numVisited = num + 1;
  }

  // Copy constructor
  Path( const Path& other ) {
    curStation = other.curStation;
    justTransferred = other.justTransferred;
    numVisited = other.numVisited;

    visited = new bool[473];
    memcpy(visited, other.visited, 473);
  }

  ~Path() {
    delete []visited;
  }

  Station * getCurrentStation() {
    return curStation;
  }

  bool didJustTransfer() {
    return justTransferred;
  }

  bool hasVisited(Station * station) {
    return visited[station->getStationNumber()];
  }

  int getNumVisited() {
    return numVisited;
  }

  Path clone(Station * newStation, bool didTransfer) {
    return Path(newStation, didTransfer, visited, numVisited);
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

  const int getNumPaths() {
    return numPaths;
  }

  const int getMaxLength() {
    return maxLength;
  }
};

Results calcLongest(Station * startStation)
{

  stack<Path> q;

  // Build starting path
  q.push(Path(startStation));

  int numChecked = 0;
  int maxLength = 0;

  while ( !q.empty() ) {

    Path curPath = q.top();
    q.pop();

    numChecked++;

    if ( curPath.getNumVisited() > maxLength ) {
      maxLength = curPath.getNumVisited();
    }

    Station * curStation = curPath.getCurrentStation();

    vector<Station *> rideStations = curStation->getRideStations();

    for ( vector<Station *>::iterator it = rideStations.begin(); it != rideStations.end(); it++ ) {
      Station * rideStation = *it;

      if ( !curPath.hasVisited(rideStation) ) {
        q.push(curPath.clone(rideStation, false));
      }
    }

    if ( !curPath.didJustTransfer() ) {

      vector<Station *> transStations = curStation->getTransferStations();

      for ( vector<Station *>::iterator it = transStations.begin(); it != transStations.end(); it++ ) {
        Station * transStation = *it;

        if ( !curPath.hasVisited(transStation) ) {
          q.push(curPath.clone(transStation, true));
        }
      }
    }
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

  for ( int i = 1; i <= 472; i++ ) {
    stations.insert(pair<int, Station *>(i, new Station(i)));
  }

  loadRideConnections( "/u1/rwitko/links.csv", stations );
  loadTransferConnections( "/u1/rwitko/trans.csv", stations );

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
    }
  }

  cout << "Total checked: " << totalChecked << " Max: " << totalLongest << "\n";

  return 0; 
} 
