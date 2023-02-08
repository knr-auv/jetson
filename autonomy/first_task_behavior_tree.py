"""Script with implementation of behavior tree designed for first SAUVC task (omitting flare)"""
import time

import py_trees

from autonomy.okon_actions import (
    CalculateDeltaYaw,
    Exit,
    IsBranch1Executed,
    IsGateFarEnough,
    Rotate,
    RotateDeltaYawAngle,
    SetDepth,
    SetGuard1True,
    SetVelocity,
    TryDetectNTimes,
    Wait,
)
from communicationThreads.Simulation.okon_sim_client import OkonSimClient

oc = OkonSimClient(ip="127.0.0.1", port=44210, sync_interval=0.05, debug=False)
oc.connect()
time.sleep(1.0)


def create_root():
    root = py_trees.composites.Sequence("testing", True)

    sequence_1 = py_trees.composites.Sequence("First sequence", True)
    sequence_2 = py_trees.composites.Sequence("Second sequence", True)

    rotate_left = Rotate(name="rotate left", okon=oc.okon, add_angle=-45.0, delta=1.0)
    rotate_right = Rotate(name="rotate left", okon=oc.okon, add_angle=45.0, delta=1.0)
    set_velocity = SetVelocity(name="setting velocity", okon=oc.okon, z=1.0)
    wait = Wait(name="wait", okon=oc.okon, secs=2.0)
    stop_okon = SetVelocity(name="stopping okon", okon=oc.okon, z=0)
    exit_action = Exit(name="exit")
    set_guard = SetGuard1True(name="setting guard true", okon=oc.okon)
    is_executed = IsBranch1Executed(name="does guard work?", okon=oc.okon)

    sequence_1.add_children([set_velocity, wait, set_guard, stop_okon])
    sequence_2.add_children([is_executed, rotate_right, exit_action])

    root.add_children([sequence_1, sequence_2])
    return root


def main():
    py_trees.logging.level = py_trees.logging.Level.DEBUG

    root = create_root()

    root.setup_with_descendants()
    for tick in range(200):
        try:
            print(f"\n{f'{tick = }':.^30}\n")
            root.tick_once()
            print("\n")
            print(py_trees.display.unicode_tree(root=root, show_status=True))
            print(py_trees.display.unicode_blackboard())
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
    print("\n")


if __name__ == "__main__":
    main()
