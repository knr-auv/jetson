""" Script for setting OKON on the starting line

Script prepared for testing autonomy using a behavior tree
in a qualification task (yellow gate) in OKON simulation (simulation-2.3dev version).
The script controls OKON to position itself on the starting line (touching the pool wall).

Run this script after starting the simulation.
Run this script before running qualification_task_behavior_tree.py script.
"""
import time

from communicationThreads.Simulation.okon_sim_client import OkonSimClient

oc = OkonSimClient(ip="127.0.0.1", port=44210, sync_interval=0.05, debug=False)
okon = oc.okon

sim = oc.simulation

if oc.connect():

    sim.reset()
    time.sleep(0.5)

    print("Initialization.")

    okon.disarm_motors()
    okon.set_stable_vel(x=0, y=0, z=0)
    okon.set_depth(0.6)
    okon.set_stable_rot(y=okon.sens["imu"]["rot"]["y"])

    okon.arm_motors()
    time.sleep(1)

    print("Reaching the starting line...")

    okon.set_stable_rot(y=0, add=True)
    while not okon.reachedTargetRotation(1):
        time.sleep(0.1)

    okon.set_stable_vel(z=-1)
    time.sleep(0.5)
    okon.set_stable_vel(z=0)
    time.sleep(1.5)
    print("Starting line reached.")

else:
    print("Error")
