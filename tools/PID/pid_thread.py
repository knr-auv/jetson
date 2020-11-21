from quaternions import Quaternion
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

    def arm(self):
        self.armed = True

    def disarm(self):
        self.armed=False

    def PIDLoop(self):
        #do całkowania potrzeba czasu.
        loop_time = 0
        last_time =0
        #pętla będzie działać z jakąś określoną częstotliwością np 50Hz
        while(1):
            loop_time = time.time()-last_time
            #gyro acc and depth will be obtained from client
            self.gyro = [1,2,3]
            self.acc = [1,2,3] #Ax,Ay,Az
            self.depth=1
            #q_from_acc = [1,1,1,1]#=[-Ay/sqrt(2(1-Az)), -sqrt(0.5*(1-Az)), 0, -Ax/sqrt(2(1-Az))]
            #OK

            acc_quaternion=Quaternion([-self.acc[1]/math.sqrt(2*(1-self.acc[2])),-math.sqrt(0.5*(1-self.acc[2])),0,-self.acc[0]/math.sqrt(2*(1-self.acc[2]))])
            #OK

            gyro_quaternion=Quaternion([0,self.gyro[0],self.gyro[1],self.gyro[2]])

            #pozycja to pozycja x,y,z w całym basenie -> na razie nie ma co tego ruszać. Docelowo z acc całkujemy przyspieszenie i mamy prędkość, którą zamieniamy na położenie

            ref_position_quaternion=Quaternion(self.ref_position)

            #self.attitude = .... integrate gyro
            #self.attitude = 0.9*self.attitude+0.1*q_from_acc
            attitude_quaternion=Quaternion(self.attitude)
            #tylko do obliczen
            temp=Quaternion.multiply(gyro_quaternion,attitude_quaternion)

            #OK tylko powinno być 0.5 * loop_time  (bo całkujesz po czasie)

            attitude_quaternion=Quaternion.sum(attitude_quaternion,Quaternion.scalar_multiply(0.5*loop_time,temp))
            #reference
            #w tym jednym wypadku chodzi o dodania do siebie wektorów. attitude_quaternion*0.9 + acc_quaternion*0.1. Quaternion.add -> filtr komplementarny(wersja dla leniwych)

            attitude_quaternion=Quaternion.sum(Quaternion.scalar_multiply((0.9,attitude_quaternion)),Quaternion.scalar_multiply(0.1,acc_quaternion))
            #ok
            attitude_quaternion.normalize()
            #na tym etapie masz już policzoną pozycje z żyroskopu. I już używasz tylko self.attitude i ew gyro_quaternion

            #pozycje liczymy cały czas, ale musimy liczyć coś więcej tylko jeśli łódka jest uzbrojona czyli pływa
            if(self.armed==True):
                #jesli
                #mode 1 czyli model ma zadane prędkości kątowe
                #jeśli self.ref_ang_vel[0] =0 itd... ustaw referencyjną pozycje na obecną i rób mode 0 -> dzieki temu okon nawet jak jest do góry nogami to utrzymuje swoją pozycje
                #jeśli uzytkownik zadal ref_ang_vel liczysz pidy za błąd uznajac self.ref_ang_vel[0] i gyro_quternion[1] itd...
                #pomijasz mode 0 i liczysz pidy
                #jesli
                #mode 0 czyli stabilny - model dąży do ref position
                #kwaternion bledu (referencyjna pozycja i pozycja)
                # na górze dopisałem self.ref_position -> to jest pozycja zadawana przez osobe, która steruje
                #teraz musisz obliczyć błąd między pozycją prawdziwą a zadaną.
                #takim wzorkiem jak niżej
                #error = q.multiply(self.ref_position, conj(self.attitude))
                #otrzymany błąd to różnica pozycji referencyjnej a prawdziwej. Od tego momentu uznajmy, że są to m/s
                #blad do wysterowania
                q_error=Quaternion.multiply(ref_position_quaternion,attitude_quaternion.conjugate())
                #tylko elementy urojone
                q_error.a=0
                #potrzebne sa tylko elementy urojone -> dokładnie tak.
                #not_important, v_x, v_y, v_z = error
                #musisz zerknąć do pidów. Bo nie pamiętam jak są napisane.
                #Jeśli przyjmują dwa argumenty to musisz podać np v_x i gyro_quternion[1]
                #jeśli jeden to wpisujesz v_x-gyro_quaternion[1] itd...

                # wzorowalem sie na poprzednich pidach
                if self.mode == 0:#tryb stabilny
                    # liczenie pidow na poszczegolne obroty i glebokosc
                    self.roll_diff=self.roll_PID.update(gyro_quaternion.b,q_error.b)## kwaterniony z klasy maja atrybuty a,b,c,d
                    self.pitch_diff=self.pitch_PID.update(gyro_quaternion.c,q_error.c)
                    self.yaw_diff=self.yaw_PID.update(gyro_quaternion.d,q_error.d)
                    self.depth_diff=self.depth_PID.update(self.ref_depth,self.depth)

                if self.mode == 1:  # tryb acro
                    if self.ref_ang_vel[0]==0 and self.ref_ang_vel[1]==0 and self.ref_ang_vel[2]==0:# nie ma zadanej predkosci katowej-> lódz powinna bys stabilna
                        #obecna pozycja jest referencyjna
                        self.ref_position[0]=attitude_quaternion.b
                        self.ref_position[1] = attitude_quaternion.c
                        self.ref_position[2] = attitude_quaternion.d
                        #mode 0 czyli stabilny
                        self.roll_diff = self.roll_PID.update(gyro_quaternion.b, q_error.b)
                        self.pitch_diff = self.pitch_PID.update(gyro_quaternion.c, q_error.c)
                        self.yaw_diff = self.yaw_PID.update(gyro_quaternion.d, q_error.d)
                        self.depth_diff = self.depth_PID.update(self.ref_depth, self.depth)
                    else:# zadana jest jakas predkosc trzeba policzyc pidy z nowa pozycja
                        self.roll_diff=self.roll_PID.update(gyro_quaternion.b,self.ref_ang_vel[0])
                        self.pitch_diff=self.pitch_PID.update(gyro_quaternion.c,self.ref_ang_vel[1])
                        self.yaw_diff = self.yaw_PID.update(gyro_quaternion.d,self.ref_ang_vel[2])

                #teraz ustawić motory i jazda
                #set motors
                self.controll_motors(self.roll_diff,self.pitch_diff,self.yaw_diff,self.depth_diff)
            last_time = time.time()

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

    def getPIDs(self,arg):
        return [arg]+self.roll_PID.getPIDCoefficients()+self.pitch_PID.getPIDCoefficients()+self.yaw_PID.getPIDCoefficients()+self.depth_PID.getPIDCoefficients()
