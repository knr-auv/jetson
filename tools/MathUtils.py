import math

import numpy as np

import tools.PID.Quaternion as Q


def vec_length(vec):
    sum = 0
    for i in vec:
        sum += i * i
    return math.sqrt(sum)


def get_real_size(h_fov, v_fov, width, height, distance):
    """
    wymiary szer. i wys. musza byc przeskalowane od 0 do 1, gdzie 1 to szerokosc/wysokosc obrazu
    fov w stopniach, dla symulacji v_fov = 60, h_fov=60*16/9 -> 106.7
    """
    ang_height = height * math.radians(v_fov)
    ang_width = width * math.radians(h_fov)
    h = math.tan(ang_height / 2) * 2 * distance
    w = math.tan(ang_width / 2) * 2 * distance
    return w, h


def get_angle(real_size, size_from_angle):
    # funkcja zwraca pod jakim kątem widzimy obiekt
    if size_from_angle > real_size:
        return 0
    return math.asin(size_from_angle / real_size)


def posFromPicture(h_fov, v_fov, distance, center_width, center_height):
    h_fov = math.radians(h_fov)
    v_fov = math.radians(v_fov)
    center_width -= 0.5
    center_height -= 0.5
    a = h_fov * center_width
    x = distance * math.cos(a)
    y = distance * math.sin(a)
    # b is angle between okon pitch and object
    b = v_fov * center_height
    z = distance * math.sin(b)
    return [x, y, z]


def toGlobalRef(pos, attitude):
    rot = Q.fromEuler(*attitude)
    x, y, z = pos
    q = Q.Quaternion([0, x, y, z])
    r = rot * q * rot.conj()
    x = r.b
    y = r.c
    z = r.d
    return [x, y, z]
