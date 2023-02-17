import time

import py_trees

from autonomy.okon_actions import Exit, Rotate
from communicationThreads.Simulation.okon_sim_client import OkonSimClient

oc = OkonSimClient(ip="127.0.0.1", port=44210, sync_interval=0.05, debug=False)
oc.connect()
time.sleep(1.0)


def create_root():
    root = py_trees.composites.Sequence("testing", True)
    rotate_45 = Rotate(name="Rotate", okon=oc.okon, add_angle=-20.0, delta=1.0)
    exit = Exit(name="Exit")
    root.add_children([rotate_45, exit])
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
