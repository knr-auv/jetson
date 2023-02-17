"""Script with implementation of behavior tree designed for first SAUVC task (omitting flare)"""
import time

import py_trees

from autonomy.okon_actions import (
    CalculateDeltaYaw,
    CalculateRotationAngle,
    Exit,
    IsBranch1Executed,
    IsGateFarEnough,
    Rotate,
    RotateDeltaYawAngle,
    RotateToFirstTask,
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

    selector_11 = py_trees.composites.Selector("selector_11", True)
    sequence_12 = py_trees.composites.Sequence("sequence_12", True)
    selector_13 = py_trees.composites.Selector("First selector", True)
    sequence_14 = py_trees.composites.Sequence("Second sequence", True)
    inverter_14 = py_trees.decorators.Inverter("Inverter_14", sequence_14)

    selector_41 = py_trees.composites.Selector("selector_41", True)
    sequence_421 = py_trees.composites.Sequence("sequence_421", True)
    sequence_422 = py_trees.composites.Sequence("sequence_422", True)
    selector_43 = py_trees.composites.Selector("selector_43", True)
    sequence_44 = py_trees.composites.Sequence("sequence_44", True)
    inverter_44 = py_trees.decorators.Inverter("Inverter_44", sequence_44)

    set_velocity = SetVelocity(name="setting velocity", okon=oc.okon, z=1.0)
    set_guard = SetGuard1True(name="setting guard true", okon=oc.okon)
    calculate_angle = CalculateRotationAngle(name="calculate rotation angle", okon=oc.okon, add_angle=5.0)
    rotate_to_first_task = RotateToFirstTask(name="rotate to first task", okon=oc.okon)
    detection = TryDetectNTimes(name="try detect 3 times", okon=oc.okon, object="gate", n=3)
    set_depth = SetDepth(name="set depth", okon=oc.okon, depth=0.6, delta=0.05)
    is_executed1 = IsBranch1Executed(name="is_executed1", okon=oc.okon)

    is_far_enough = IsGateFarEnough(name="Check if gate is further than 1.5 m", okon=oc.okon, max_distance=1.5)
    calc_delta_yaw = CalculateDeltaYaw(name="Calculate delta yaw", okon=oc.okon)
    set_depth_3 = SetDepth(name="set depth", okon=oc.okon, depth=0.6, delta=0.05)
    rotate_delta_yaw = RotateDeltaYawAngle(name="Turn deltaYaw angle", okon=oc.okon, delta=2.0)
    set_velocity_3 = SetVelocity(name="setting velocity", okon=oc.okon, z=1.0)
    calculate_angle_3 = CalculateRotationAngle(name="calculate rotation angle", okon=oc.okon, add_angle=5.0)
    rotate_to_first_task_3 = RotateToFirstTask(name="rotate to third branch task", okon=oc.okon)
    detection_3 = TryDetectNTimes(name="try detect 3 times", okon=oc.okon, object="gate", n=3)
    wait = Wait(name="Wait for 2 seconds", okon=oc.okon, secs=2.0)
    stop_okon = SetVelocity(name="stop okon", okon=oc.okon, z=0.0)
    exit_action = Exit(name="Exit")
    wait_for_a_while = Wait(name="Wait for 0.1 seconds", okon=oc.okon, secs=0.1)
    wait_for_1_sec = Wait(name="Wait for 2 seconds", okon=oc.okon, secs=1.0)
    detection_3_1 = TryDetectNTimes(name="try detect 3 times", okon=oc.okon, object="gate", n=3)
    set_velocity_3_1 = SetVelocity(name="setting velocity", okon=oc.okon, z=1.0)

    sequence_14.add_children([calculate_angle, rotate_to_first_task])
    selector_13.add_children([detection, inverter_14])
    sequence_12.add_children([selector_13, set_guard, set_depth, set_velocity])
    selector_11.add_children([is_executed1, sequence_12])

    sequence_44.add_children([calculate_angle_3, rotate_to_first_task_3])
    selector_43.add_children([detection_3, inverter_44])
    sequence_421.add_children(
        [
            selector_43,
            set_velocity_3_1,
            wait_for_1_sec,
            detection_3_1,
            is_far_enough,
            calc_delta_yaw,
            set_depth_3,
            rotate_delta_yaw,
            set_velocity_3,
        ]
    )

    sequence_422.add_children([wait, stop_okon, wait_for_a_while, exit_action])
    selector_41.add_children([sequence_421, sequence_422])

    root.add_children([selector_11, selector_41])

    return root


def main():
    py_trees.logging.level = py_trees.logging.Level.DEBUG

    root = create_root()

    root.setup_with_descendants()
    for tick in range(400):
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
