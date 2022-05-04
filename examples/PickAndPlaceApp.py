from fanucpy import RobotApp


class PickAndPlaceApp(RobotApp):
    def __init__(self, robot) -> None:
        self.robot = robot
        self.configure()

    def configure(self):
        pass

    def _main(self, static_params, tunable_params):
        self.robot.connect()

        self.robot.move(
            move_type=static_params["pick_approach"]["move_type"],
            vals=static_params["pick_approach"]["pose"],
            velocity=tunable_params["pick_approach_velocity"],
            acceleration=tunable_params["pick_approach_acceleration"],
            cnt_val=static_params["pick_approach"]["cnt_val"],
            linear=static_params["pick_approach"]["linear"],
        )
        self.robot.gripper(True)
        self.robot.move(
            move_type=static_params["pick"]["move_type"],
            vals=static_params["pick"]["pose"],
            velocity=tunable_params["pick_velocity"],
            acceleration=tunable_params["pick_acceleration"],
            cnt_val=static_params["pick"]["cnt_val"],
            linear=static_params["pick"]["linear"],
        )
        self.robot.gripper(False)
        self.robot.move(
            move_type=static_params["pick_retract"]["move_type"],
            vals=static_params["pick_retract"]["pose"],
            velocity=tunable_params["pick_retract_velocity"],
            acceleration=tunable_params["pick_retract_acceleration"],
            cnt_val=static_params["pick_retract"]["cnt_val"],
            linear=static_params["pick_retract"]["linear"],
        )
        self.robot.move(
            move_type=static_params["place_approach"]["move_type"],
            vals=static_params["place_approach"]["pose"],
            velocity=tunable_params["place_approach_velocity"],
            acceleration=tunable_params["place_approach_acceleration"],
            cnt_val=static_params["place_approach"]["cnt_val"],
            linear=static_params["place_approach"]["linear"],
        )
        self.robot.move(
            move_type=static_params["place"]["move_type"],
            vals=static_params["place"]["pose"],
            velocity=tunable_params["place_velocity"],
            acceleration=tunable_params["place_acceleration"],
            cnt_val=static_params["place"]["cnt_val"],
            linear=static_params["place"]["linear"],
        )
        self.robot.gripper(True)
        self.robot.move(
            move_type=static_params["place_retract"]["move_type"],
            vals=static_params["place_retract"]["pose"],
            velocity=tunable_params["place_retract_velocity"],
            acceleration=tunable_params["place_retract_acceleration"],
            cnt_val=static_params["place_retract"]["cnt_val"],
            linear=static_params["place_retract"]["linear"],
        )
        self.robot.gripper(False)
        self.robot.move(
            move_type=static_params["home"]["move_type"],
            vals=static_params["home"]["pose"],
            velocity=tunable_params["home_velocity"],
            acceleration=tunable_params["home_acceleration"],
            cnt_val=static_params["home"]["cnt_val"],
            linear=static_params["home"]["linear"],
        )

        self.robot.disconnect()
        return "done"
