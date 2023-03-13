import numpy as np
from fanucpy import Robot

robot = Robot(
    robot_model="Fanuc",
    host="127.0.0.1",
    port=18735,
    ee_DO_type="RDO",
    ee_DO_num=7,
)

robot.__version__()

robot.connect()

# get robot state
print("Current poses: ")
cur_pos = robot.get_curpos()
cur_jpos = robot.get_curjpos()
print(f"Current pose: {cur_pos}")
print(f"Current joints: {cur_jpos}")

# move in joint space
robot.move(
    "joint",
    vals=np.array(cur_jpos) + 0.5,
    velocity=100,
    acceleration=100,
    cnt_val=0,
    linear=False,
)

print("Poses after moving: ")
cur_pos = robot.get_curpos()
cur_jpos = robot.get_curjpos()
print(f"Current pose: {cur_pos}")
print(f"Current joints: {cur_jpos}")
