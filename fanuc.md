# FANUC MAPPDK Driver

## 0. Software compatibility
Fanuc controllers must have the following modules enabled:
- R632 - KAREL
- R648 - User Socket Messaging

Check the compatibility:
1. Go to **MENU** -> **STATUS** -> **Version ID**.
2. Click **ORDER FI**.
3. Check for **R632** and **648** in the list.

## 1. Network connection
Set up the ethernet connection with host and robot controller, then follow the below steps:
1. Go to **MENU** -> **SETUP** -> **Host Comm**.
2. Set the **Robot name**.
3. Set the **IP addr** to **192.168.1.100** or IP in the same subnet as the host computer. This is the IP address of the robot controller.
4. Set the **Subnet Mask** to **255.255.255.0**.
5. Set **Host Name** and **Internet Address**. This is the IP address of the host computer.
6. Disable DHCP: **DHCP** -> **DHCP Enable**: **False**.
7. Activate the above settings by pressing **INIT**.


## 2. Server setup
The FANUC MAPPDK server by default uses server tag **'S8:'** and port **18735**.
1. Go to **MENU** -> **SYSTEM** -> **Variables**.
    * 1.1. Select **$HOSTS_CFG**.
    * 1.2. Select the number **8**.
    * 1.3. Set the variable **$SERVER_PORT** to **18735**.
2. Go to **MENU** -> **SETUP** -> **Host Comm**.
    * 2.1. Select **SHOW** -> **Servers**.
    * 2.2. Select **S8**.
    * 2.3. Set **Protocol** to **SM**.
    * 2.4. Set **Port** to **18735**.
    * 2.5. Set **Startup State** to **START**.
    * 2.6. Set **Current State** to **STARTED**:
        * Select **\[ACTION\]** -> **DEFINE**.
        * Select **\[Action\]** -> **START**.

## 3. Logger setup
The FANUC MAPPDK logger by default uses server tag **'S7:'** and port **18736**.
To setup the logger, follow the step for the FANUC MAPPDK server setup. Use **S7** as the server, and **18736** as the port number.

## 4. Running MAPPDK
1. Copy the following files to a robot controller either using USB flash drive or FTP connection:
    * **mappdk.ls**: The MAPPDK main file which should be run from the teach pendant. This file runs MAPPDK server and MAPPDK logger. Uncomment the corresponding line to disable the functioality.
    * **mappdk_server.pc**: The MAPPDK server file.
    * **mappdk_logger.pc**: The MAPPDK logger file.
    * **mappdk_move.ls**: The MAPPDK move file.
    * **mappdk_movel.ls**: The MAPPDK linear move file.
2. In TP:
    * 2.1. Press **SELECT**.
    * 2.2. Locate **MAPPDK**.
    * 2.3. Run in **T1/T2** or **AUTO** mode.


## 5. Reserved registers and frames.
* MAPPDK uses the **USER FRAME=8** and **TOOL FRAME=8**.
* MAPPDK uses registers **R[81]** for velocity,  **R[82]** for acceleration, and **R[83]** fo continuous value.
* MAPPDK uses position register **PR[81]** for position and joint values.

## 6. Troubleshooting
In case of error or hanging python script:
1. Select **FCTN** -> **ABORT ALL**.
2. Re-run the **MAPPDK**. 