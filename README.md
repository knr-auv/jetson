# jetson-v2
Jetson v2 is software written with the purpose of controlling Okon - an AUV built by KNR AUV team. The target platform is Nvidia Jetson Nano.

Software includes:
 - API for comunication with [GUI](https://github.com/knr-auv/GUI-v2 "GUI")
 - [Simulation](https://github.com/knr-auv/simulation/ "Simulation") web API client
 - API for comunicating with Okon's control module
 - PID controller intended to use with simulation
 - Autonomy logic based on: zed camera, darknet, attitude estimation

## Table of contents

- [Usage](#usage)
  - [Startup](#startup)
  - [Important notes](#important-notes)
* [Networking](#networking)
  - [Packet structure](#packet-structure)
      - [Request packet](#request-packet)
      - [Steering packet](#steering-packet)
      - [Control packet](#control-packet)
      - [Settings packet](#settings-packet)
  - [Packet types to jetson](#packet-types-to-jetson)
  - [Packet types from jetson](#packet-types-from-jetson)


## Usage
### Prerequisites
To kick off with Jetson, you should set up Conda environment and install internal dependencies(simulation, GUI).

### Creating Conda Environment with Dependencies (Python)

1. Create Conda Environment and Install Dependencies

    ```bash
    conda env create -f environment.yml
    ```

2. Activate Conda Environment

    ```bash
    conda activate jetson
    ```

### Updating Dependencies (Python) - if environment.yml file changed
1. Activate Conda Environment

    ```bash
    conda activate jetson
    ```

2. Update Conda Environment Dependencies

    ```bash
    conda env update -f environment.yml --prune
    ```
### Dependencies
Okon can operate with and without GUI. Nevertheless they are some common requirements:
- Download release 2.3 of [Simulation](https://github.com/knr-auv/simulation/ "Simulation")
- Download release 1.0.2 of [GUI](https://github.com/knr-auv/GUI-v2 "GUI")

In both cases it is nessecary to launch simulation first, than you can launch main_GUI.py. After that, you should run GUI.
GUI in networking settings should have _control port: 65531_ and _stream port: 8090_ to allow you to connect to simulation and GUI.

### Important notes
Launching jetson without running simulation will fail. If program can't establish connection with simulation or GUI please make sure that IP adresses are corect. If problem still occurs try disabling your firewall.
If you have low performance PC it is recomended to launch simulation on another desktop in LAN.

## Coordinates system
![coordinates](https://github.com/knr-auv/jetson-v2/blob/develop/okonCoordinates.png?raw=true)

## Networking
App comunicates with Jetson using TCP sockets:
 - video default port is 8090
 - control default port is 8080
 
Both ports can be adjusted in settings.

### Packet structure
All control packets consist of header and data. Header is defined in following way:

| Data length | Packet type |
| ----------- | ----------- |
| 4 bytes (uint32)| 1 byte|

TODO: describe stream header

### Packet types to jetson
- Request `0x01`
- Steering `0x02`
- Control `0x03`
- Settings `0x04`

#### Request packet
Packet used for requesting data from jetson. Jetson should respond with appropriate data.
- `0x01` PID request
- `0x02` config request - wtf?

#### Steering packet
Packet used for controlling jetson movement.
- `0x01` pad data - int[5] - roll, pitch, yaw , forward, vertical
- `0x02` mode acro - sending this packet will change PID controller mode to acro
- `0x03` mode stable - sending this packet will change PID controller mode to stable

#### Control packet
- `0x01` arm 
- `0x02` disarm
- `0x03` start autonomy
- `0x04` stop autonomy
- `0x05` start telemetry
- `0x06` start detector
- `0x07` stop detector
- `0x08` set motors int[6]

#### Settings packet
  - `0x01` PID - data is double[16] with pid values in order: roll, pitch,yaw, depth

### Packet types from jetson
- Telemetry `0x01`
- Request responce `0x02`
- Autonomy `0x03`
- Status `0x04`
- Setting `0x05`

#### Telemetry packet
Packets for sending telemetry data.
- `0x01` motors  - float[6]
- `0x02` IMU - float[13], attitude, acc, gyro, mag, depth
- `0x03` movement info - float[9], position, velocity, acceleration
- `0x04` Battery

#### Request responce packet
- `0x01` PID -double[16] with pid values in order: roll, pitch,yaw, depth
- `0x02` arm confirm
- `0x03` disarm confirm

#### Autonomy packet
- `0x01` detection
- `0x02` autonomy started
- `0x03` autonomy stoped
- `0x04` detector started
- `0x05` detector stoped

#### Status packet
- `0x01` loggs
- `0x02` sensor statur
- `0x03` task_manager
- `0x04` mode pc_simulation
- `0x05` mode jetson_stm
- `0x06` mode jetson_simulation
