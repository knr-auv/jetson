class Protocol(object):
     class FROM_GUI:
        REQUEST = 0x01
        class REQUEST_MSG:
            PID = 0x01
            CONFIG = 0x02

        STEERING = 0x02
        class STEERING_MSG:
            PAD = 0x01
            MODE = 0x02

        CONTROL = 0x03
        class CONTROL_MSG:
            ARM = 0x01
            DISARM = 0x02
            START_AUTONOMY=0x03
            STOP_AUTONOMY=0x04
            START_TELEMETRY=0x05

        SETTINGS = 0x04
        class SETTINGS_MSG:
            PID = 0x01

     class TO_GUI:

        TELEMETRY = 0x01
        class TELEMETRY_MSG:
            MOTORS = 0x01
            IMU = 0x02
            POSITION =0x03
            BATTERY = 0x04
            HUMMIDITY = 0x05
            TEMPERATURE = 0X06



        REQUEST_RESPONCE = 0x02
        class REQUEST_RESPONCE_MSG:
            PID = 0x01
            ARMED = 0x02
            DISARMED =0x03


        AUTONOMY = 0x03
        class AUTONOMY_MSG:
            DETECTION = 0x01
            AUTONOMY_STARTED = 0x02
            AUTONOMY_STOPED = 0x03

        STATUS = 0x04
        class STATUS_MSG:
            LOGGER = 0x01
            SENSOR_STATUS = 0x02
            TASK_MANAGER = 0x03




