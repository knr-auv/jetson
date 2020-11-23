
#class for controlling AUV
#all methods should be implemented acording to communicationThreads

class ControlThread:    
    def __init__(self):
        pass

    def arm(self):
        pass

    def disarm(self):
        pass

    #PID thread should constantly integrate ACC data to obtain position. 
    def setPosition(self, x,y,z):
        pass

#here we are implementing 2 controll methods 
    def setControlMode(self, mode):
        #mode 1 --> 'acro' (cant find better name). --> in this mode our boat is trying to maintain orientation. We are controlling it by setting angular velocity
        #mode 2 --> 'stable' --> here boat will try to be leveled. We can set roll/pitch setpoints
        pass
    def getControlMode(self):
        pass
    def moveForward(self, value):
        #lets say that 0 is neutral, -1000 is max backward and 1000 is max forward
        pass

#how to control boat in mode 1
    #velocity is in deg/sec. 
    def setAngularVelocity(self, roll,pitch, yaw):
        pass

#how to control boat in mode 2
    def setAngle(self, pitch, roll):
        #this function should send angle setpoints to odro/stm
        pass
    #add value to heading in deg
    def addHeading(self, val):
        pass

    def setHeading(self, heading):
        #here we set heading... north, east, west etc.
        pass
    #add value to depth
    def addDepth(self, val):
        pass

    def setDepth(self, depth):
        pass

#methods for obtaining data from jetson/stm/simulation
    def getHeading(self):
        #return heading
        pass
    #attitude mag gyro acc
    def getImuData(self):
        #return euler angles + angular velocity
        pass

    def getPosition(self):
        #returns position
        pass
    
    def getDepth(self):
        #return depth
        pass

    def getMotors(self):
        pass

    def getHumidity(self):
        pass

#PID stuff
    def setPIDs(self):
        pass

    def getPIDs(self):
        #return P, I, D
        pass
#in case of any problem with humidity, IMU or whatever we can pass it to GUI or Autonomy thread with this callback.
#callbacks
    def IMU_problem(self):
        pass

