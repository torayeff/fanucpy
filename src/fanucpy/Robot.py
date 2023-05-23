from abc import ABC
import socket
import sys


class Robot(ABC):
    def __init__(
        self,
        robot_model: str,
        host: str,
        port: int = 18375,
        ee_DO_type: str = None,
        ee_DO_num: int = None,
        socket_timeout: int = 60,
    ):
        """[summary]

        Args:
            robot_model (str): Robot model: Fanuce, Kuka, etc.
            host (str): IP address of host.
            port (int): Port number. Defaults to 18735.
            ee_DO_type (str, optional): End-effector digital output type.
                                        Fanuc used RDO type. Defaults to None.
                                        Others may use DO type.
            ee_DO_num (int, optional): End-effector digital output number.
                                       Defaults to None.
            socket_timeout(int): Socket timeout in seconds. Defaults to 5 seconds.
        """
        super().__init__()

        self.robot_model = robot_model
        self.host = host
        self.port = port
        self.ee_DO_type = ee_DO_type
        self.ee_DO_num = ee_DO_num
        self.sock_buff_sz = 1024
        self.socket_timeout = socket_timeout
        self.comm_sock = None
        self.SUCCESS_CODE = 0
        self.ERROR_CODE = 1

    def __version__(self):
        print("MAPPDK Robot class v0.1.12")

    def handle_response(self, resp: str, verbose: bool = False):
        """Handles response from socket communication.

        Args:
            resp (str): Response string returned from socket.
            verbose (bool, optional): [description]. Defaults to False.

        Returns:
            tuple(int, str): Response code and response message.
        """
        code, msg = resp.split(":")
        code = int(code)

        if code == self.SUCCESS_CODE:
            if verbose:
                print(f"The instruction was successfully executed. Message: {msg}.")
        elif code == self.ERROR_CODE:
            raise Exception(msg)
        else:
            print(f"Something wrong: {msg}")
            sys.exit()

        return code, msg

    def connect(self) -> None:
        """Connects to the physical robot."""
        # create socket and connect
        self.comm_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.comm_sock.settimeout(self.socket_timeout)
        self.comm_sock.connect((self.host, self.port))
        resp = self.comm_sock.recv(self.sock_buff_sz).decode()
        _, _ = self.handle_response(resp, verbose=True)

    def disconnect(self) -> None:
        self.comm_sock.close()

    def send_cmd(self, cmd: str):
        """Sends command to a physical robot.

        Args:
            cmd (str): Command string.

        Returns:
            tuple(int, str): Response code and response message.
        """
        # end of command character
        cmd = cmd.strip() + "\n"

        # 1. send
        self.comm_sock.sendall(cmd.encode())

        # 2. wait for a result
        resp = self.comm_sock.recv(self.sock_buff_sz).decode()
        return self.handle_response(resp)

    def call_prog(self, prog_name: str) -> None:
        """Calls external program name in a physical robot.

        Args:
            prog_name ([str]): External program name.
        """
        cmd = f"mappdkcall:{prog_name}"
        self.send_cmd(cmd)

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

    def get_curpos(self):
        """Gets current cartesian position of tool center point.

        Returns:
            list[float]: Current positions XYZWPR.
        """

        cmd = "curpos"
        _, msg = self.send_cmd(cmd)
        vals = [float(val.split("=")[1]) for val in msg.split(",")]
        return vals

    def get_curjpos(self):
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
        move_type: str,
        vals: list,
        velocity: int = 25,
        acceleration: int = 100,
        cnt_val: int = 0,
        linear: bool = False,
    ) -> None:
        """Moves robot.

        Args:
            move_type (str): Movement type (joint or pose).
            vals (list[real]): Position values.
            velocity (int, optional): Percentage or mm/s. Defaults to 25%.
            acceleration (int, optional): Percentage or mm/s^2. Defaults to 100%.
            cnt_val (int, optional): Continuous value for stopping. Defaults to 50.
            linear (boolean, optioal): Linear movement. Defaults to False.

        Raises:
            ValueError: raises if movement type is not one of ("movej", "movep")
        """

        # prepare velocity. percentage or mm/s
        # format: aaaa, e.g.: 0001%, 0020%, 3000 mm/s
        velocity = int(velocity)
        velocity = f"{velocity:04}"

        # prepare acceleration. percentage or mm/s^2
        # format: aaaa, e.g.: 0001%, 0020%, 0100 mm/s^2
        acceleration = int(acceleration)
        acceleration = f"{acceleration:04}"

        # prepare CNT value
        # format: aaa, e.g.: 001, 020, 100
        cnt_val = int(cnt_val)
        assert 0 <= cnt_val <= 100, "Incorrect CNT value."
        cnt_val = f"{cnt_val:03}"

        if move_type == "joint":
            cmd = "movej"
        elif move_type == "pose":
            cmd = "movep"
        else:
            raise ValueError("Incorrect movement type!")

        if linear:
            motion_type = 1
        else:
            motion_type = 0

        cmd += f":{velocity}:{acceleration}:{cnt_val}:{motion_type}:{len(vals)}"

        # prepare joint values
        for val in vals:
            vs = f"{abs(val):013.6f}"
            if val >= 0:
                vs = "+" + vs
            else:
                vs = "-" + vs
            cmd += f":{vs}"

        # call send_cmd
        self.send_cmd(cmd)

    def gripper(self, value: bool) -> None:
        """Opens/closes robot gripper.

        Args:
            value (boolean): True or False
        """
        if (self.ee_DO_type is not None) and (self.ee_DO_num is not None):
            value = "true" if value else "false"

            cmd = ""
            if self.ee_DO_type == "RDO":
                cmd = "setrdo"
            elif self.ee_DO_type == "DO":
                cmd = "setdo"
            else:
                raise ValueError("Wrong DO type!")

            cmd = cmd + f":{self.ee_DO_num }:{value}"
            self.send_cmd(cmd)
        else:
            raise ValueError("DO type or number is None!")

    def get_rdo(self, rdo_num: int):
        """Get RDO value.

        Args:
            rdo_num (int): RDO number.

        Returns:
            rdo_value: RDO value.
        """
        cmd = f"getrdo:{rdo_num}"
        _, rdo_value = self.send_cmd(cmd)
        rdo_value = int(rdo_value)
        return rdo_value

    def set_rdo(self, rdo_num: int, val: bool):
        """Sets RDO value.

        Args:
            rdo_num (int): RDO number.
            val (bool): Value.
        """
        if val:
            val = "true"
        else:
            val = "false"
        cmd = f"setrdo:{rdo_num}:{val}"
        self.send_cmd(cmd)

    def get_dout(self, dout_num: int):
        """Get DOUT value.

        Args:
            dout_num (int): DOUT number.

        Returns:
            dout_value: DOUT value.
        """
        cmd = f"getdout:{dout_num}"
        _, dout_value = self.send_cmd(cmd)
        dout_value = int(dout_value)
        return dout_value

    def set_dout(self, dout_num: int, val: bool):
        """Sets DOUT value.

        Args:
            dout_num (int): DOUT number.
            val (bool): Value.
        """
        if val:
            val = "true"
        else:
            val = "false"
        cmd = f"setdout:{dout_num}:{val}"
        self.send_cmd(cmd)

    def set_sys_var(self, sys_var: str, val: bool):
        """Sets system variable to True or False.

        Args:
            sys_var (str): System variable name.
            val (bool): Value.
        """
        if val:
            val = "T"
        else:
            val = "F"
        cmd = f"setsysvar:{sys_var}:{val}"
        self.send_cmd(cmd)
