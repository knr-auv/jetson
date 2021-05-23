from communicationThreads.Simulation.simulationClient import SimulationClient
from tools.PID.pid_thread import PIDThread
from controlThread.controlThread import ControlThread
import threading


class SimulationControlThread(ControlThread):
   
    def __init__(self):
        ControlThread.__init__(self)
        self.client = SimulationClient()
        self.PIDThread = PIDThread(self.client, self.HandleNewData)

    def HandleSteeringInput(self, data):
        self.PIDThread.HandleSteeringInput(data)

#common methods for mode 1 and 2
    def disarm(self):
        super().disarm()
        self.PIDThread.disarm()

    def arm(self, mode = 0):
        super().arm()
        self.PIDThread.arm(mode)

    def setControlMode(self, mode):
        super().setControlMode(mode)
        print("mode changed to:"+str(mode))
        self.PIDThread.mode = mode
        self.PIDThread.heading_setpoint = self.PIDThread.client.get_sample('yaw')
        self.mode = mode

    def moveForward(self, value):
        self.PIDThread.moveForward(value)
    def moveSideway(self,value):
        self.PIDThread.moveSideway(value)
#mode 0
    def setAngularVelocity(self, roll, pitch, yaw):
        super().setAngularVelocity(roll, pitch, yaw)
        self.PIDThread.velocity_setpoints = [roll, pitch,yaw]

    #TODO zachowanie głębokości w tym trybie
    def vertical(self, arg):
        self.PIDThread.vertical = arg

#mode 1
    def setAttitude(self, roll, pitch, yaw):
        super().setAttitude(roll, pitch, yaw)
        self.PIDThread.SetAttitude(roll, pitch,yaw)
    
    def setDepth(self, depth):
        super().setDepth(depth)
        self.PIDThread.SetDepth(depth)

    def setPIDs(self, arg):
        self.PIDThread.SetPIDs(arg)
       
    def getPIDs(self):
        return self.PIDThread.GetPIDs()

    def HandleNewData(self, data):
        attitude, gyro, acc, mag, depth, angular_velocity, position, velocity, acceleration, motors = data
        val = {}
        for i in self.keys:
            val[i]=eval(i)
        self.NewDataCallback.Invoke(val)
