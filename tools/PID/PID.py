import threading
import time


class PID:
    def __init__(self, P=0.0, I=0.0, D=0.0, L=0.0):

        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.Kl = L
        self.lock = threading.Lock()

        self.PTerm = 0
        self.ITerm = 0
        self.DTerm = 0

        self.last_error = 0

        # windup guard

        self.windup_guard = 20

        self.output = 0

        self.max_output = 0
        self.current_time = 0
        self.last_time = 0

    def update(self, feedback, setPoint):
        error = setPoint - feedback
        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        self.last_time = self.current_time
        self.PTerm = error

        self.ITerm += error * delta_time
        if self.ITerm > self.windup_guard:
            self.ITerm = self.windup_guard
        elif self.ITerm < -self.windup_guard:
            self.ITerm = -self.windup_guard
        if delta_time == 0:
            self.DTerm = 0
        else:
            self.DTerm = (error - self.last_error) / delta_time

        self.last_time = self.current_time

        self.output = self.Kp * self.PTerm + self.Ki * self.ITerm + self.Kd * self.DTerm
        # na testy, zeby predkosc sie nie zwiekszyla za bardzo
        # if self.output > self.max_output:
        # self.output = self.max_output

        self.last_error = error
        return self.output

    def setWindup(self, windup):
        self.windup_guard = windup

    def setPIDCoefficients(self, Kp, Ki, Kd, Kl):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.Kl = Kl
        print(Kp, Ki, Kd, Kl)

    def getPIDCoefficients(self):
        return [self.Kp, self.Ki, self.Kd, self.Kl]

    def setMaxOutput(self, max_output):
        self.max_output = max_output
