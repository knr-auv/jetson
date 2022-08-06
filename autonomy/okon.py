""" Implementation of an Abstract Base Class (ABC) Okon 

Okon ABC implementation provides unified communication between
the autonomy module and simulation/TCM.
"""
from abc import ABC, abstractmethod


class Okon(ABC):
    @abstractmethod
    def set_depth(self, depth: float, add: bool = False) -> None:
        pass

    @abstractmethod
    def set_stable_vel(self, x: float = None, y: float = None, z: float = None) -> None:
        pass

    @abstractmethod
    def arm_motors(self) -> None:
        pass

    @abstractmethod
    def disarm_motors(self) -> None:
        pass

    @abstractmethod
    def setMode(self, mode: str) -> None:
        pass

    @abstractmethod
    def reachedTargetRotation(self, delta):
        pass

    @abstractmethod
    def reachedTargetDepth(self, delta):
        pass

    @abstractmethod
    def get_detection(self, className: str):
        pass

    @abstractmethod
    def set_stable_rot(self, x: float = None, y: float = None, z: float = None, add=False) -> None:
        pass
