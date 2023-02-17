"""Module with implementation of OKON actions using py_trees"""
import math
import sys
import time

import py_trees

from communicationThreads.Simulation.okon_sim_client import OkonSim


class Status:
    SUCCESS = py_trees.common.Status.SUCCESS
    FAILURE = py_trees.common.Status.FAILURE
    RUNNING = py_trees.common.Status.RUNNING
    INVALID = py_trees.common.Status.INVALID


class SetDepth(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "set depth", okon: OkonSim = None, depth: float = 0.6, delta: float = 0.05):
        super().__init__(name)
        self.okon = okon
        self.depth = depth
        self.delta = delta
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        self.okon.set_depth(self.depth)
        new_status = Status.SUCCESS if self.okon.reachedTargetDepth(self.delta) else Status.RUNNING
        if new_status == Status.SUCCESS:
            self.feedback_message = "Target depth of {self.depth} m reached."
            self.feedback_message = (
                f"Current depth {self.okon.sens['baro'] / 1000 / 9.81:.3f}. Waiting for target depth of {self.depth} m."
            )
        self.logger.debug(f"{self.__class__.__name__}.update()[{self.status}->{new_status}][{self.feedback_message}]")
        return new_status

    def update_depth(self, new_depth):
        self.depth = new_depth

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class SetVelocity(py_trees.behaviour.Behaviour):
    def __init__(
        self, name: str = "set velocity", okon: OkonSim = None, x: float = 0.0, y: float = 0.0, z: float = 0.0
    ):
        super().__init__(name)
        self.okon = okon
        self.x = x
        self.y = y
        self.z = z
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        self.okon.set_stable_vel(x=self.x, y=self.y, z=self.z)
        new_status = Status.SUCCESS
        if new_status == Status.SUCCESS:
            self.feedback_message = f"Speed set as: Vx = {self.x:.3f} Vy = {self.y:.3f} Vz = {self.z:.3f}."
        self.logger.debug(f"{self.__class__.__name__}.update()[{self.status}->{new_status}][{self.feedback_message}]")
        return new_status

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class Rotate(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "rotate", okon: OkonSim = None, add_angle: float = 45.0, delta: float = 1.0):
        super().__init__(name)
        self.okon = okon
        self.add_angle = add_angle
        self.target_angle = self.okon.sens["imu"]["rot"]["y"] + self.add_angle
        self.delta = delta
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.target_angle = self.okon.sens["imu"]["rot"]["y"] + self.add_angle
        if self.target_angle < 0.0:
            self.target_angle += 360.0
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        self.okon.set_stable_rot(y=self.target_angle)
        new_status = Status.SUCCESS if self.okon.reachedTargetRotation(self.delta) else Status.RUNNING
        if new_status == Status.SUCCESS:
            self.feedback_message = f"Target rotation of {self.target_angle} degrees reached."
        else:
            self.feedback_message = f"Current rotation is {self.okon.sens['imu']['rot']['y']:.3f} degrees. Waiting for target rotation of {self.target_angle:.3f} degrees."
        self.logger.debug(f"{self.__class__.__name__}.update()[{self.status}->{new_status}][{self.feedback_message}]")
        return new_status

    def update_add_angle(self, new_add_angle):
        self.add_angle = new_add_angle

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class RotateDeltaYawAngle(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "rotate delta yaw angle", okon: OkonSim = None, delta: float = 1.0):
        super().__init__(name)
        self.okon = okon
        self.delta = delta
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="deltaYaw", access=py_trees.common.Access.READ)
        self.target_angle = self.okon.sens["imu"]["rot"]["y"]
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.target_angle = self.okon.sens["imu"]["rot"]["y"] + self.blackboard.deltaYaw
        if self.target_angle < 0.0:
            self.target_angle += 360.0
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        self.okon.set_stable_rot(y=self.target_angle)
        new_status = Status.SUCCESS if self.okon.reachedTargetRotation(self.delta) else Status.RUNNING
        if new_status == Status.SUCCESS:
            self.feedback_message = f"Target rotation of {self.target_angle} degrees reached."
        else:
            self.feedback_message = f"Current rotation is {self.okon.sens['imu']['rot']['y']:.3f} degrees. Waiting for target rotation of {self.target_angle:.3f} degrees."
        self.logger.debug(f"{self.__class__.__name__}.update()[{self.status}->{new_status}][{self.feedback_message}]")
        return new_status

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class TryDetectNTimes(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "try detect n times", okon: OkonSim = None, object: str = "gate", n: int = 3):
        super().__init__(name)
        self.okon = okon
        self.object = object
        self.n = n
        self.counter = 1
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="detection", access=py_trees.common.Access.WRITE)
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.counter = 1
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        detection = self.okon.get_detection(self.object)
        if len(detection) > 0:
            new_status = Status.SUCCESS
            self.blackboard.detection = detection
        elif self.counter == self.n:
            new_status = Status.FAILURE
        else:
            new_status = Status.RUNNING

        if new_status == Status.SUCCESS:
            self.feedback_message = f"Object {self.object} detected in attempt number {self.counter}"
        else:
            self.feedback_message = f"Object {self.object} undetected in attempt number {self.counter}"

        self.counter += 1

        self.logger.debug(f"{self.__class__.__name__}.update()[{self.status}->{new_status}][{self.feedback_message}]")
        return new_status

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class CalculateDeltaYaw(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "calculate delta yaw", okon: OkonSim = None):
        super().__init__(name)
        self.okon = okon
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="detection", access=py_trees.common.Access.READ)
        self.blackboard.register_key(key="deltaYaw", access=py_trees.common.Access.WRITE)
        self.delta_yaw = 0
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        detection = self.blackboard.detection
        if len(detection) > 0:
            new_status = Status.SUCCESS
            hfov = 60
            gate = detection[0]
            if gate["distance"] < 1:
                self.delta_yaw = 0
            else:
                center = (gate["max"]["x"] + gate["min"]["x"]) / 2 * 2 - 1
                camera_plane_x = 1.0 / math.tan(hfov / 2 / 180 * math.pi)
                self.delta_yaw = math.atan(center / camera_plane_x) / math.pi * 180
            self.blackboard.deltaYaw = self.delta_yaw
        else:
            new_status = Status.FAILURE

        if new_status == Status.SUCCESS:
            self.feedback_message = f"Delta Yaw was calculated and is equal to {self.delta_yaw}"
        else:
            self.feedback_message = "There were no objects in the detection parameter in blackboard."

        self.logger.debug(f"{self.__class__.__name__}.update()[{self.status}->{new_status}][{self.feedback_message}]")
        return new_status

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class IsGateFarEnough(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "calculate delta yaw", okon: OkonSim = None, max_distance: float = 1.5):
        super().__init__(name)
        self.okon = okon
        self.max_distance = max_distance
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="detection", access=py_trees.common.Access.READ)
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        gate = self.blackboard.detection[0]
        new_status = Status.SUCCESS if gate["distance"] > self.max_distance else Status.FAILURE

        if new_status == Status.SUCCESS:
            self.feedback_message = f"Gate is in distance of {gate['distance']:.3f} m."
        else:
            self.feedback_message = f"Gate is closer than max distance set to {self.max_distance:.3f}m."

        self.logger.debug(f"{self.__class__.__name__}.update()[{self.status}->{new_status}][{self.feedback_message}]")
        return new_status

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class Wait(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "wait", okon: OkonSim = None, secs: float = 0.0):
        super().__init__(name)
        self.okon = okon
        self.secs = secs
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        time.sleep(self.secs)
        new_status = Status.SUCCESS
        if new_status == Status.SUCCESS:
            self.feedback_message = f"Robot waited for {self.secs} seconds."
        self.logger.debug(f"{self.__class__.__name__}.update()[{self.status}->{new_status}][{self.feedback_message}]")
        return new_status

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class Exit(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "exit"):
        super().__init__(name)
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        sys.exit()


class SetGuard1True(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "set guard 1 true", okon: OkonSim = None):
        super().__init__(name)
        self.okon = okon
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="guard1", access=py_trees.common.Access.WRITE)
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.blackboard.guard1 = "False"
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        self.blackboard.guard1 = "True"
        new_status = Status.SUCCESS
        return new_status

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class IsBranch1Executed(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "is branch 1 executed", okon: OkonSim = None):
        super().__init__(name)
        self.okon = okon
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="guard1", access=py_trees.common.Access.READ)
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        try:
            if self.blackboard.guard1 == "True":
                new_status = Status.SUCCESS
            else:
                new_status = Status.FAILURE
        except KeyError:
            new_status = Status.FAILURE
        return new_status

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class RotateToFirstTask(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "rotate", okon: OkonSim = None, delta: float = 1.0):
        super().__init__(name)

        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="angle", access=py_trees.common.Access.READ)

        self.okon = okon

        self.target_angle = self.okon.sens["imu"]["rot"]["y"] + self.blackboard.angle
        self.delta = delta
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.target_angle = self.okon.sens["imu"]["rot"]["y"] + self.blackboard.angle
        if self.target_angle < 0.0:
            self.target_angle += 360.0
        self.logger.debug(f"{self.__class__.__name__}.initialise()")

    def update(self):
        self.okon.set_stable_rot(y=self.target_angle)
        new_status = Status.SUCCESS if self.okon.reachedTargetRotation(self.delta) else Status.RUNNING
        if new_status == Status.SUCCESS:
            self.feedback_message = f"Target rotation of {self.target_angle} degrees reached."
        else:
            self.feedback_message = f"Current rotation is {self.okon.sens['imu']['rot']['y']:.3f} degrees. Waiting for target rotation of {self.target_angle:.3f} degrees."
        self.logger.debug(f"{self.__class__.__name__}.update()[{self.status}->{new_status}][{self.feedback_message}]")
        return new_status

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")


class CalculateRotationAngle(py_trees.behaviour.Behaviour):
    def __init__(self, name: str = "calculate rotation angle", okon: OkonSim = None, add_angle: float = 5.0):
        super().__init__(name)
        self.okon = okon
        self.add_angle = add_angle
        self.side = 1

        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="angle", access=py_trees.common.Access.READ)
        self.blackboard.register_key(key="angle", access=py_trees.common.Access.WRITE)

        self.blackboard.angle = 0.0

        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def initialise(self):
        self.logger.debug(f"{self.__class__.__name__}.__init__()")

    def update(self):
        current = abs(self.blackboard.angle)
        if self.side % 2 == 1:
            self.blackboard.angle = current + self.add_angle
        else:
            self.blackboard.angle = (current + self.add_angle) * (-1)
        self.side += 1
        return Status.SUCCESS

    def terminate(self, new_status):
        """Nothing to clean up in this example."""
        self.logger.debug(f"{self.__class__.__name__}.terminate()[{self.status}->{new_status}]")
