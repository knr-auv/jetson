import tools.PID.Quaternion as q
import threading
import logging
import time, random
from tools.PID.PID import PID
import numpy as np
import math

class PIDThread:
    def __init__(self, client, data_receiver):
        self.setMotors = client._run_motors
        self.client = client

        self.data_receiver = data_receiver
        self.armed = False
        self.position = [0,0,0]
        self.velocity = [0]*3
        self.motors = [0]*6
        self.mag = [1,1,1]
        self.forward = 0
        self.direct_depth = False
        self.attitude = q.Quaternion([1,0,0,0])
        self.gyro = [0]*3
        self.acc = [0]*3
        self.roll_ref = 0
        self.pitch_ref =0
        self.yaw_ref =0
        self.depth=0
        self.ref_depth=0
        self.vertical = 0
        self.roll_diff = 0
        self.pitch_diff = 0
        self.yaw_diff = 0
        self.depth_diff = 0

        self.ref_ang_vel = [0]*3
        self.ref_attitude = q.Quaternion([1,0,0,0])
        self.velocity_setpoints = [0]*3
        self.mode = 0 #niech 0 -> stabilny , 1-> acro
        self.pad_input = False
        self.roll_PID = PID()
        self.pitch_PID = PID()
        self.yaw_PID = PID()
        self.depth_PID = PID()

        self.x = threading.Thread(target = self.PIDLoop)
        self.x.start()

    def arm(self):
        self.armed = True

    def disarm(self):
        self.armed=False
        m = [0]*5
        self.setMotors(m)

    def PIDLoop(self):
        last_data = 0
        data_t = 1/10

        loop_T = 1/20
        sleep_time = loop_T/10 #sounds reasonable...
        loop_time = 0
        last_time =0
     
        self.ref_depth = self.client.get_sample('depth')


        while(1):
            dt = time.time()-last_time
            if(dt>=loop_T):
                self.client.catch_sample()
                s = self.client.get_pos()
                self.acc = self.client.get_sample('acc')
                self.gyro = self.client.get_sample('gyro')
                self.depth=self.client.get_sample('depth')
                at = self.client.get_sample('attitude')
                
                self.attitude = q.fromEuler(*at)
                error = self.attitude.conj()*self.ref_attitude
                
                #TODO position integration
                try:
                    new_pos = [s["pos"]["x"],s["pos"]["y"],s["pos"]["z"]]
                    for i in range(3):
                       # self.position[i]+=self.velocity[i]
                       self.velocity[i]=new_pos[i]-self.position[i]
                    self.position= new_pos
                except:
                    pass
                if self.mode == 0 and self.pad_input:
                    self.pad_input = False
                elif self.mode==0:
                    #enlarging error to avoid L parameter being very big
                    t = 50
                    self.ref_ang_vel[0]= error.b*t*self.roll_PID.Kl
                    self.ref_ang_vel[1]= error.c*t*self.pitch_PID.Kl
                    
                    if self.yaw_ref != 0:
                        self.ref_ang_vel[2] = self.yaw_ref
                        self.ref_attitude = q.fromEuler(self.roll_ref, self.pitch_ref, at[2])
                    else:                   
                        self.ref_ang_vel[2]= error.d*t*self.yaw_PID.Kl

                    if self.vertical!=0:
                        self.direct_depth = True
                        self.ref_depth = self.depth
                    else:
                        self.direct_depth = False

                #pid base
                if(self.armed):
                    self.roll_diff=self.roll_PID.update(self.gyro[0],self.ref_ang_vel[0])
                    self.pitch_diff=self.pitch_PID.update(self.gyro[1],self.ref_ang_vel[1])
                    self.yaw_diff = self.yaw_PID.update(self.gyro[2],self.ref_ang_vel[2])

                    if(self.direct_depth):
                        self.depth_diff = self.vertical
                    else:
                        self.depth_diff = self.depth_PID.update(self.depth, self.ref_depth*self.depth_PID.Kl)

                    self.controll_motors(self.roll_diff,self.pitch_diff,self.yaw_diff,self.depth_diff)

                last_time = time.time()
            else:
                if(time.time()-last_data>=data_t):
                    data = [self.attitude.toEuler(), self.gyro, self.acc,
                            self.mag, self.depth, self.gyro,
                            self.position, self.velocity,
                            self.acc, self.motors]
                    self.data_receiver(data)
                    last_data = time.time()
                else:
                    time.sleep(sleep_time)


    def controll_motors(self, roll_error, pitch_error, yaw_error, depth_error):
        motors = [0]*5
        def control_roll():

            motors[4]+=roll_error
            motors[2]-=roll_error
        def control_pitch():
            motors[2]+=pitch_error
            motors[4]+=pitch_error
            motors[3]-=pitch_error
        def control_yaw():
            motors[0] +=self.forward+yaw_error
            motors[1] -= -self.forward+yaw_error
        def control_depth():
            motors[2] += depth_error/2
            motors[3] += depth_error
            motors[4] += depth_error/2

        control_roll()
        control_pitch()
        control_yaw()
        control_depth()
        for i in range(5):
            if abs(motors[i])>1000:
                motors[i] = motors[i]/abs(motors[i])*1000
        self.motors=motors
        self.setMotors(motors)

#GUI methods

    def HandleSteeringInput(self, data):
        roll, pitch, yaw, forward, vertical = data
        self.roll_ref = roll*30/1000
        self.pitch_ref = pitch*30/1000
        self.yaw_ref = yaw
        self.forward = forward
        self.vertical = vertical
        a=self.client.get_sample('attitude')
        self.ref_attitude = q.fromEuler(self.roll_ref,self.pitch_ref,a[2])

    def SetDepth(self, depth):
        self.ref_depth = depth

    def SetAttitude(self, roll, pitch, yaw):
        self.roll_ref = roll
        self.pitch_ref = pitch
        self.yaw_ref = yaw
        self.ref_attitude =q.fromEuler(roll, pitch, yaw)


    def SetHeading(self, heading):
        
        b = self.attitude.toEuler()
        self.ref_attitude = q.Quaternion.fromEuler(math.degrees(b[2]),math.degrees(b[1]), heading)
        self.yaw_ref = heading

    def SetPosition(self,position):
        #x,y,z
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
        def map(input,in_min,in_max,out_min,out_max):
            return int((input-in_min)*(out_max-out_min)/(in_max-in_min)+out_min)
        ret=[]
        for i in self.m:
            ret.append(map(i, -1000,1000,0,100))
        return ret



    def SetPIDs(self, arg):
        self.roll_PID.setPIDCoefficients(arg[0],arg[1],arg[2],arg[3])
        self.pitch_PID.setPIDCoefficients(arg[4],arg[5],arg[6],arg[7])
        self.yaw_PID.setPIDCoefficients(arg[8],arg[9],arg[10],arg[11])
        self.depth_PID.setPIDCoefficients(arg[12], arg[13], arg[14],arg[15])

    def GetPIDs(self):
        return self.roll_PID.getPIDCoefficients()+self.pitch_PID.getPIDCoefficients()+self.yaw_PID.getPIDCoefficients()+self.depth_PID.getPIDCoefficients()
