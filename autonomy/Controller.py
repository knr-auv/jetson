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
    swim_to_xyz - Okon is swimming to the choosen point.
    This function takes as a parameters list of coordinates [x,y,z] and optional error and velocity. In default error = 0.5, velocity =700
    ([x,y,z],error,velocity). Okon coordinate system: https://github.com/knr-auv/jetson-v2/blob/develop/okonCoordinates.png?raw=true

    test_swim and test_swim_2 are used to show how controller works. User have to remember to use sleep function
    between swim_to_xyz calls. Otherwise it may not work properly because of "turbulence"

    If you want to set orientation of a stationary boat use set_heading function. Takes the angle as an argument (0-360) measured clockwise.
    Boat cannot be turned 180 degrees due to some kind of bug. If you choose (177-183) boat will rotate endlessly.

    set_depth function is used to set depth of boat. Take 1 argument. Value of argument must be positive

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
        self.controlThread.arm(1)

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
        self.move_backward(1000)
        self.controlThread.moveForward(0)

    def set_depth(self, depth):
        self.controlThread.setDepth(depth)

    def __get_motors(self):
        self.motors=self.controlThread.getMotors()

    def turn_right(self,angle):
        self.__get_current_orientation()
        self.__set_orientation(0,0,self.current_orientation[2]+angle)

    def turn_left(self,angle):
        self.__get_current_orientation()
        self.__set_orientation(0,0,self.current_orientation[2]-angle)

    def set_heading(self,angle):
        if (angle>=180 and angle<=360):
            self.turn_left(abs(angle-360))
        elif(angle>=0):
            self.turn_right(angle)
        self.stop()

    def __xyz_callback(self):
        # funkcja do wywołania callbacku po osiągnieciu pozycji xyz
        self.xyz_reached=True
        self.xyz_reached_callback.Invoke(self.xyz_reached)

    def __calculate_direction(self,reference_position):
        self.__get_current_position()
        self.__get_current_orientation()
        position_error=np.subtract(reference_position,self.current_position)
        angle=math.atan2(position_error[1],position_error[0])
        angle=angle-math.radians(self.current_orientation[2])
        if angle>math.pi:
            angle=angle-2*math.pi
        elif angle<-math.pi:
            angle=angle+2*math.pi
        return angle,position_error

    def swim_to_xyz(self,reference_position,error=0.5,velocity=700):
        self.set_depth(-reference_position[2])
        angle,position_error=self.__calculate_direction(reference_position)
        self.move_forward(velocity)
        while (self.xyz_reached!=True):
            if (math.sqrt(position_error[0] * position_error[0] + position_error[1] * position_error[1]) < error):
                self.stop()
                Logger.write("Point XYZ reached", "controller")
                self.__xyz_callback()
            if (angle <= math.pi and angle > 0):
                self.turn_right(math.degrees(angle))
            elif (angle < 0 and angle >= -math.pi):
                self.turn_left(math.degrees(abs(angle)))
            angle, position_error = self.__calculate_direction(reference_position)
            time.sleep(0.1)
        self.__get_current_orientation()
        self.__get_current_position()
        Logger.write("pozycja: "+str(self.current_position),"swim to xyz")
        Logger.write("orientacja: "+str(self.current_orientation),"swim to xyz")
        self.xyz_reached = False

    def test_swim(self):
        self.swim_to_xyz([0,5,-1],0.4)
        time.sleep(3)
        Logger.write("kolejny odcinek","autonomia")
        self.swim_to_xyz([5,5,-1],0.4)
        time.sleep(3)
        Logger.write("kolejny odcinek", "autonomia")
        self.swim_to_xyz([5, -5, -1],0.4)
        time.sleep(3)
        Logger.write("kolejny odcinek", "autonomia")
        self.swim_to_xyz([0, -5, -1], 0.4)
        time.sleep(3)
        Logger.write("kolejny odcinek", "autonomia")
        self.swim_to_xyz([0,0, -1], 0.4)

    def test_swim_2(self):
        Logger.write("pierwszy odcinek", "autonomia")
        self.swim_to_xyz([1, 2, -1], 0.4)
        time.sleep(3)
        Logger.write("kolejny odcinek", "autonomia")
        self.swim_to_xyz([5, 1, -1], 0.4)
        time.sleep(3)
        Logger.write("kolejny odcinek", "autonomia")
        self.swim_to_xyz([5, 5, -1], 0.4)
        time.sleep(3)
        Logger.write("kolejny odcinek", "autonomia")
        self.swim_to_xyz([2, 5, -1], 0.4)
        time.sleep(3)
        Logger.write("kolejny odcinek", "autonomia")
        self.swim_to_xyz([2, 8, -1], 0.4)
        time.sleep(3)
        Logger.write("kolejny odcinek", "autonomia")
        self.swim_to_xyz([7, 12, -1], 0.4)
        time.sleep(3)
        Logger.write("kolejny odcinek", "autonomia")
        self.swim_to_xyz([6, 13, -1], 0.4)
