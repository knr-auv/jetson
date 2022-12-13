import threading

from communicationThreads.Simulation.simulationClient import SimulationClient
from controlThread.controlThread import ControlThread
from tools.PID.pid_thread import PIDThread


class SimulationControlThread(ControlThread):
    def __init__(self, client):
        ControlThread.__init__(self)
        self.client = client
        # self.PIDThread = PIDThread(self.client, self.HandleNewData)

    def HandleSteeringInput(self, data):
        print("Handling steering...")
        # self.PIDThread.HandleSteeringInput(data)

    # common methods for mode 1 and 2
    def disarm(self):
        super().disarm()
        print("Handling steering...")
        self.client.okon.disarm_motors()
        # self.PIDThread.disarm()

    def arm(self, mode=0):
        super().arm()
        self.client.okon.arm_motors()
        # self.PIDThread.arm(mode)

    def setControlMode(self, mode):
        super().setControlMode(mode)
        print("mode changed to:" + str(mode))
        # self.PIDThread.mode = mode
        # self.PIDThread.heading_setpoint = self.PIDThread.client.get_sample("yaw")
        # self.mode = mode
        self.mode = "stable"
        self.client.okon.setMode("stable")

    def moveForward(self, value):
        self.client.okon.set_stable_vel(z=value)
        # self.PIDThread.moveForward(value)

    # mode 0
    def setAngularVelocity(self, roll, pitch, yaw):
        super().setAngularVelocity(roll, pitch, yaw)
        print("set angular velocity")
        # TODO: implement angular velocity
        #
        # self.PIDThread.velocity_setpoints = [roll, pitch, yaw]

    # TODO zachowanie głębokości w tym trybie
    def vertical(self, arg):
        print("vertical")
        # self.PIDThread.vertical = arg

    # mode 1
    def setAttitude(self, roll, pitch, yaw):
        super().setAttitude(roll, pitch, yaw)
        self.client.okon.set_stable_rot(x=pitch, y=yaw, z=roll)
        # self.PIDThread.SetAttitude(roll, pitch, yaw)

    def setDepth(self, depth):
        super().setDepth(depth)
        self.client.okon.set_depth(depth)
        # self.PIDThread.SetDepth(depth)

    def setPIDs(self, arg):
        print("set pid")
        # self.PIDThread.SetPIDs(arg)

    def getPIDs(self):
        print("Get pids")
        return None
        # return self.PIDThread.GetPIDs()

    def HandleNewData(self, data):
        attitude, gyro, acc, mag, depth, angular_velocity, position, velocity, acceleration, motors = data
        val = {}
        for i in self.keys:
            val[i] = eval(i)
        self.NewDataCallback.Invoke(val)
