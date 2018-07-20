import numpy as np


class Obj(object):

    def __init__(self):
        self.pos = None
        self.M = None
        self.vertices = None
        self.v = None



def euler_angles(yaw=0, pitch=0, roll= 0):

    T_yaw = np.array([
        [np.cos(yaw), np.sin(yaw), 0],
        [-np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1],
    ])

    T_pitch = np.array([
        [np.cos(pitch), 0, -np.sin(yaw),],
        [0,1,0],
        [np.sin(pitch), 0, np.cos(pitch)],

    ])

    T_roll = np.array([
        [1, 0, 0],
        [0, np.cos(roll), np.sin(roll),],
        [0, -np.sin(roll), np.cos(roll), ],
    ])

    M_GNR = np.dot(T_roll, np.dot(T_pitch, T_yaw))
    return M_GNR



if __name__ == "__main__":
    # ego at (10,20,0) rotated 30 degree around z axis
    e = Obj()
    e.pos = np.array([10, 0, 0])
    e.M = euler_angles(yaw=90/180.*np.pi)

    # vcl at (40, 40, 0) rotated 0
    o = Obj()
    o.pos = np.array([40, 40, 0])
    o.M = euler_angles(yaw=0 / 180. * np.pi)

    print "Distance in world frame {} {}".format(np.linalg.norm(o.pos - e.pos), o.pos)

    n = Obj()
    n.pos = np.dot(e.M,  o.pos - e.pos)
    n.M = np.dot(e.M, o.M)

    print "Distance in sensor frame {} {}".format(np.linalg.norm(n.pos), n.pos)

    print e.M
    print o.M
    print n.M

