# FANUC MAPPDK Driver

## 0. Software compatibility
Fanuc controllers must have the following modules enabled:
- R632 - KAREL
- R648 - User Socket Messaging

Check the compatibility:
1. Go to **MENU** -> **NEXT** -> **STATUS** -> **Version ID**.
![image](https://user-images.githubusercontent.com/67538561/169281756-e59e61af-3a40-4c8a-aa00-94123f3ba3e3.png)

3. Click **ORDER FI**.
![image](https://user-images.githubusercontent.com/67538561/169282210-865d139e-1bad-4598-80c0-086461c159a6.png)

4. Check for **R632** and **648** in the list.
![image](https://user-images.githubusercontent.com/67538561/169282483-d85084dc-d572-4bbf-9d5d-dc9057802e01.png)

For roboguide software, there are two possibilities. 
1. The roboguide cell is already existing, now we need to update the robot options to install R632 and R648. Then use the instructions below to serailize the robot and install the R632 and R648 package.  
![image](https://user-images.githubusercontent.com/67538561/169279461-eec2fbec-18d1-46f2-81e9-903dcdb88ba6.png)

Then you will enter the virtual robot edit wizard to install the R632 and R648
![image](https://user-images.githubusercontent.com/67538561/169279787-9e8fac9b-9e72-42d5-8d6e-abfe48e7aec0.png)

2. It is a new workcell, which means you can install the R632 and R648 at the very first begining. 

## 1. Network connection
Set up the ethernet connection with host and robot controller, then follow the below steps:
1. Go to **MENU** -> **SETUP** -> **Host Comm**.
![3](https://user-images.githubusercontent.com/67538561/169283076-5172b547-660e-42f0-9447-cb79ed5f114f.png)

2. Go to **TCP/IP**
  real robot:
  - Set the **Robot name**, the **IP addr** to **192.168.234.2** or IP in the same subnet as the host computer. This is the IP address of the robot controller.
  roboguide: 
  - The IP address is **127.0.0.1** by default
4. Set the **Subnet Mask** to **255.255.255.0**.
5. Set **Host Name** and **Internet Address**. This is the IP address of the host computer.
![image](https://user-images.githubusercontent.com/67538561/169283497-e25bc159-74ef-43d2-b2fe-008b5076b062.png)

6. Disable DHCP: **DHCP** -> **DHCP Enable**: **False**.
7. Activate the above settings by pressing **INIT**.


## 2. Server setup
The FANUC MAPPDK server by default uses server tag **'S8:'** and port **18735**.
1. Go to **MENU** ->**Next** -> **SYSTEM** -> **Variables**.
    * 1.1. Select **$HOSTS_CFG**.
    
    ![image](https://user-images.githubusercontent.com/67538561/169284408-8736d381-c708-4422-989f-58de8743f9f2.png)

    * 1.2. Press enter to select the number **8**.
    *
    * 1.3. Once you enter into a new place, set the variable **$SERVER_PORT** to **18735**.
    ![image](https://user-images.githubusercontent.com/67538561/169285678-88508464-2651-4f4c-8c15-52c67ccf9747.png)

2. Go to **MENU** -> **SETUP** -> **Host Comm**.
    * 2.1. Select **SHOW** -> **Servers**.
    * 2.2. Select **S8**.
    * 2.3. Set **Protocol** to **SM**.
    * 2.4. Set **Port** to **18735**.
    * 2.5. Set **Startup State** to **START**.
    * 2.6. Set **Current State** to **STARTED**:
        * Select **\[ACTION\]** -> **DEFINE**.
        * Select **\[Action\]** -> **START**.
        ![image](https://user-images.githubusercontent.com/67538561/169286175-271bb666-d8c1-4415-a55d-89ab2a65ddf1.png)


## 3. Logger setup
The FANUC MAPPDK logger by default uses server tag **'S7:'** and port **18736**.
To setup the logger, follow the step for the FANUC MAPPDK server setup. Use **S7** as the server, and **18736** as the port number.
![image](https://user-images.githubusercontent.com/67538561/169286578-fc57f24d-32bd-4620-a0f6-2fdd8814a149.png)



## 4. Running MAPPDK
1. Copy the following files to a robot controller either using USB flash drive or FTP connection:
    * **mappdk.ls**: The MAPPDK main file which should be run from the teach pendant. This file runs MAPPDK server and MAPPDK logger. Uncomment the corresponding line to disable the functioality.
    * **mappdk_server.pc**: The MAPPDK server file.
    * **mappdk_logger.pc**: The MAPPDK logger file.
    * **mappdk_move.ls**: The MAPPDK move file.
    * **mappdk_movel.ls**: The MAPPDK linear move file.
   ![image](https://user-images.githubusercontent.com/67538561/169286670-c283a061-9c50-4e21-b844-961c014b33d1.png)

2. In the teach pendant:
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

![4](https://user-images.githubusercontent.com/67538561/169287126-a808bb14-61ae-4124-a4db-961fb6c7f8f7.png)

2. Re-run the **MAPPDK**. 
