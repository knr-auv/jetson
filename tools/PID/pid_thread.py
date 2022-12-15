import math
import threading
import time

import tools.PID.Quaternion as q
from tools.PID.PID import PID


class PIDThread:
    """PID controller for okon. For more informations refer to readme"""

    def __init__(self, client, data_receiver):
        self.setMotors = client._run_motors
        self.client = client
        self.data_receiver = data_receiver
        self.armed = False

        self.motors = [0] * 8

        self.pad_active = True

        self.mode = 0  # niech 0 -> stabilny , 1-> acro
        self.controlMode = 0  # 0--> manual, 1-->autonomy
        # control setpoints
        self.ref_attitude = q.Quaternion([1, 0, 0, 0])
        self.ref_heading = 0
        self.ref_depth = 0
        # these are ignored in manual modes
        self.forward = 0

        # sensors info
        self.mag = [1, 1, 1]
        self.gyro = [0] * 3
        self.acc = [0] * 3
        self.depth = 0

        # Attitude info
        self.position = [0, 0, 0]
        self.velocity = [0] * 3
        self.attitude = q.Quaternion([1, 0, 0, 0])

        # PIDS
        self.roll_PID = PID()
        self.pitch_PID = PID()
        self.yaw_PID = PID()
        self.depth_PID = PID()

        # manual control stuff
        self.pad_input = [0] * 5

        self.x = threading.Thread(target=self.PIDLoop)
        self.x.start()

    def arm(self, mode):
        self.controlMode = mode
        self.armed = True
        self.velocity = [0] * 3
        self.position = [0] * 3

    def disarm(self):
        self.armed = False
        m = [0] * 5
        self.setMotors(m)

    def auto_stable(self):
        ref_vel = list()
        t = 50
        error = self.attitude.conj() * self.ref_attitude
        ref_vel.append(error.b * t * self.roll_PID.Kl)
        ref_vel.append(error.c * t * self.pitch_PID.Kl)
        ref_vel.append(error.d * t * self.yaw_PID.Kl)
        depth_diff = -self.depth_PID.update(self.depth, self.ref_depth)

        return ref_vel, self.forward, depth_diff

    def manual_acro(self):
        t = 50
        ref_vel = list()
        roll, pitch, yaw, forward, depth = self.pad_input
        if roll == pitch == yaw == 0:
            error = self.attitude.conj() * self.ref_attitude
            ref_vel.append(error.b * t * self.roll_PID.Kl)
            ref_vel.append(error.c * t * self.pitch_PID.Kl)
            ref_vel.append(error.d * t * self.yaw_PID.Kl)

            depth_diff = depth
            self.ref_depth = self.depth
        else:
            self.ref_attitude = self.attitude
            ref_vel.append(-roll * 2)
            ref_vel.append(-pitch)
            ref_vel.append(yaw)
            depth_diff = depth

        return ref_vel, forward, depth_diff

    def manual_stable(self):
        ref_vel = list()
        t = 50
        roll, pitch, yaw, forward, depth = self.pad_input

        roll_ref = -roll * 30 / 1000
        pitch_ref = -pitch * 30 / 1000

        ref_attitude = q.fromEuler(roll_ref, pitch_ref, self.ref_heading)
        error = self.attitude.conj() * ref_attitude
        ref_vel.append(error.b * t * self.roll_PID.Kl)
        ref_vel.append(error.c * t * self.pitch_PID.Kl)

        if yaw != 0:
            ref_vel.append(yaw)
            self.ref_heading = self.attitude.toEuler()[2]
        else:
            ref_vel.append(error.d * t * self.yaw_PID.Kl)
        if depth == 0:
            depth_diff = -self.depth_PID.update(self.depth, self.ref_depth)
        else:
            depth_diff = depth
            self.ref_depth = self.depth

        return ref_vel, forward, depth_diff

    def PIDLoop(self):
        last_data = 0
        data_t = 1 / 10
        loop_T = 1 / 100
        sleep_time = loop_T / 10  # sounds reasonable...
        loop_time = 0
        last_time = time.time()
        self.ref_depth = self.client.get_sample("depth")
        while True:
            dt = time.time() - last_time
            if dt >= loop_T:
                self.client.catch_sample()
                s = self.client.get_pos()
                self.acc = self.client.get_sample("acc")
                self.gyro = self.client.get_sample("gyro")
                self.depth = self.client.get_sample("depth")
                at = self.client.get_sample("attitude")
                self.attitude = q.fromEuler(*at)

                try:
                    new_pos = [s["pos"]["z"], s["pos"]["x"], s["pos"]["y"]]

                    for i in range(3):
                        # self.position[i]+=self.velocity[i]
                        self.velocity[i] = (new_pos[i] - self.position[i]) / dt
                    self.position = new_pos

                except:
                    pass
                """
                for i in range(3):
                    self.position[i]+=self.velocity[i]*dt
                    self.velocity[i]+=self.acc[i]*dt
                """
                if self.controlMode == 0:  # manual control
                    if self.mode == 0:
                        ref_ang_vel, forward, vertical = self.manual_stable()
                    elif self.mode == 1:
                        ref_ang_vel, forward, vertical = self.manual_acro()
                elif self.controlMode == 1:  # autonomy controll
                    ref_ang_vel, forward, vertical = self.auto_stable()
                    pass

                # pid base
                if self.armed:
                    roll_diff = self.roll_PID.update(self.gyro[0], ref_ang_vel[0])
                    pitch_diff = self.pitch_PID.update(self.gyro[1], ref_ang_vel[1])
                    yaw_diff = self.yaw_PID.update(self.gyro[2], ref_ang_vel[2])
                    self.controll_motors(roll_diff, pitch_diff, yaw_diff, vertical, forward)

                last_time = time.time()
            else:
                if time.time() - last_data >= data_t:
                    data = [
                        self.attitude.toEuler(),
                        self.gyro.copy(),
                        self.acc.copy(),
                        self.mag.copy(),
                        self.depth,
                        self.gyro.copy(),
                        self.position.copy(),
                        self.velocity.copy(),
                        self.acc.copy(),
                        self.motors.copy(),
                    ]
                    self.data_receiver(data)
                    last_data = time.time()
                else:
                    time.sleep(sleep_time)

    def controll_motors(self, roll_error, pitch_error, yaw_error, depth_error, forward):
        motors = [0] * 8

        def control_roll():
            motors[4] -= roll_error
            motors[2] += roll_error

        def control_pitch():
            motors[2] -= pitch_error
            motors[4] -= pitch_error
            motors[3] += pitch_error

        def control_yaw():
            motors[0] += forward + yaw_error
            motors[1] -= -forward + yaw_error

        def control_depth():
            motors[2] += depth_error
            motors[3] += depth_error
            motors[4] += depth_error

        motors[7] = 700
        control_roll()
        control_pitch()
        control_yaw()
        control_depth()
        for i in range(5):
            if abs(motors[i]) > 1000:
                motors[i] = motors[i] / abs(motors[i]) * 1000
        self.motors = motors
        self.setMotors(motors)

    # GUI methods

    def HandleSteeringInput(self, data):
        self.pad_input = data
        self.pad_active = True

    def SetDepth(self, depth):
        self.ref_depth = depth

    def SetAttitude(self, roll, pitch, yaw):
        self.roll_ref = roll
        self.pitch_ref = pitch
        self.yaw_ref = yaw
        self.ref_attitude = q.fromEuler(roll, pitch, yaw)

    def moveForward(self, value):
        self.forward = value

    def SetHeading(self, heading):

        b = self.attitude.toEuler()
        self.ref_attitude = q.Quaternion.fromEuler(math.degrees(b[2]), math.degrees(b[1]), heading)
        self.yaw_ref = heading

    def SetPosition(self, position):
        # x,y,z
        self.position = position

    def GetDepth(self):
        return self.depth

    def GetAttitude(self):
        return self.attitude.toEuler()

    def GetHeading(self):
        ret = Quaternion(self.attitude)
        ret.quat2eul()
        return ret[0]
        pass

    def GetPosition(self):
        return self.position

    def GetMotors(self):
        def map_value(input, in_min, in_max, out_min, out_max):
            return int((input - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

        ret = []
        for i in self.m:
            ret.append(map_value(i, -1000, 1000, 0, 100))
        return ret

    def SetPIDs(self, arg):
        self.roll_PID.setPIDCoefficients(arg[0], arg[1], arg[2], arg[3])
        self.pitch_PID.setPIDCoefficients(arg[4], arg[5], arg[6], arg[7])
        self.yaw_PID.setPIDCoefficients(arg[8], arg[9], arg[10], arg[11])
        self.depth_PID.setPIDCoefficients(arg[12], arg[13], arg[14], arg[15])

    def GetPIDs(self):
        return (
            self.roll_PID.getPIDCoefficients()
            + self.pitch_PID.getPIDCoefficients()
            + self.yaw_PID.getPIDCoefficients()
            + self.depth_PID.getPIDCoefficients()
        )
