from tools.PID.pid_thread import PIDThread
from communicationThreads.Simulation.simulationClient import SimulationClient
from tools.Delegate import Delegate
from controlThread.controlThread_simulation import SimulationControlThread as sct
from controlThread.controlThread import ControlThread as ct
import numpy as np


class Controller:
    def __init__(self):
        self.client = SimulationClient()
        self.xyz_reached_callback = Delegate()
        self.current_position = [0] * 3  # x y z
        self.current_orientation = [0] * 3  # roll pitch yaw
        self.xyz_reached=False

    def arm(self):
        sct.arm()

    def disarm(self):
        sct.disarm()

    def get_current_position(self):
        self.current_position=ct.getPosition()

    def set_orientation(self, roll,pitch, yaw):
        sct.setAttitude(roll,pitch,yaw)

    def get_current_orientation(self):
        self.current_orientation=ct.getAttitudeSetpoint()

    def stop(self):
        self.move_forward(0)

    def move_forward(self, value):
        sct.moveForward(value)

    def move_backward(self, value):
        sct.moveForward(-value)#tutaj nie jestem pewien czy to zadziała

    def setDepth(self, depth):
        sct.setDepth(depth)

    #skrecanie odbywa sie przez obrot wokol osi z czyli kat yaw
    #nie wiem tylko jak jest zorientowany ukłąd, więc mozliwe ze trzeba zmienic + z - w turn_right/turn_left
    def turn_right(self,angle):
        self.set_orientation(self.current_orientation[0], self.current_orientation[1], self.current_orientation[3]+angle)

    def turn_left(self,angle):
        self.set_orientation(self.current_orientation[0], self.current_orientation[1], self.current_orientation[3]-angle)

    def xyz_callback(self):
        # funkcja do wywołania callbacku po osiągnieciu pozycji xyz
        self.xyz_reached=True
        self.xyz_reached_callback.Invoke(self.xyz_reached)

    def swim_to_xyz(self, reference_position):
        error=0.01
        while(self.xyz_reached != True):
            self.get_current_position()
            position_error = np.subtract(reference_position, self.current_position)
            self.setDepth(reference_position[2])
            ##obliczenie kąta i kierunku skretu
            ## nic nie ma bo nie wiem jak z ukłądem współrzednych




            if(abs(position_error[0])<error and abs(position_error[1])<error and abs(position_error[2])<error):
                self.xyz_callback()


