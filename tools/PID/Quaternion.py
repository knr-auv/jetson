"""Quaternion math implementation"""

import math

import numpy as np


def multiply(Q1, Q2):
    new_a = Q1.a * Q2.a - Q1.b * Q2.b - Q1.c * Q2.c - Q1.d * Q2.d
    new_b = Q1.a * Q2.b + Q2.a * Q1.b + Q1.c * Q2.d - Q1.d * Q2.c
    new_c = Q1.a * Q2.c - Q1.b * Q2.d + Q1.c * Q2.a + Q1.d * Q2.b
    new_d = Q1.a * Q2.d + Q1.b * Q2.c - Q1.c * Q2.b + Q1.d * Q2.a
    Qwyn = [new_a, new_b, new_c, new_d]
    Qwyn = Quaternion(Qwyn)
    return Qwyn


def fromEuler(roll, pitch, yaw):
    roll = math.radians(roll)
    pitch = math.radians(pitch)
    yaw = math.radians(yaw)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    Q = Quaternion()
    Q.a = cr * cp * cy + sr * sp * sy
    Q.b = sr * cp * cy - cr * sp * sy
    Q.c = cr * sp * cy + sr * cp * sy
    Q.d = cr * cp * sy - sr * sp * cy
    return Q


def normalize(vector):
    sum_of_square = 0
    for i in vector:
        sum_of_square += i * i
    sum = math.sqrt(sum_of_square)
    for i in range(len(vector)):
        vector[i] = vector[i] / sum
    return vector


def scalar_multiply(scalar, Q):
    Q.a = scalar * Q.a
    Q.b = scalar * Q.b
    Q.c = scalar * Q.c
    Q.d = scalar * Q.d
    return Q


class Quaternion:
    a = None
    b = None
    c = None
    d = None

    def __init__(self, Q=None):
        if Q != None:
            self.a = Q[0]
            self.b = Q[1]
            self.c = Q[2]
            self.d = Q[3]

    def __repr__(self):
        return "[" + str(self.a) + "," + str(self.b) + "," + str(self.c) + "," + str(self.d) + "]"

    def __str__(self):
        return str([self.a, self.b, self.c, self.d])

    def __mul__(self, other):
        if type(other) == type(self):
            return multiply(self, other)
        return scalar_multiply(other, self)

    def _add_(self, other):
        self.a += other.a
        self.b += other.b
        self.c += other.c
        self.d += other.d
        return self

    def toList(self):
        return [self.a, self.b, self.c, self.d]

    def norm(self):
        lenght = math.sqrt(self.a * self.a + self.b * self.b + self.c * self.c + self.d * self.d)
        return lenght

    def normalize(self):
        lenght = self.norm()
        self.a /= lenght
        self.b /= lenght
        self.c /= lenght
        self.d /= lenght

    def conj(self):
        q = Quaternion(self.toList())
        q.b = -q.b
        q.c = -q.c
        q.d = -q.d
        return q

    def ToDCM(self):
        Q = self.normalize()
        a = self.a
        b = self.b
        c = self.c
        d = self.d
        rot_matrix = np.array(
            [
                [a**2 + b**2 - c**2 - d**2, 2 * (b * c + a * d), 2 * (b * d - a * c)],
                [2 * (b * c - a * d), a**2 - b**2 + c**2 - d**2, 2 * (c * d + a * b)],
                [2 * (b * d + a * c), 2 * (c * d - a * b), (a**2 - b**2 - c**2 + d**2)],
            ]
        )
        return rot_matrix

    def toEuler(self):
        self.normalize()
        q_0 = self.a
        q_1 = self.b
        q_2 = self.c
        q_3 = self.d
        gamma = math.atan2(2 * (q_1 * q_2 + q_0 * q_3), q_0**2 + q_1**2 - q_2**2 - q_3**2)
        beta = math.asin(-2 * (q_1 * q_3 - q_0 * q_2))
        alfa = math.atan2(2 * (q_2 * q_3 + q_0 * q_1), q_0 * q_0 - q_1 * q_1 - q_2 * q_2 + q_3 * q_3)
        return [math.degrees(alfa), math.degrees(beta), math.degrees(gamma)]
