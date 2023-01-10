from Detectors.DetectorBaseClass import DetectorBaseClass


class SimulationGPU_detector(DetectorBaseClass):
    def __init__(self, cameraStream):
        super.__init__(self, cameraStream)
