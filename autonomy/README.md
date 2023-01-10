# knr-auv/autonomy

knr-auv/autonomy is a software for the development of a behavior tree-based autonomy module for the OKOŃ AUV built by KNR AUV team.

## Behavior Tree Editor

Behavioral tree projects placed in the BTs directory can be opened/edited using [the Behavior Tree Visual Editor](https://opensource.adobe.com/behavior_tree_editor).

Links to JSON files with projects of Behavior Trees:

- [Qualification Task Behavior Tree](BTs/qualificationTaskProjet.json)

## py_trees

[Demo files](https://github.com/splintered-reality/py_trees/tree/devel/py_trees/demos) useful for implementaion software using py_trees library can be found in [the official repository](https://github.com/splintered-reality/py_trees).

## Usage    ```

### Running Qualification Task Behavior Tree

1. Run Okon.exe file (simulation-2.3dev)

2. Activate Conda Environment

    ```bash
    $ conda activate jetson
    ```

3. Make sure you're on the repos root directory (`jetson/`). All imports are relative to the root in this project, so they can be easily imported in other directories. We also need to use this as a package.
    ```bash
    $ ls
    .../jetson
    ```

3. Move AUV to starting position

    ```bash
    $ python autonomy/go_to_starting_line.py
    ```

4. Run Behavior Tree

    ```bash
    $ python autonomy/qualification_task_behavior_tree.py
    ```
