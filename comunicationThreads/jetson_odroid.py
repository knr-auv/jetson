
#this should be some kind of thread. It should talk with odroid. 
#I assume that imu and motors are connected to odroid 
#server should receive data from stm/odroid all the time. All methods used for sending data will be used from other threads.
class odroidConnection():
    
    def __init(self):
        pass
    #enabling/disabling pid thread and motors
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

    def moveForward(self, value):
        #lets say that 500 is neutral, 0 is max backward and 1000 is max forward (almost like in pwm)
        pass

#how to control boat in mode 1
#pls keep in mind that this mode will allow us to perform flips and other fancy stuff so it is very important
    #velocity is in deg/sec. 
    def setAngularVelocity(self, pitch, roll, yaw):
        pass


#how to control boat in mode 2
    #yaw is still controlled by setting angular velocity
    def yawVelocity(self, yaw):
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

    def getHeading(self):
        #return heading
        pass

    def getImuData(self):
        #return euler angles + angular velocity
        pass
    
    def getDepth(self):
        #return depth
        pass

    def setPIDs(self, arg, P, I , D):
        #arg is "yaw", "roll" etc...
        pass

    def getPIDs(self, arg):
        #return P, I, D
        pass

    def storePIDs(self):
    #method should copy pids from stm and copy them to file. (if stm has eeprom support it should save them there and in file)
        pass