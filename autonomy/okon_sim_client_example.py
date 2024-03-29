import time

from communicationThreads.Simulation.okon_sim_client import OkonSimClient, PacketFlag, PacketType


def handle_simulation_reset(args=None) -> None:
    print("sim resetted")


def handle_ping(args=None) -> None:
    global sum, n
    cur_ping = round((time.time() - float(args)) * 10000) / 10
    sum += cur_ping
    n += 1


oc = OkonSimClient(
    ip="127.0.0.1", port=44210, sync_interval=0.05, debug=False
)  # ping simRST hitNGZ hitFZ packet error disconnect # run on separate thread
oc.on_event("simRST", handle_simulation_reset)
oc.on_event("ping", handle_ping)
okon = oc.okon
sim = oc.simulation

sum = 0  # ping checking
n = 0
if oc.connect():
    sim.reset()

    i = 1000
    while i > 0:  # ping checking
        oc.send(PacketType.GET_VIDEO_BYTES)
        oc.send(PacketType.PING, PacketFlag.NONE, str(time.time()))
        time.sleep(0.01)
        i -= 1
    print("waiting")
    while n < 1000:
        time.sleep(0.01)
    print(f"avg RTT is {sum/n}ms")
    exit()

    okon.disarm_motors()
    okon.set_stable_vel(x=0, y=0, z=0)

    for i in range(5):
        oc.send(PacketType.PING, PacketFlag.NONE, str(time.time()))
        time.sleep(0.1)

    print("setting pos and depth")
    okon.set_depth(0.6)
    print(okon.sens["baro"] / 1000 / 9.81 + 0.3)
    okon.set_stable_rot(y=okon.sens["imu"]["rot"]["y"])
    print(okon.sens["imu"]["rot"]["y"])
    okon.arm_motors()
    time.sleep(1)

    okon.set_stable_rot(y=50, add=True)
    print("waiting for target rotation")
    while not okon.reachedTargetRotation(1):
        time.sleep(0.1)
    print("done waiting for target rotation")

    okon.set_stable_rot(y=-50, add=True)
    while not okon.reachedTargetRotation(1):
        time.sleep(0.1)
    okon.set_stable_vel(z=1)
    while len(okon.get_detection("gate")) > 0:
        dete = okon.get_detection("gate")
        if len(dete) > 0 and dete[0]["distance"] < 4:
            okon.set_depth(1.3)

    print("passing through gate")
    time.sleep(2)
    okon.set_stable_vel(z=0)
    time.sleep(0.5)  # wait for packet to be send
