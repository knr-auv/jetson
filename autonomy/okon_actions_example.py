""" Script for showing usage of actions defined in okon_acions module.

Script prepared for testing actions defined in okon_actions module
in OKON simulation (simulation-2.3dev version).

Run this script after starting the simulation.
"""
import time

import py_trees

from autonomy.okon_actions import Rotate, SetDepth
from autonomy.okon_sim_client import OkonSimClient

oc = OkonSimClient(ip="127.0.0.1", port=44210, sync_interval=0.05, debug=False)
oc.connect()
time.sleep(1.0)


def create_root():
    """Implementation of py_trees behavior tree using okon_actions"""
    root = py_trees.composites.Sequence("Sequence")
    set_depth_action_1 = SetDepth(name="Set Depth to 0.2 m", okon=oc.okon, depth=0.2, delta=0.005)
    rotate_action_2 = Rotate(name="Turn left", okon=oc.okon, add_angle=-45.0, delta=1.0)
    set_depth_action_3 = SetDepth(name="Set Depth to 0.8 m", okon=oc.okon, depth=0.8, delta=0.005)
    rotate_action_4 = Rotate(name="Turn right", okon=oc.okon, add_angle=45.0, delta=1.0)
    root.add_children([set_depth_action_1, rotate_action_2, set_depth_action_3, rotate_action_4])
    return root


def main():
    """Main function of the script"""
    py_trees.logging.level = py_trees.logging.Level.DEBUG

    root = create_root()
    root.setup_with_descendants()

    for tick in range(30):
        try:
            print(f"\n{f'{tick = }':.^30}\n")
            root.tick_once()
            print("\n")
            print(py_trees.display.unicode_tree(root=root, show_status=True))
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
    print("\n")


if __name__ == "__main__":
    main()
