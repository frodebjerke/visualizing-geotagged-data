'''
Created on Oct 28, 2012

@author: fredo
'''
class ConnectionMode:
    WALK = 0
    TRAIN = 1
    BIKE = 2
    MOTOR_VEHICLE = 3

    ALL = [WALK, BIKE, TRAIN, MOTOR_VEHICLE]
    

class MapConnectionTrace:
    def __init__(self):
        self.connections = []
    def addconnection(self, connection):
        self.connections.append(connection)
    def finish(self):
        self.connections.reverse()

    def gettotalcost(self):
        cost = 0
        for connection in self.connections:
            cost += connection.cost
        return cost

    def tomappointtrack(self):
        pointtrack = MapPointTrace()
        if not self.connections:
            return pointtrack
        pointtrack.addpoint(self.connections[0].mapsource)
        for connection in self.connections:
            pointtrack.addpoint(connection.maptarget)
        return pointtrack

    def reset(self):
        self.connections = []

    def getlastconnection (self):
        if self.connections:

            return self.connections[-1]
        else:
            return None

    def __iter__(self):
        for connection in self.connections:
            yield connection

    def __str__(self):
        if not self.connections:
            return ""
        strconnections = []
        strconnections.append(str(self.connections[0].mapsource.id))
        for connection in self.connections:
            label = str(connection.maptarget.id)
            if hasattr(connection, "video"):
                label = "(%d)%d" % (connection.video.id, connection.maptarget.id)
            strconnections.append(label)
        return ">".join(strconnections)

class MapPointTrace:
    def __init__(self):
        self.points = []
    def addpoint(self, point):
        self.points.append(point)

    def __iter__(self):
        for point in self.points:
            yield point