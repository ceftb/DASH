class Locations(object):
    def __init__(self):
        self.object_locations = dict()
        self.locations = set()
        self.distances = dict()

    def addLocation(self, loc):
        self.locations.add(loc)
    
    def setLocation(self, object, loc):
        self.object_locations[object] = loc

    def setDistance(self, loc1, loc2, dist):
        self.distances[(loc1, loc2)] = dist
        
    def getDistance(self, loc1, loc2):
        # find shortest path b/w loc1 and loc2
        return 0
