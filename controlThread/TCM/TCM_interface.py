from tools.Delegate import Delegate
from controlThread.TCM.TCM_Protocol import TCM_Protocol

class TCM_Interface:
    __attitude_Q = [0] * 4
    __attitude_E = [3] * 3
    __mag = [0] * 3
    __angular_velocity = [0] * 3
    __battery_level = [0] * 2
    __temperature = [0] * 2
    __hummidity = [0] * 1
    __desired_angular_velocity = [0] * 3
    __desired_attitude_Q = [0] * 4
    __actuator_outputs = [0] * 8
    __stick_inputs = [0] * 16

    keys = [
        "attitude_Q",
        "attitude_E",
        "mag"
        "angular_velocity",
        "battery_level",
        "TCM_temperature",
        "TCM_hummidity",
        "desired_angular_velocity",
        "desired_attitude_Q",
        "actuator_outputs"
        "stick_inputs"
    ]

    # Invoke after receiving new data, as argument pass a dictionary with keys defined above.
    # You can subscribe to this callback, but it is prefered to use NewDataNotification
    NewDataCallback = Delegate()

    # Prefered way of notifying about new data.
    # It takes no arguments, but it might be used for settings flag
    # F.e: NewDataNotyfication+=lambda: NewDataDlag = true
    NewDataNotification = Delegate()
    DisarmNotificator = Delegate()
    ArmNotificator = Delegate()

    def __init__(self):
        self.NewDataCallback += self.__update_local_var
        self.NewDataCallback += self.NewDataNotification
        self.DisarmNotificator = Delegate()
        self.ArmNotificator = Delegate()

    def __update_local_var(self, data):
        self.__attitude_Q = data["attitude_Q"]
        self.__attitude_E = data["attitude_E"]
        self.__mag = data["mag"]
        self.__angular_velocity = data["angular_velocity"]
        self.__battery_level = data["battery_level"]
        self.__temperature = data["TCM_temperature"]
        self.__hummidity = data["TCM_hummidity"]
        self.__desired_angular_velocity = data["desired_angular_velocity"]
        self.__desired_attitude_Q = data["desired_attitude_Q"]
        self.__actuator_outputs = data["actuator_outputs"]
        self.__stick_inputs = data["stick_inputs"]



    # Interface to control the boat
    def HandleSteeringInput(self, data):
        pass

    # common methods for mode 1 and 2. Control mode is either 0 -> manual or 1-> autonomy
    def arm(self, controlMode=0):
        self.ArmNotificator()

    def disarm(self):
        self.DisarmNotificator()

    def getControlMode(self):
        return self.__mode

    def setControlMode(self, mode):
        self.__mode = mode

    def moveForward(self, value):
        pass

    # mode 0 -> zadane s¹ prêdkoœci k¹towe -> ³ódka siê sama nie poziomuje

    def setAngularVelocity(self, roll, pitch, yaw):
        self.__angular_vel_setpoint = [roll, pitch, yaw]

    def vertical(self, arg):
        pass

    # mode 1 -> ³ódka siê poziomuje
    def setAttitude(self, roll, pitch, yaw):
        self.__attitude_setpoint = [roll, pitch, yaw]

    def setDepth(self, depth):
        self.__depth_setpoint = depth

    # lepiej braæ setpoint ni¿ dane z ³ódki
    def getAttitudeSetpoint(self):
        return self.__attitude_setpoint

    def getDepthSetpoint(self):
        return self.__depth_setpoint

    def getAngularVelocitySetpoint(self):
        return self.__angular_vel_setpoint

    def getPosition(self):
        return self.__position

    def getAttitude(self):
        return self.__attitude

    def getDepth(self):
        return self.__depth

    def getIMUData(self):
        pass

    def getPosData(self):
        ret = []
        ret += self.__position
        ret += self.__velocity
        ret += self.__acceleration
        return ret

    def getMotors(self):
        return self.__motors

    def getBattery(self):
        return self.__battery

    def setPIDs(self, arg):
        pass

    def getPIDs(self):
        pass
