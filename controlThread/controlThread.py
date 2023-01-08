from tools.Delegate import Delegate


class ControlThread:
    """Base class for comunication with Okon controller"""

    # data that can be obtained from controller
    __mode = "stable"
    __acc = [0] * 3
    __mag = [0] * 3
    __gyro = [0] * 3
    __depth = 0
    __attitude = [0] * 3
    __angular_velocity = [0] * 3

    __position = [0] * 3
    __acceleration = [0] * 3
    __velocity = [0] * 3
    __motors = [0] * 5
    __battery = [0] * 2

    __depth_setpoint = 0
    __attitude_setpoint = [0] * 3
    __angular_vel_setpoint = [0] * 3
    keys = [
        "attitude",
        "gyro",
        "acc",
        "mag",
        "depth",
        "angular_velocity",
        "position",
        "velocity",
        "acceleration",
        "motors",
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
        self.__attitude = data["attitude"]
        self.__gyro = data["gyro"]
        self.__acc = data["acc"]
        self.__mag = data["mag"]
        self.__depth = data["depth"]
        self.__position = data["position"]
        self.__velocity = data["velocity"]
        self.__angular_velocity = data["angular_velocity"]
        self.__acceleration = data["acceleration"]
        self.__motors = data["motors"]

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

    # mode 0 -> zadane są prędkości kątowe -> łódka się sama nie poziomuje

    def setAngularVelocity(self, roll, pitch, yaw):
        self.__angular_vel_setpoint = [roll, pitch, yaw]

    def vertical(self, arg):
        pass

    # mode 1 -> łódka się poziomuje
    def setAttitude(self, roll, pitch, yaw):
        self.__attitude_setpoint = [roll, pitch, yaw]

    def setDepth(self, depth):
        self.__depth_setpoint = depth

    # lepiej brać setpoint niż dane z łódki
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
