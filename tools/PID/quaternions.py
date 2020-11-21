import numpy as np
import math

class Quaternion():
    def __init__(self,Q):
        self.a=Q[0]
        self.b=Q[1]
        self.c=Q[2]
        self.d=Q[3]
    def sum(Q1, Q2):
        Qw=[Q1.a+Q2.a, Q1.b+Q2.b, Q1.c+Q2.c, Q1.d+Q2.d]
        Qw=Quaternion(Qw)
        return Qw
    def multiply(Q1, Q2):
        new_a=(Q1.a*Q2.a-Q1.b*Q2.b-Q1.c*Q2.c-Q1.d*Q2.d)
        new_b=(Q1.a*Q2.b + Q2.a*Q1.b+Q1.c*Q2.d-Q1.d*Q2.c)
        new_c=(Q1.a*Q2.c-Q1.b*Q2.d+Q1.c*Q2.a+Q1.d*Q2.b)
        new_d=(Q1.a*Q2.d+Q1.b*Q2.c-Q1.c*Q2.b+Q1.d*Q2.a)
        Qwyn=[new_a,new_b,new_c,new_d]
        Qwyn=Quaternion(Qwyn)
        return Qwyn
    def scalar_multiply(scalar,Q):
        Q.a = scalar*Q.a
        Q.b = scalar * Q.b
        Q.c = scalar * Q.c
        Q.d = scalar * Q.d
        return Q
    def norm(self):
        lenght=math.sqrt(self.a*self.a+self.b*self.b+self.c*self.c+self.d*self.d)
        return lenght
    def normalize(self):
        lenght = self.norm()
        self.a /= lenght
        self.b /= lenght
        self.c /= lenght
        self.d /= lenght
        return self
    def conjugate(self):
        self.b = -self.b
        self.c = -self.c
        self.d = -self.d
        return self
    def quat2dcm(self):
        Q = self.normalize()
        a=Q.a
        b=Q.b
        c=Q.c
        d=Q.d
        rot_matrix=np.array([[a**2+b**2-c**2-d**2,2*(b*c+a*d),2*(b*d-a*c)],
                             [2*(b*c-a*d),a**2-b**2+c**2-d**2,2*(c*d+a*b)],
                             [2*(b*d+a*c),2*(c*d-a*b),(a**2-b**2-c**2+d**2)]])
        return rot_matrix
    def quat2eul(self):
        Q=self.normalize()
        q_0=Q.a
        q_1=Q.b
        q_2 = Q.c
        q_3 = Q.d
        gamma=math.atan2(2*(q_1*q_2+q_0*q_3),q_0**2+q_1**2-q_2**2-q_3**2)
        beta=math.asin(-2*(q_1*q_3-q_0*q_2))
        alfa=math.atan2(2*(q_2*q_3 + q_0*q_1), q_0*q_0 - q_1*q_1 - q_2*q_2 + q_3*q_3)
        return np.array([gamma,beta,alfa])
    def print(self):
        print(self.a)
        print(self.b)
        print(self.c)
        print(self.d)


def normalize(vector):
    sum_of_square=0
    for i in vector:
        sum_of_square=sum_of_square+(i*i)
    sum=math.sqrt(sum_of_square)
    for i in range(len(vector)):
        vector[i]=vector[i]/sum
    return vector
'''
xc=0
yc=0
zc=0

L=2  #cube size
alpha=0.8 #transparency (max=1=opaque)
X=np.array([[0,0, 0, 0, 0, 1],[1, 0, 1, 1, 1, 1],[1, 0, 1, 1, 1, 1], [0, 0, 0, 0, 0, 1]])
Y=np.array([[0, 0, 0, 0, 1, 0],[0, 1, 0, 0, 1, 1],[0, 1, 1, 1, 1, 1],[0, 0, 1, 1, 1, 0]])
Z= np.array([[0, 0, 1, 0, 0, 0],[0, 0, 1, 0, 0, 0],[1, 1, 1, 0, 1, 1],[1, 1, 1, 0, 1, 1]])
C=np.array([0.1, 0.3, 0.9, 0.9, 0.1, 0.5])

X = L*(X-0.5) + xc
Y = L/1.5*(Y-0.5) + yc
Z = L/3*(Z-0.5) + zc

simulation_time = 100
V1=X.reshape(1,24,order="F")
V2=Y.reshape(1,24,order="F")
V3=Z.reshape(1,24,order="F")
V=np.zeros((3,24))
print(V1)
V[0]=V1
V[1]=V2
V[2]=V3
Vr=V

max_vel = 0.9
test_vel_q = np.array([0,-10,0,0])
vel_q=np.array([0,0.2,0.9,0])
pos_q = np.array([1,0,0,0])
ref_pos_q =np.array([1,0,0,0])
test_vel_q=Quaternion(test_vel_q)
pos_q=Quaternion(pos_q)
vel_q=Quaternion(vel_q)
ref_pos_q=Quaternion(ref_pos_q)
t=0

i=0
while t<simulation_time:
    t=t+0.0005
    temp=Quaternion.sum(pos_q,Quaternion.scalar_multiply(0.5,Quaternion.multiply(test_vel_q,pos_q)))
    ref_pos_q = Quaternion.normalize(temp)

    vel_q=Quaternion.multiply(ref_pos_q,Quaternion.conjugate(pos_q))
    vel_q.a=0

    if Quaternion.norm(vel_q)>max_vel:
        norm_inv=1/Quaternion.norm(vel_q)
        temp=Quaternion.scalar_multiply(max_vel,vel_q)
        vel_q=Quaternion.scalar_multiply(norm_inv,temp)

    scalar=0.5*t
    pomnozone_kwateriony=Quaternion.multiply(vel_q,pos_q)
    skl_sumy=Quaternion.scalar_multiply(scalar,pomnozone_kwateriony)
    pos_q=Quaternion.sum(pos_q,skl_sumy)

    pos_q=Quaternion.normalize(pos_q)
    dcm = Quaternion.quat2dcm(pos_q)

    katy=Quaternion.quat2eul(pos_q)*180/math.pi
    print(V)
    print(dcm)
    Vr=dcm.dot(V)
    V1=np.array(V[0])
    V2=np.array(V[1])
    V3=np.array(V[2])

    X=V1.reshape((4,6),order="F")
    Y=V2.reshape((4,6),order="F")
    Z=V3.reshape((4,6),order="F")
    print(Vr)
    input() # tylko do testów porównywalem z matlabem i sie zgadza, tak samo funkcje, wstawiłem rózne kwaterniony i patrzyłem czy jest to samo

'''