#this thread is handling odroid/stm task it is controlled by jetson_simulation
import threading
import logging
import time, random
from tools.PID.PID import PID
import numpy as np
import math

class PIDThread:
    def __init__(self, client):
        self.setMotors = client._run_motors
        self.client = client
        self.x = threading.Thread(target = self.PIDLoop)
        self.x.start()
        self.armed = False
        self.position = [0,0,0]
        self.motors = [0]*6

        self.attitude = [0]*4
        self.gyro = [0]*3
        self.acc = [0]*3

    def arm(self):
        self.armed = True

    def disarm(self):
        self.armed=False

    def PIDLoop(self):
        while(1):
            #gyro and acc will be obtained from client
            self.gyro = [1,2,3]
            self.acc = [1,2,3] #Ax,Ay,Az
            q_from_acc = [1,1,1,1]#=[-Ay/sqrt(2(1-Az)), -sqrt(0.5*(1-Az)), 0, -Ax/sqrt(2(1-Az))]
            #self.attitude = .... integrate gyro
            self. attitude = 0.9*self.attitude+0.1*q_from_acc
            if(self.armed==True):
                #calculate pids
                #set motors
                pass

    def controll_motors(self, roll_error, pitch_error, yaw_error, depth_error):
        motors = [0]*5
        def control_roll(self):
            pass
        def control_pitch(self):
            pass
        def control_yaw(self):
            pass
        def control_depth(self):
            pass
        self.motors=motors
        self.setMotors(motors)
#GUI methods
    def setPosition(self,position):
        #x,y,z
        self.position = position

    def getPosition(self):
        return self.position

    def getMotors(self):
        def map(input,in_min,in_max,out_min,out_max):
            return int((input-in_min)*(out_max-out_min)/(in_max-in_min)+out_min)
        ret=[]
        for i in self.m:
            ret.append(map(i, -1000,1000,0,100))
        return ret

    def setPIDs(self, arg):
        self.roll_PID.setPIDCoefficients(arg[1],arg[2],arg[3],arg[4])
        self.pitch_PID.setPIDCoefficients(arg[5],arg[6],arg[7],arg[8])
        self.yaw_PID.setPIDCoefficients(arg[9],arg[10],arg[11],arg[12])
        self.depth_PID.setPIDCoefficients(arg[13], arg[14], arg[15],arg[16])

    def getPIDs(self):
        return [arg]+self.roll_PID.getPIDCoefficients()+self.pitch_PID.getPIDCoefficients()+self.yaw_PID.getPIDCoefficients()+self.depth_PID.getPIDCoefficients()