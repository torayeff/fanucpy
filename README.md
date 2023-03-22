# fanucpy: Python package for FANUC industrial robots

## Software contents
The package consists of two parts: 
1. Robot interface code written in Python programming language
2. FANUC robot controller driver (tested with R-30iB Mate Plus Controller) written in KAREL and FANUC teach pendant languages

The communication protocol between the Python package and the FANUC robot controller is depicted below:
![Communication Protocol](https://github.com/torayeff/fanucpy/raw/main/media/CommProtocol.png)

## Python package installation
```bash
pip install fanucpy
```

## Driver installation
Follow these [steps](https://github.com/torayeff/fanucpy/blob/main/fanuc.md) to install FANUC driver.

## Usage
### Connect to a robot:
```python
from fanucpy import Robot

robot = Robot(
    robot_model="Fanuc",
    host="192.168.1.100",
    port=18735,
    ee_DO_type="RDO",
    ee_DO_num=7,
)

robot.connect()
```

### Moving
```python
# move in joint space
robot.move(
    "joint",
    vals=[19.0, 66.0, -33.0, 18.0, -30.0, -33.0],
    velocity=100,
    acceleration=100,
    cnt_val=0,
    linear=False
)

# move in cartesian space
robot.move(
    "pose",
    vals=[0.0, -28.0, -35.0, 0.0, -55.0, 0.0],
    velocity=50,
    acceleration=50,
    cnt_val=0,
    linear=False
)
```

### Opening/closing gripper
```Python
# open gripper
robot.gripper(True)

# close gripper
robot.gripper(False)
```

### Querying robot state
```python
# get robot state
print(f"Current pose: {robot.get_curpos()}")
print(f"Current joints: {robot.get_curjpos()}")
print(f"Instantaneous power: {robot.get_ins_power()}")
print(f"Get gripper state: {robot.get_rdo(7)}")
```

### Calling external program
```python
robot.call_prog(prog_name)
```

### Get/Set RDO
```python
robot.get_rdo(rdo_num=7)
robot.set_rdo(rdo_num=7, value=True)
```

## Contributions
External contributions are welcome!

- Agajan Torayev: Key developer
- Karol
- Fan Mo: Support with documentation
- Michael Yiu: External contributor


## RobotApp
We introduce an experimental feature: Robot Apps. This class facilitates modularity and plug-and-produce functionality. Check the following example apps:

1. [Pick and Place App](examples/PickAndPlaceApp.py)
1. [Aruco Tracking App](examples/ArucoTrackingApp.py)
1. [FANUC ChatGPT](examples/fanucpy-gpt/README.MD)

## Citation
Please use the following to cite if you are using this library in academic publications [Towards Modular and Plug-and-Produce Manufacturing Apps](https://www.sciencedirect.com/science/article/pii/S2212827122004255)
```
@article{torayev2022towards,
  title={Towards Modular and Plug-and-Produce Manufacturing Apps},
  author={Torayev, Agajan and Mart{\'\i}nez-Arellano, Giovanna and Chaplin, Jack C and Sanderson, David and Ratchev, Svetan},
  journal={Procedia CIRP},
  volume={107},
  pages={1257--1262},
  year={2022},
  publisher={Elsevier}
}
```

## Acknowledgements
This work was developed at the [Institute for Advanced Manufacturing at the University of Nottingham](https://www.nottingham.ac.uk/ifam/index.aspx) as a part of the [Digital Manufacturing and Design Training Network](https://dimanditn.eu/).

This project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie Skłodowska-Curie grant agreement No 814078.
