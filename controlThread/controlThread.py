
#class for controlling AUV
#all methods should be implemented acording to communicationThreads
class comunicator:
    #class for sending data to gui.
     def __init__(self):
         self.confirmArm=None
         self.confirmDisarm =None
         self.autonomyMsg = None

class controlThread:    
    def __init__(self, comunicator = comunicator()):
        self.comunicator = comunicator
        self.padData = None
    def arm(self):
        pass

    def disarm(self):
        pass

#here we are implementing 2 controll methods 
    def setControlMode(self, mode):
        #mode 1 --> 'acro' (cant find better name). --> in this mode our boat is trying to maintain orientation. We are controlling it by setting angular velocity
        #mode 2 --> horizontal --> here boat will try to be leveled. We can set roll/pitch setpoints
        #while being in horizontal mode we should be able to enable/disable barometer and magnetometer support. 
        pass
    def getControlMode(self):
        pass
    def moveForward(self, value):
        #lets say that 500 is neutral, 0 is max backward and 1000 is max forward (almost like in pwm)
        pass

#how to control boat in mode 1
    #velocity is in deg/sec. 
    def setAngularVelocity(self, roll,pitch, yaw):
        pass

#how to control boat in mode 2
    #yaw is still controlled by setting angular velocity
    def setYawVelocity(self, yaw):
        pass

    def setAngle(self, pitch, roll):
        #this function should send angle setpoints to odro/stm
        pass

    #if we are in mode supported by magnetometer we can set heading
    def setHeading(self, heading):
        #here we set heading... north, east, west etc.
        pass
    
    def setDepth(self, depth):
        pass

#methods for obtaining data from jetson/stm/simulation
    def getHeading(self):
        #return heading
        pass

    def getImuData(self):
        #return euler angles + angular velocity
        pass
    
    def getDepth(self):
        #return depth
        pass

    def getMotors(self):
        pass

#PID stuff
    def setPIDs(self, arg):
        #arg is "yaw", "roll" etc...
        pass

    def getPIDs(self, arg):
        #return P, I, D
        pass

    def storePIDs(self):
    #method should copy pids from stm and copy them to file. (if stm has eeprom support it should save them there and in file)
        pass
