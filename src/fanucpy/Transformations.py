import numpy as np
from scipy.spatial.transform import Rotation


def Rt_to_H(R, t):
    """Converts 3x3 rotation matrix 3x1 translation vector into
    4x4 homogeneous transformation matrix."""
    H = np.eye(4)
    H[0:3, 0:3] = R
    H[0:3, 3] = t.squeeze()
    return H


def H_to_Rt(H):
    """Converts 4x4 homogeneous transformation matrix into
    3x3 rotation matrix and 3x1 translation vector."""
    return H[0:3, 0:3], H[0:3, 3]


def xyzrpw_to_H(xyzrpw):
    """Converts xyzrpw to 4x4 homogeneous transformation matrix."""
    R = Rotation.from_euler("xyz", xyzrpw[3:], degrees=True).as_matrix()
    H = Rt_to_H(R, xyzrpw[:3])
    return H


def H_to_xyzrpw(H):
    """Converts 4x4 homogeneous transformation matrix to xyzrpw."""
    R, t = H_to_Rt(H)
    rpw = Rotation.from_matrix(R).as_euler("xyz", degrees=True)
    return list(t.flatten()) + list(rpw.flatten())
