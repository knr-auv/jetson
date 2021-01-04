import numpy as np
import math
import tools.Logger as Logger
from tools.Delegate import Delegate
import time


class Controller:

    def __init__(self, controlthread):
        self.controlThread = controlthread
        self.xyz_reached_callback = Delegate()
        self.current_position = [0] * 3  # x y z
        self.current_orientation = [0] * 3  # roll pitch yaw
        self.motors=[0]*5
        self.xyz_reached=False
        Logger.write("DEBUG CONTROLER ACTIVE", "controller")
    def arm(self):
        self.controlThread.arm()
    def disarm(self):
        self.controlThread.disarm()
    def get_current_position(self):
        self.current_position=[self.controlThread.getPosition()[0],self.controlThread.getPosition()[1],self.controlThread.getPosition()[2]]
    def set_orientation(self, roll,pitch, yaw):
        self.controlThread.setAttitude(roll,pitch,yaw)
    def get_current_orientation(self):
        self.current_orientation=self.controlThread.getAttitude()
    def move_forward(self, value):
        self.controlThread.moveForward(value)
    def stop(self):
        self.controlThread.moveForward(0)
        self.controlThread.moveForward(-1000)
        self.controlThread.moveForward(0)
    def set_depth(self, depth):
        self.controlThread.setDepth(depth)
    def get_motors(self):
        self.motors=self.controlThread.getMotors()
    def turn_right(self,angle):
        self.get_current_orientation()
        error=1.5
        refference_orientation=self.current_orientation
        self.set_orientation(0,0,10)
        while True:
            self.get_current_orientation()
            orinetation=self.current_orientation
            orientation_difference=abs(orinetation[2]-refference_orientation[2])
            if(abs(angle-orientation_difference)<error):
                self.set_orientation(0, 0,math.radians(angle))
                break
            time.sleep(0.1)
        self.stop()
    def plyn_i_stop(self):
        self.move_forward(700)
        time.sleep(10);
        print("stop")
        self.controlThread.moveForward(0)

    def turn_left(self,angle):
        self.get_current_orientation()
        error = 1.5
        refference_orientation = self.current_orientation
        self.set_orientation(0,0,-10)
        while True:
            self.get_current_orientation()
            orinetation = self.current_orientation
            orientation_difference = abs(orinetation[2] - refference_orientation[2])
            if (abs(angle - orientation_difference) < error):
                self.set_orientation(0, 0, -math.radians(angle))
                break
            time.sleep(0.1)
        self.stop()
    def xyz_callback(self):
        # funkcja do wywołania callbacku po osiągnieciu pozycji xyz
        self.xyz_reached=True
        self.xyz_reached_callback.Invoke(self.xyz_reached)

    def swim(self,reference_position):
        error=0.3
        self.get_current_position()
        position_error = np.subtract(reference_position,[self.current_position[0], self.current_position[1], self.current_position[2]])
        self.set_depth(reference_position[2])
        # trzeba ustalic w ktora strone i o ile mamy skrecac
        angle = math.atan2(position_error[1], position_error[0])  # kat o który należy się obrócić
        print("kat: "+str(angle))
        if (angle <= math.pi and angle > 0):
            self.turn_right(math.degrees(angle))
            self.stop()
            self.controlThread.setAttitude(0, 0, -0.6)
        elif (angle < 0 and angle >= -math.pi):
            self.turn_left(math.degrees(abs(angle)))
            self.stop()
            self.controlThread.setAttitude(0, 0, 0.6)
        self.get_current_orientation()
        print(self.current_orientation)
        time.sleep(3)
        velocity=700
        self.move_forward(velocity)
        while (self.xyz_reached != True):
            self.get_current_orientation()
            self.get_current_position()
            self.get_motors()
            position_error = np.subtract(reference_position, self.current_position)
            print("orientacja")
            print(self.current_orientation[2])
            print("pozycja")
            print(self.current_position)
            print("silniki")
            print(self.motors)
            time.sleep(0.2)
            if(abs(position_error[0])<error and abs(position_error[1])<error):#tutaj moze byc jeszcze norma wetkora ewentualnie
                self.stop()
                self.xyz_callback()