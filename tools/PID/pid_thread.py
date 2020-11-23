from quaternions import Quaternion
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
        

        self.armed = False
        self.position = [0,0,0]
        self.velocity = [0]*3
        self.motors = [0]*6

        self.attitude = [0]*4
        self.gyro = [0]*3
        self.acc = [0]*3

        self.depth=0
        self.ref_depth=0

        self.roll_diff = 0
        self.pitch_diff = 0
        self.yaw_diff = 0
        self.depth_diff = 0

        self.ref_ang_vel = [0]*3
        self.ref_position = [1,0,0,0]
        self.mode = 0 #niech 0 -> stabilny , 1-> acro

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

    def PIDLoop(self):
        loop_T = 1/50
        sleep_time = loop_t/10 #sounds reasonable...
        loop_time = 0
        last_time =0

        while(1):
            dt = time.time()-last_time
            if(dt>=loop_T):
                self.gyro = [1,2,3]
                self.acc = [1,2,3] #Ax,Ay,Az
                self.depth=1

                #TODO apply filter on acc
                self.velocity[0]= self.acc[0]*dt
                self.velocity[1]=self.acc[1]*dt
                self.velocity[2]=self.acc[2]*dt

                It = dt*dt/2
                self.position[0]= self.acc[0]*It
                self.position[1]=self.acc[1]*It
                self.position[2]=self.acc[2]*It

                #q_from_acc = [1,1,1,1]#=[-Ay/sqrt(2(1-Az)), -sqrt(0.5*(1-Az)), 0, -Ax/sqrt(2(1-Az))]
                acc_quaternion=Quaternion([-self.acc[1]/math.sqrt(2*(1-self.acc[2])),-math.sqrt(0.5*(1-self.acc[2])),0,-self.acc[0]/math.sqrt(2*(1-self.acc[2]))])
                #kwaternion do całkowania danych z żyroskopu
                gyro_quaternion=Quaternion([0,self.gyro[0],self.gyro[1],self.gyro[2]])


                ref_position_quaternion=Quaternion(self.ref_position)

                #kwaternion położenia
                attitude_quaternion=Quaternion(self.attitude)

                #scałkowane położenie
                #q(t) = q(t-1)+0.5*dt*w*q(t-1), gdzie w to predkosc katowa dana jako: [0,self.gyro[0],self.gyro[1],self.gyro[2]]

            
                attitude_quaternion=Quaternion.sum(attitude_quaternion,Quaternion.scalar_multiply(0.5*dt,Quaternion.multiply(gyro_quaternion,attitude_quaternion)))
            

                #podróbka filtra komplementarnego - w symulacji to chyba i tak bez znaczenia
                #TODO filtr kalmana dla kwaternionów
                attitude_quaternion=Quaternion.sum(Quaternion.scalar_multiply((0.9,attitude_quaternion)),Quaternion.scalar_multiply(0.1,acc_quaternion))
                #czasem się zdażą błędy numeryczne... Kwaternion musi być o długości 1.
                attitude_quaternion.normalize()


                if(self.armed==True):
                    #TODO To nie zawsze będzie najmniejszy obrót...
                    q_error=Quaternion.multiply(ref_position_quaternion,attitude_quaternion.conjugate())

                    if self.mode == 0:#tryb stabilny
                        self.roll_diff=self.roll_PID.update(gyro_quaternion.b,q_error.b)
                        self.pitch_diff=self.pitch_PID.update(gyro_quaternion.c,q_error.c)
                        self.yaw_diff=self.yaw_PID.update(gyro_quaternion.d,q_error.d)
                        self.depth_diff=self.depth_PID.update(self.ref_depth,self.depth)

                    elif self.mode == 1:  # tryb acro
                        if self.ref_ang_vel[0]==0 and self.ref_ang_vel[1]==0 and self.ref_ang_vel[2]==0:# nie ma zadanej predkosci katowej-> lódz powinna bys stabilna
                            #obecna pozycja jest referencyjna
                            self.ref_position[0] = attitude_quaternion.a
                            self.ref_position[1]=attitude_quaternion.b
                            self.ref_position[2] = attitude_quaternion.c
                            self.ref_position[3] = attitude_quaternion.d

                            self.roll_diff = self.roll_PID.update(gyro_quaternion.b, q_error.b)
                            self.pitch_diff = self.pitch_PID.update(gyro_quaternion.c, q_error.c)
                            self.yaw_diff = self.yaw_PID.update(gyro_quaternion.d, q_error.d)
                            self.depth_diff = self.depth_PID.update(self.ref_depth, self.depth)

                        else:# zadana jest jakas predkosc trzeba policzyc pidy z nowa pozycja
                            self.roll_diff=self.roll_PID.update(gyro_quaternion.b,self.ref_ang_vel[0])
                            self.pitch_diff=self.pitch_PID.update(gyro_quaternion.c,self.ref_ang_vel[1])
                            self.yaw_diff = self.yaw_PID.update(gyro_quaternion.d,self.ref_ang_vel[2])

                    self.controll_motors(self.roll_diff,self.pitch_diff,self.yaw_diff,self.depth_diff)

                last_time = time.time()
            else:
                time.sleep(sleep_time)


    def controll_motors(self, roll_error, pitch_error, yaw_error, depth_error):
        motors = [0]*5
        def control_roll(self):
            motors[4]+=roll_error
            motors[2]-=roll_error
        def control_pitch(self):
            motors[2]-=pitch_error
            motors[4]-=pitch_error
            motors[3]-=pitch_error
        def control_yaw(self):
            motors[0] += yaw_error
            motors[1] -= yaw_error
        def control_depth(self):
            motors[2] += depth_error
            motors[3] -= depth_error
            motors[4] += depth_error
        control_roll()
        control_pitch()
        control_yaw()
        control_depth()
        self.motors=motors
        self.setMotors(motors)

#GUI methods



    def SetDepth(self, depth):
        self.ref_depth = depth

    def SetAttitude(self, roll, pitch):
        a = Quaternion(self.attitude)
        b = a.quat2eul()
        t = Quaternion.fromEuler(roll, pitch, b[0])
        self.attitude = [t.a, t.b, t.c, t.d]

    def SetHeading(self, heading):
        a = Quaternion(self.attitude)
        b = a.quat2eul()
        t = Quaternion.fromEuler(b[2], b[1], heading)
        self.attitude = [t.a, t.b, t.c, t.d]

    def SetPosition(self,position):
        #x,y,z
        self.position = position


    def GetDepth(self):
        return self.depth

    def GetAttitude(self):
        ret = Quaternion(self.attitude)
        ret= ret.quat2eul()
        return ret.reverse()
        
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
