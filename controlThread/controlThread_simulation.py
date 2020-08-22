
#this should be some kind of thread.
#it controll pid thread and simulation client
from comunicationThreads.simulationClient import SimulationClient
from tools.PID.pid_thread import PIDThread
from controlThread.controlThread import controlThread
import threading


class simulationConnection(controlThread):
    def __init__(self, comunicator):
        super().__init__(comunicator)
        self.client = SimulationClient()
        self.PIDThread = PIDThread(self.client)
        pass

    def arm(self):
        x = threading.Thread(target=self.PIDThread.run)
        x.start()
        
        self.comunicator.confirmArm()
        pass

    def disarm(self):
        self.PIDThread.active = False
        self.comunicator.confirmDisarm()
        

    def setControlMode(self, mode):
        print(mode)
        pass

    def moveForward(self, value):
        self.PIDThread.forward = value

    #temporary methods
    def vertical(self, value):
        self.PIDThread.vertical = value
    def yaw(self, value):
        self.PIDThread.yaw = value

#mode 1
    def setAngularVelocity(self, pitch, roll, yaw):
        pass

#mode 2
    def yawVelocity(self, yaw):
        pass

    def setAngle(self, roll, pitch):
        self.PIDThread.roll_PID.set_point = roll
        self.PIDThread.pitch_PID.set_point = pitch

    #if we are in mode supported by magnetometer we can set heading
    def setHeading(self, heading):
        #here we set heading... north, east, west etc.
        pass
    
    def setDepth(self, depth):
        pass

#comunication stuff

    def getHeading(self):
        #return heading
        pass

    def getImuData(self):
        return self.PIDThread.imu_data
    
    def getDepth(self):
        pass

    def getMotors(self):
        return self.PIDThread.getMotors()

#PID stuff
    def setPIDs(self, arg):
        self.PIDThread.setPIDs(arg)
       
    def getPIDs(self, arg):
        return self.PIDThread.getPIDs(arg)

    def storePIDs(self):
        pass