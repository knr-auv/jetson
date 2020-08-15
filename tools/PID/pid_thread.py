#this thread is handling odroid/stm task it is controlled by jetson_simulation
import threading
import logging
import time, random
from tools.PID.PID import PID

class PIDThread(threading.Thread):
    """Thread class that sets up all PID controllers and updates motors velocity after calculating difference
    between actual position and set_point position
    roll
    pitch
    yaw
    depth - not used yet because of lack of depth feedback in AUV
    velocity - not used because of lack of velocity feedback in AUV"""

    def __init__(self, client):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
        self.roll_PID = PID()
        self.pitch_PID = PID()
        self.yaw_PID = PID()
        self.setMotors = client._run_motors
        self.client = client
        #gui stuff
        self.active = True
        self.isActive = False
        self.m = [0,0,0,0,0]
        self.yaw = 0
        self.vertical = 0
        self.forward = 0
        self.interval = 0.01
        self.roll_diff, self.pitch_diff, self.yaw_diff = 0, 0, 0
  
        
        max_sum_output = 18000.
        self.roll_PID.setMaxOutput(max_sum_output / 4)
        self.pitch_PID.setMaxOutput(max_sum_output / 4)
        self.yaw_PID.setMaxOutput(max_sum_output / 4)
        self.pid_motors_speeds_update = [0, 0, 0, 0, 0]
        self.imu_data = [0,0,0,0]

    def run(self): 
        logging.debug("STARTING PID THREAD")
        self.isActive=True
        self.active = True
        while self.active:
            now = time.time()
            self.client.catch_sample()
            roll = self.client.get_sample('roll')
            pitch = self.client.get_sample('pitch')
            yaw = self.client.get_sample('yaw')
            depth = self.client.get_sample('depth')
            self.imu_data = [roll, pitch,yaw,depth]
            self.roll_diff = self.roll_PID.update(roll)
            self.pitch_diff = self.pitch_PID.update(pitch)
            self.yaw_diff = self.yaw_PID.update(yaw)  # maybe try:  'gyro_raw_x' 'gro_proc_x'

            with self.lock:
                self.roll_control()
                self.pitch_control()
                self.yaw_control()
                self.pad_control()
                self.update_motors()

            if(time.time()-now>self.interval):
                logging.debug("PID loop timeout")
            else:
                time.sleep((self.interval-time.time()+now))
        logging.debug("STOPING PID THREAD")

        with self.lock:
            self.disable_motors()
            self.active = True
            self.isActive = False

    def disable_motors(self):
        self.setMotors([0,0,0,0,0])

    def roll_control(self):
        #exactly like in pitch...
        self.pid_motors_speeds_update[4] += self.roll_diff
        self.pid_motors_speeds_update[2] -= self.roll_diff

    def pitch_control(self):
        #since motors 3 and 4 are inverted in simulaton motor controler '+,+,-' is vertical control...
        self.pid_motors_speeds_update[2] -= self.pitch_diff  # * 2 / 3
        self.pid_motors_speeds_update[4] -= self.pitch_diff  # * 2 / 3
        self.pid_motors_speeds_update[3] -= self.pitch_diff

    def yaw_control(self):
        self.pid_motors_speeds_update[0] += self.yaw_diff
        self.pid_motors_speeds_update[1] -= self.yaw_diff

    def pad_control(self):
        #motorsPAD = [self.vertical+self.yaw+self.forward, self.vertical-self.yaw+self.forward,self.vertical,self.vertical,self.vertical]
        self.pid_motors_speeds_update[0] += self.yaw+self.forward
        self.pid_motors_speeds_update[1] += self.forward-self.yaw
        self.pid_motors_speeds_update[2] -= self.vertical
        self.pid_motors_speeds_update[3] += self.vertical
        self.pid_motors_speeds_update[4] -= self.vertical


    def update_motors(self):
        for i in range(len(self.pid_motors_speeds_update)):
            if self.pid_motors_speeds_update[i]>1000:
                self.pid_motors_speeds_update[i]=1000
            elif self.pid_motors_speeds_update[i]<-1000:
                self.pid_motors_speeds_update[i]=-1000
        
        self.m =self.pid_motors_speeds_update
     
        self.setMotors(self.pid_motors_speeds_update)
        self.pid_motors_speeds_update = [0] * 5



#GUI methods


    def getMotors(self):
        def map(input,in_min,in_max,out_min,out_max):
            return int((input-in_min)*(out_max-out_min)/(in_max-in_min)+out_min)
        ret=[]
        for i in self.m:
            ret.append(map(i, -1000,1000,0,100))
        return ret

    def setPIDs(self, arg):
        if arg[0] == 'roll':
            self.roll_PID.setPIDCoefficients(arg[1],arg[2],arg[3])
        elif arg[0] == 'pitch':
            self.pitch_PID.setPIDCoefficients(arg[1],arg[2],arg[3])
        elif arg[0] == 'yaw':
            self.yaw_PID.setPIDCoefficients(arg[1],arg[2],arg[3])
        elif arg[0] == 'all':
            self.roll_PID.setPIDCoefficients(arg[1],arg[2],arg[3])
            self.pitch_PID.setPIDCoefficients(arg[4],arg[5],arg[6])
            self.yaw_PID.setPIDCoefficients(arg[7],arg[8],arg[9])

    def getPIDs(self,arg):
        if arg=='roll':
            return [arg]+self.roll_PID.getPIDCoefficients()
        elif arg == 'pitch':
            return [arg]+self.pitch_PID.getPIDCoefficients()
        elif arg == 'yaw':
            return [arg]+self.yaw_PID.getPIDCoefficients()
        elif arg == 'all':
            return [arg]+self.roll_PID.getPIDCoefficients()+self.pitch_PID.getPIDCoefficients()+self.yaw_PID.getPIDCoefficients()