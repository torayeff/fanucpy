import sys

from cv2 import cv2
import numpy as np
from fanucpy import RobotApp
from fanucpy.Calibration import Calibration


class ArucoTrackingApp(RobotApp):
    def __init__(self, cam, camera_matrix, dist_coeffs, marker_length) -> None:
        super().__init__()
        self.configure(
            cam=cam,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
            marker_length=marker_length,
        )

    def configure(self, cam, camera_matrix, dist_coeffs, marker_length):
        self.cam = cam
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.marker_length = marker_length

    def _main(self):
        print("Press [q] to exit.")
        while True:
            _, frame = self.cam.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_7X7_50)
            parameters = cv2.aruco.DetectorParameters_create()
            corners, ids, _ = cv2.aruco.detectMarkers(
                gray,
                aruco_dict,
                parameters=parameters,
                cameraMatrix=self.camera_matrix,
                distCoeff=self.dist_coeffs,
            )
            if np.all(ids is not None):
                for i in range(len(ids)):
                    rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(
                        corners=corners[i],
                        markerLength=self.marker_length,
                        cameraMatrix=self.camera_matrix,
                        distCoeffs=self.dist_coeffs,
                    )
                    (rvec - tvec).any()
                    cv2.aruco.drawDetectedMarkers(frame, corners)
                    cv2.aruco.drawAxis(
                        image=frame,
                        cameraMatrix=self.camera_matrix,
                        distCoeffs=self.dist_coeffs,
                        rvec=rvec,
                        tvec=tvec,
                        length=50,
                    )
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1)
            if key == ord("q"):
                self.cam.release()
                cv2.destroyAllWindows()
                break


if __name__ == "__main__":
    # get calibration data
    calib = Calibration()
    fp = "../../test_data/calib_data/calib_data_robot.pkl"
    calib_data = calib.load_calib_data(fp)

    cam = cv2.VideoCapture(0)
    app = ArucoTrackingApp(
        cam=cam,
        camera_matrix=calib_data["camera_matrix"],
        dist_coeffs=calib_data["dist_coeffs"],
        marker_length=120,
    )
    status, message, result = app.run()
    print(status, message)
