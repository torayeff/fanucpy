from __future__ import annotations

import socket
from typing import Literal


class FanucError(Exception):
    pass


class Robot:
    def __init__(
        self,
        robot_model: str,
        host: str,
        port: int = 18375,
        ee_DO_type: str | None = None,
        ee_DO_num: int | None = None,
        socket_timeout: int = 60,
    ):
        """Class to connect to the robot, send commands, and receive
        responses.

        Args:
            robot_model (str): Robot model: Fanuc, Kuka, etc.
            host (str): IP address of host.
            port (int): Port number. Defaults to 18735.
            ee_DO_type (str, optional): End-effector digital output
                type. Fanuc used RDO type. Defaults to None. Others may
                use DO type.
            ee_DO_num (int, optional): End-effector digital output
                number. Defaults to None.
            socket_timeout(int): Socket timeout in seconds. Defaults to
                5 seconds.
        """
        self.robot_model = robot_model
        self.host = host
        self.port = port
        self.ee_DO_type = ee_DO_type
        self.ee_DO_num = ee_DO_num
        self.sock_buff_sz = 1024
        self.socket_timeout = socket_timeout
        self.comm_sock: socket.socket
        self.SUCCESS_CODE = 0
        self.ERROR_CODE = 1

    def handle_response(
        self, resp: str, continue_on_error: bool = False
    ) -> tuple[Literal[0, 1], str]:
        """Handles response from socket communication.

        Args:
            resp (str): Response string returned from socket.
            verbose (bool, optional): [description]. Defaults to False.

        Returns:
            tuple(int, str): Response code and response message.
        """
        code_, msg = resp.split(":")
        code = int(code_)

        # Catch possible errors
        if code == self.ERROR_CODE and not continue_on_error:
            raise FanucError(msg)
        if code not in (self.SUCCESS_CODE, self.ERROR_CODE):
            raise FanucError(f"Unknown response code: {code} and message: {msg}")

        return code, msg  # type: ignore[return-value]

    def connect(self) -> tuple[Literal[0, 1], str]:
        """Connects to the physical robot."""
        self.comm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.comm_sock.settimeout(self.socket_timeout)
        self.comm_sock.connect((self.host, self.port))
        resp = self.comm_sock.recv(self.sock_buff_sz).decode()
        return self.handle_response(resp)

    def disconnect(self) -> None:
        self.comm_sock.close()

    def send_cmd(
        self, cmd: str, continue_on_error: bool = False
    ) -> tuple[Literal[0, 1], str]:
        """Sends command to a physical robot.

        Args:
            cmd (str): Command string.

        Returns:
            tuple(int, str): Response code and response message.
        """
        # end of command character
        cmd = cmd.strip() + "\n"

        # Send command
        self.comm_sock.sendall(cmd.encode())

        # Wait for a result (blocking)
        resp = self.comm_sock.recv(self.sock_buff_sz).decode()
        return self.handle_response(resp=resp, continue_on_error=continue_on_error)

    def call_prog(self, prog_name: str) -> tuple[Literal[0, 1], str]:
        """Calls external program name in a physical robot.

        Args:
            prog_name ([str]): External program name.
        """
        cmd = f"mappdkcall:{prog_name}"
        return self.send_cmd(cmd)

    def get_ins_power(self) -> float:
        """Gets instantaneous power consumption.

        Returns:
            float: Watts.
        """

        cmd = "ins_pwr"
        _, msg = self.send_cmd(cmd)

        # Fanuc returns in kW. Should be adjusted to other robots.
        ins_pwr = float(msg) * 1000

        return ins_pwr

    def get_curpos(self) -> list[float]:
        """Gets current cartesian position of tool center point.

        Returns:
            list[float]: Current positions XYZWPR.
        """

        cmd = "curpos"
        _, msg = self.send_cmd(cmd)
        vals = [float(val.split("=")[1]) for val in msg.split(",")]
        return vals

    def get_curjpos(self) -> list[float]:
        """Gets current joint values of tool center point.

        Returns:
            list[float]: Current joint values.
        """
        cmd = "curjpos"
        _, msg = self.send_cmd(cmd)
        vals = [float(val.split("=")[1]) for val in msg.split(",") if val != "j=none"]
        return vals

    def move(
        self,
        move_type: Literal["joint"] | Literal["pose"],
        vals: list,
        velocity: int = 25,
        acceleration: int = 100,
        cnt_val: int = 0,
        linear: bool = False,
        continue_on_error: bool = False,
    ) -> tuple[Literal[0, 1], str]:
        """Moves robot.

        Args:
            move_type (str): Movement type (joint or pose).
            vals (list[real]): Position values.
            velocity (int, optional): Percentage or mm/s. Defaults to
                25%.
            acceleration (int, optional): Percentage or mm/s^2. Defaults
                to 100%.
            cnt_val (int, optional): Continuous value for stopping.
                Defaults to 50.
            linear (bool, optioal): Linear movement. Defaults to False.

        Raises:
            ValueError: raised if movement type is not one of
                ("movej", "movep")
        """

        # prepare velocity. percentage or mm/s
        # format: aaaa, e.g.: 0001%, 0020%, 3000 mm/s
        velocity = int(velocity)
        velocity_ = f"{velocity:04}"

        # prepare acceleration. percentage or mm/s^2
        # format: aaaa, e.g.: 0001%, 0020%, 0100 mm/s^2
        acceleration = int(acceleration)
        acceleration_ = f"{acceleration:04}"

        # prepare CNT value
        # format: aaa, e.g.: 001, 020, 100
        cnt_val = int(cnt_val)
        if not (0 <= cnt_val <= 100):
            raise ValueError("Incorrect CNT value.")
        cnt_val_ = f"{cnt_val:03}"

        if move_type == "joint" or move_type == "movej":
            cmd = "movej"
        elif move_type == "pose" or move_type == "movep":
            cmd = "movep"
        else:
            raise ValueError("Incorrect movement type!")

        motion_type = int(linear)

        cmd += f":{velocity_}:{acceleration_}:{cnt_val_}:{motion_type}:{len(vals)}"

        # prepare joint values
        for val in vals:
            vs = f"{abs(val):013.6f}"
            if val >= 0:
                vs = "+" + vs
            else:
                vs = "-" + vs
            cmd += f":{vs}"

        # call send_cmd
        return self.send_cmd(cmd, continue_on_error=continue_on_error)

    def gripper(
        self,
        value: bool,
        continue_on_error: bool = False,
    ) -> tuple[Literal[0, 1], str]:
        """Opens/closes robot gripper.

        Args:
            value (bool): True or False
        """
        if (self.ee_DO_type is not None) and (self.ee_DO_num is not None):
            cmd = ""
            if self.ee_DO_type == "RDO":
                cmd = "setrdo"
                port = str(self.ee_DO_num)
            elif self.ee_DO_type == "DO":
                cmd = "setdout"
                port = str(self.ee_DO_num).zfill(5)
            else:
                raise ValueError("Wrong DO type!")

            cmd = cmd + f":{port}:{str(value).lower()}"
            return self.send_cmd(cmd, continue_on_error=continue_on_error)
        else:
            raise ValueError("DO type or number is None!")

    def get_rdo(self, rdo_num: int) -> int:
        """Get RDO value.

        Args:
            rdo_num (int): RDO number.

        Returns:
            rdo_value: RDO value.
        """
        cmd = f"getrdo:{rdo_num}"
        _, rdo_value_ = self.send_cmd(cmd)
        rdo_value = int(rdo_value_)
        return rdo_value

    def set_rdo(
        self,
        rdo_num: int,
        val: bool,
        continue_on_error: bool = False,
    ) -> tuple[Literal[0, 1], str]:
        """Sets RDO value.

        Args:
            rdo_num (int): RDO number.
            val (bool): Value.
        """
        cmd = f"setrdo:{rdo_num}:{str(val).lower()}"
        return self.send_cmd(cmd, continue_on_error=continue_on_error)

    def get_dout(self, dout_num: int) -> int:
        """Get DOUT value.

        Args:
            dout_num (int): DOUT number.

        Returns:
            dout_value: DOUT value.
        """
        cmd = f"getdout:{str(dout_num).zfill(5)}"
        _, dout_value_ = self.send_cmd(cmd)
        dout_value = int(dout_value_)
        return dout_value

    def set_dout(
        self,
        dout_num: int,
        val: bool,
        continue_on_error: bool = False,
    ) -> tuple[Literal[0, 1], str]:
        """Sets DOUT value.

        Args:
            dout_num (int): DOUT number.
            val (bool): Value.
        """
        cmd = f"setdout:{str(dout_num).zfill(5)}:{str(val).lower()}"
        return self.send_cmd(cmd, continue_on_error=continue_on_error)

    def set_sys_var(
        self,
        sys_var: str,
        val: bool,
        continue_on_error: bool = False,
    ) -> tuple[Literal[0, 1], str]:
        """Sets system variable to True or False.

        Args:
            sys_var (str): System variable name.
            val (bool): Value.
        """
        val_ = "T" if val else "F"
        cmd = f"setsysvar:{sys_var}:{val_}"
        return self.send_cmd(cmd, continue_on_error=continue_on_error)


if __name__ == "__main__":
    robot = Robot(
        robot_model="Fanuc",
        host="10.211.55.3",
        port=18735,
        ee_DO_type="RDO",
        ee_DO_num=7,
    )

    robot.connect()

    # move in joint space
    robot.move(
        "joint",
        vals=[0, 0, 0, 0, 0, 0],
        velocity=100,
        acceleration=100,
        cnt_val=0,
        linear=not False,
    )
    print(robot.get_curpos())

    # move in cartesian space
    robot.move(
        "pose",
        vals=[350, 0, 280, -15, -90, -160],
        velocity=100,
        acceleration=100,
        cnt_val=0,
        linear=not False,
    )
