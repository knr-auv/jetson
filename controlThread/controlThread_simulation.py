
from communicationThreads.Simulation.simulationClient import SimulationClient
from tools.PID.pid_thread import PIDThread
from controlThread.controlThread import controlThread
import threading


class SimulationControlThread(controlThread):
    def __init__(self):
        self.client = SimulationClient()
        self.PIDThread = PIDThread(self.client)

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
        self.PIDThread.roll_setpoint = roll
        self.PIDThread.pitch_setpoint = pitch


    def setHeading(self, heading):
        self.PIDThread.heading_setpoint = heading
        pass
    
    def setDepth(self, depth):
        self.PIDThread.depth_setpoint= depth

#comunication stuff

    def getHeading(self):
        return self.PIDThread.imu_data[2]

    def getImuData(self):
        return self.PIDThread.imu_data
    
    def getDepth(self):
        return self.PIDThread.imu_data[3]

    def getMotors(self):
        return self.PIDThread.getMotors()

#PID stuff
    def setPIDs(self, arg):
        self.PIDThread.setPIDs(arg)
       
    def getPIDs(self, arg):
        print(arg)
        val = self.PIDThread.getPIDs(arg)
        print(val)
        return self.PIDThread.getPIDs(arg)

