
from communicationThreads.Simulation.simulationClient import SimulationClient
from tools.PID.pid_thread import PIDThread
from controlThread.controlThread import ControlThread
import threading


class SimulationControlThread(ControlThread):
    def __init__(self):
        self.client = SimulationClient()
        self.PIDThread = PIDThread(self.client)
        self.mode = "stable"

    def arm(self):
        self.PIDThread.arm()
        pass

    def disarm(self):
        self.PIDThread.disarm()
        

    def setControlMode(self, mode):
        print("mode changed to:"+str(mode))
        self.PIDThread.mode = mode
        self.PIDThread.heading_setpoint = self.PIDThread.client.get_sample('yaw')
        self.mode = mode

    def getControlMode(self):
        return self.mode

    def moveForward(self, value):
        self.PIDThread.forward = value

    #temporary methods



#mode 0
    def setAngularVelocity(self, roll,pitch, yaw):
        self.PIDThread.vel_pitch_setpoint = pitch
        self.PIDThread.vel_roll_setpoint = roll
        self.PIDThread.vel_yaw_setpoint = yaw
    def vertical(self, arg):
        self.PIDThread.vertical = arg

#mode 1
    def setAngle(self, roll, pitch):
        self.PIDThread.SetAttitude(roll, pitch)

    def setHeading(self, heading):
        self.PIDThread.SetHeading(heading)
    
    def setDepth(self, depth):
        self.PIDThread.SetDepth(depth)

#comunication stuff

    def getHeading(self):
        return self.PIDThread.GetHeading()

    def getImuData(self):
        ret = self.PIDThread.GetAttitude()
        ret+=self.PIDThread.acc
        ret+=self.PIDThread.gyro
        ret+=self.PIDThread.mag
        ret.append(self.getDepth())
        
        return ret
    
    def getDepth(self):
        return self.PIDThread.GetDepth()

    def getMotors(self):
        return self.PIDThread.GetMotors()

#PID stuff
    def setPIDs(self, arg):
        self.PIDThread.SetPIDs(arg)
       
    def getPIDs(self):
        return self.PIDThread.GetPIDs()

