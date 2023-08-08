"""Transformations related to the Fanuc robot.

Some of the transformations are based on the following sources:
    - https://automaticaddison.com/how-to-convert-euler-angles-to-quaternions-using-python/
    - https://automaticaddison.com/how-to-convert-a-quaternion-into-euler-angles-in-python/
"""
import numpy as np
from scipy.spatial.transform import Rotation

import math
from collections import namedtuple


WPR = namedtuple("WPR", ["W", "P", "R"])
WrPrRr = namedtuple("WrPrRr", ["Wr", "Pr", "Rr"])
Quaternion = namedtuple("Quaternion", ["x", "y", "z", "w"])


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


def WPR_to_WrPrRr(wpr: WPR) -> WrPrRr:
    """Converts WPR angles from degrees to radians.

    Args:
        wpr (WPR): WPR angles in degrees

    Returns:
        WrPrRr: WPR angles in radians
    """
    return WrPrRr(
        Wr=math.radians(wpr.W),
        Pr=math.radians(wpr.P),
        Rr=math.radians(wpr.R),
    )


def WrPrRr_to_WPR(wpr: WrPrRr) -> WPR:
    """Converts WPR angles from radians to degrees.

    Args:
        wpr (WrPrRr): WPR angles in radians

    Returns:
        WPR: WPR angles in degrees
    """
    return WPR(
        W=math.degrees(wpr.Wr),
        P=math.degrees(wpr.Pr),
        R=math.degrees(wpr.Rr),
    )


def WrPrRr_to_Quaternion(wpr: WrPrRr) -> Quaternion:
    """Converts WrPrRr angles to a quaternion.

    https://automaticaddison.com/how-to-convert-euler-angles-to-quaternions-using-python/

    Args:
        wpr (WPR): WPR angles in radians

    Returns:
        Quaternion: WPR angles as a quaternion
    """
    return Quaternion(
        x=math.sin(wpr.Rr / 2) * math.cos(wpr.Pr / 2) * math.cos(wpr.Wr / 2)
        - math.cos(wpr.Rr / 2) * math.sin(wpr.Pr / 2) * math.sin(wpr.Wr / 2),
        y=math.cos(wpr.Rr / 2) * math.sin(wpr.Pr / 2) * math.cos(wpr.Wr / 2)
        + math.sin(wpr.Rr / 2) * math.cos(wpr.Pr / 2) * math.sin(wpr.Wr / 2),
        z=math.cos(wpr.Rr / 2) * math.cos(wpr.Pr / 2) * math.sin(wpr.Wr / 2)
        - math.sin(wpr.Rr / 2) * math.sin(wpr.Pr / 2) * math.cos(wpr.Wr / 2),
        w=math.cos(wpr.Rr / 2) * math.cos(wpr.Pr / 2) * math.cos(wpr.Wr / 2)
        + math.sin(wpr.Rr / 2) * math.sin(wpr.Pr / 2) * math.sin(wpr.Wr / 2),
    )


def Quaternion_to_WrPrRr(quat: Quaternion) -> WrPrRr:
    """Converts a quaternion to WrPrRr angles.

    https://automaticaddison.com/how-to-convert-a-quaternion-into-euler-angles-in-python/

    Args:
        quat (Quaternion): WPR angles as a quaternion

    Returns:
        WrPrRr: WPR angles in radians
    """
    return WrPrRr(
        Wr=math.atan2(
            2 * (quat.w * quat.z + quat.x * quat.y), 1 - 2 * (quat.y**2 + quat.z**2)
        ),
        Pr=math.asin(max(min(2 * (quat.w * quat.y - quat.z * quat.x), 1.0), -1.0)),
        Rr=math.atan2(
            2 * (quat.w * quat.x + quat.y * quat.z), 1 - 2 * (quat.x**2 + quat.y**2)
        ),
    )


def WPR_to_Quaternion(wpr: WPR) -> Quaternion:
    """Converts WPR angles to a quaternion.

    https://automaticaddison.com/how-to-convert-euler-angles-to-quaternions-using-python/

    Args:
        wpr (WPR): WPR angles in degrees

    Returns:
        Quaternion: WPR angles as a quaternion
    """
    return WrPrRr_to_Quaternion(WPR_to_WrPrRr(wpr))


def Quaternion_to_WPR(quat: Quaternion) -> WPR:
    """Converts a quaternion to WPR angles.

    https://automaticaddison.com/how-to-convert-a-quaternion-into-euler-angles-in-python/

    Args:
        quat (Quaternion): WPR angles as a quaternion

    Returns:
        WPR: WPR angles in degrees
    """
    return WrPrRr_to_WPR(Quaternion_to_WrPrRr(quat))
