import time, threading


class PID:

    def __init__(self, P=0., I=0., D=0., set_point = 0, sample_time = 0.001):

        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.lock = threading.Lock()
        self.memory = [self.Kp, self.Ki, self.Kd]

        self.set_point = set_point

        self.sample_time = sample_time
        self.current_time = time.time()
        self.last_time = self.current_time

        self.PTerm = 0
        self.ITerm = 0
        self.DTerm = 0

        self.last_error = 0

        #windup guard

        self.windup_guard = 20

        self.output = 0

        self.max_output = 0



    def update(self, feedback):

        error = self.set_point - feedback
      #po co sprawdza� czas skoro p�tla ma okre�lon� cz�stotliwo��?
        self.current_time = time.time()

        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error
        self.PTerm = error
        self.ITerm += error * delta_time
        if (self.ITerm > self.windup_guard):
            self.ITerm = self.windup_guard
        elif (self.ITerm < -self.windup_guard):
            self.ITerm = -self.windup_guard
        if(delta_time ==0):
            self.DTerm = 0
        else:
            self.DTerm = delta_error / delta_time
        #save last data for next calculation
        self.last_time = self.current_time
        self.last_error = error
        with self.lock:
            self.output = self.Kp * self.PTerm + self.Ki * self.ITerm + self.Kd * self.DTerm
        # na testy, zeby predkosc sie nie zwiekszyla za bardzo
        if self.output > self.max_output:
            self.output = self.max_output

        return self.output


    def setKp(self, Kp):
        self.Kp = Kp

    def setKi(self, Ki):
        self.Ki = Ki

    def setKd(self, Kd):
        self.Kd = Kd

    def setSampleTime(self, sample_time):
        self.sample_time = sample_time

    def setWindup(self, windup):
        self.windup_guard = windup

    def setPIDCoefficients(self, Kp, Ki, Kd):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        print(Kp, Ki, Kd)

    def getPIDCoefficients(self):
        return [self.Kp, self.Ki, self.Kd]

    def setMaxOutput(self, max_output):
        self.max_output = max_output

    def setSampleTime(self, sample_time):
        self.sample_time = sample_time

    def getError(self):
        return self.error

    def setSetPoint(self, set_point):
        self.set_point = set_point

    def getSetPoint(self):
        return self.set_point

    def turn_off(self):
        self.Kp = 0
        self.Ki = 0
        self.Kd = 0
        self.memory = [self.Kp, self.Ki, self.Kd]

    def turn_on(self):
        self.Kp = self.memory[0]
        self.Ki = self.memory[1]
        self.Kd = self.memory[2]

