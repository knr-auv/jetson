import numpy as np
import math
import tools.Logger as Logger
from tools.Delegate import Delegate
import time


class Controller:
    '''
    Controller class is written with the purpose of controlling Okon
    Functions arm and disarm are used to armaming and disarmaming the boat
    They don't take any parameters
    Functions starting with __ are used only inside the class. I won't describe them

    move_forward and move_backward are used to move our boat forward and backward
    they take velocity as a parameter (0-1000)
    stop function - set velocity of boat to 0 (don't take parameter)

    turn functions are used to change orientation of boat.
    They take angle as a parameter (angle must be in degrees)

    Mainly function
    swim_to_xyz - Okon is swimming to the choosen point. In this version after arriving
    to xyz Okon sets orientation to (0,0,0). In next versions it will be facing the gate or etc.
    This function takes as a parameters list of coordinates [x,y,z] and optional error. In default it is set to 0.3
    ([x,y,z],error)

    test_swim is used to show how controller works. User have to remember to use sleep function
    between swim_to_xyz calls. Otherwise it won't work because of "turbulece"

    '''

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

    def __get_current_position(self):
        self.current_position=[self.controlThread.getPosition()[0],self.controlThread.getPosition()[1],self.controlThread.getPosition()[2]]

    def __set_orientation(self, roll,pitch, yaw):
        self.controlThread.setAttitude(roll,pitch,yaw)

    def __get_current_orientation(self):
        self.current_orientation=self.controlThread.getAttitude()

    def move_forward(self, velocity):
        self.controlThread.moveForward(velocity)

    def move_backward(self, velocity):
        self.controlThread.moveForward(-velocity)

    def stop(self):
        self.controlThread.moveForward(0)
        self.controlThread.moveForward(0)

    def __set_depth(self, depth):
        self.controlThread.setDepth(depth)

    def __get_motors(self):
        self.motors=self.controlThread.getMotors()

    def turn_right(self,angle):
        self.__get_current_orientation()
        self.__set_orientation(0,0,self.current_orientation[2]+angle)
        time.sleep(1.5)

    def turn_left(self,angle):
        self.__get_current_orientation()
        self.__set_orientation(0,0,self.current_orientation[2]-angle)
        time.sleep(1.5)

    def __xyz_callback(self):
        # funkcja do wywołania callbacku po osiągnieciu pozycji xyz
        self.xyz_reached=True
        self.xyz_reached_callback.Invoke(self.xyz_reached)

    def swim_to_xyz(self,reference_position,error=0.3):
        self.__get_current_position()
        position_error = np.subtract(reference_position,[self.current_position[0], self.current_position[1], self.current_position[2]])
        self.__set_depth(reference_position[2])
        # trzeba ustalic w ktora strone i o ile mamy skrecac
        angle = math.atan2(position_error[1], position_error[0])  # kat o który należy się obrócić
        if (angle <= math.pi and angle > 0):
            if math.degrees(angle)>=177:
                self.turn_right(177)
                reference_position[1]=reference_position[1]+0.4
            else:
                self.turn_right(math.degrees(angle))
            self.stop()
        elif (angle < 0 and angle >= -math.pi):
            if math.degrees(angle)<=-177:
                self.turn_left(177)
                reference_position[1] = reference_position[1] - 0.4
            else:
                self.turn_left(math.degrees(abs(angle)))
            self.stop()
        velocity=700
        time.sleep(1.5)
        self.__get_current_position()
        position_error = np.subtract(reference_position,
        [self.current_position[0], self.current_position[1], self.current_position[2]])
        angle = math.atan2(position_error[1], position_error[0])
        while (self.xyz_reached != True):
            self.move_forward(velocity)
            self.__get_current_orientation()
            self.__get_current_position()
            position_error = np.subtract(reference_position, self.current_position)
            orientation_error=self.current_orientation[2]-math.degrees(angle)
            if angle>0:
                if orientation_error>0.05:
                    self.turn_left(2)
                elif orientation_error<-0.05:
                    self.turn_right(2)
            elif angle<0:
                if orientation_error>0.05:
                    self.turn_left(2)
                elif orientation_error<0.05:
                    self.turn_right(2)
            time.sleep(0.1)
            if(math.sqrt(position_error[0]*position_error[0]+position_error[1]*position_error[1])<error):
                self.stop()
                Logger.write("Point XYZ reached", "controller")
                self.__xyz_callback()
        self.xyz_reached=False
        self.__set_orientation(0,0,0)
    def test_swim(self):
        self.swim_to_xyz([3,5,1])
        self.stop()
        time.sleep(3)
        self.swim_to_xyz([3,0,1],0.4)
        time.sleep(3)
        self.swim_to_xyz([0,-3,1],0.4)
        time.sleep(3)
        self.swim_to_xyz([0, 0, 1],0.4)
