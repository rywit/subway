// C++ program to illustrate the 
// iterators in vector 
#include <iostream> 
#include <vector> 
#include <set>
#include <map>
  
using namespace std; 

class Station {
  int stationNumber;
  vector<Station *> rideStations;
  vector<Station *> transStations;

  public:
  
  Station(int id) {
    stationNumber = id;
    rideStations = vector<Station *>();
    transStations = vector<Station *>();
  }

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
};
  
class Path 
{ 
  set<Station*> visited;
  Station * curStation;
  bool justTransferred;

  public: 
      
  //Default Constructor 
  Path(Station * cur) { 
    curStation = cur;
    justTransferred = true;
    visited.insert(cur);
  } 

  // Constructor for cloning
  Path(Station * cur, bool trans, set<Station *> visit) { 
    curStation = cur;
    justTransferred = trans;
    visited = visit;
    visited.insert(cur);
  }

  Station * getCurrentStation() {
    return curStation;
  }

  bool didJustTransfer() {
    return justTransferred;
  }

  bool hasVisited(Station * station) {
    return visited.find(station) != visited.end();
  }

  Path clone(Station * newStation, bool didTransfer) {
    return Path(newStation, didTransfer, visited);
  }

}; 

int main() 
{ 
  map<int, Station *> stations;

  for ( int i = 1; i <= 472; i++ ) {
    stations.insert(pair<int, Station *>(i, new Station(i)));
  }

  // Insert ride connections
  Station * from = stations[200];
  Station * to = stations[202];

  from->addRideStation(to);

  Station * s = new Station(200);
  Station * s2 = new Station(202);

  Path p(s);

  Path p2 = p.clone(s2, false);

  cout << p2.getCurrentStation() << "\n";

  return 0; 
} 

