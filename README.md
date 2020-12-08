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


## Usage

### Startup
Okon can operate with and without GUI. Nevertheless they are some common requirements:
- Make sure you have installed following python modules:
  - numpy
- Download [Simulation](https://github.com/knr-auv/simulation/ "Simulation")
- Download [GUI](https://github.com/knr-auv/GUI-v2 "GUI") (optional)

In both cases it is nessecary to launch simulation first, than you can launch main.py (version withou GUI is not suported yet).

### Important notes
Launching jetson without running simulation will fail. If program can't establish connection with simulation or GUI please make sure that IP adresses are corect. If problem still occurs try disabling your firewall.
If you have low performance PC it is recomended to launch simulation on another desktop in LAN.
