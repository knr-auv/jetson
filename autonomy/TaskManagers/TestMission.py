import autonomy.Tasks.Tasks as Tasks
from .TaskManagerBase import TaskManager
import threading, time
import tools.Logger as Logger

class GateDetection:
    """
    Structure of handled Gate detection 

    """
    center_x = 0
    center_y = 0 
    width = 0
    height = 0
    width_to_x = 0 
    width_to_y = 0
    w_h_ratio = 0
    width_on_screen = 0 
    height_on_screen = 0

class Mission(TaskManager):
    """
    Menager of tasks that selects tasks and controls their progress and eventual exceptions.

    1. init hardware/software
    2. init Task Menager

    SAUVC (has its own task menager)

                       task mengaer
                      /      |     \

         Gate task    drop the ball     shoot the vapire           # independent tasks 
           |     \                                                     
            
    find the gate                                                  # dependent tasks



    RoboSub (has)
            
    if go throuig gate
        step 1
        step 2 ....

    if drop the ball
        find gate 
        .....


    if end
        return
    - 


    Steps:
      - unrelated steps for test task
      - Handle detection (thread)
      - 


    """

    name = "test mission"
    controller = None
    gate = False
    gatePos = None
    gate_w_h_ratio = 1
    max_w = 1280
    max_h = 720
    detections = list()

    def __init__(self, detector, controller):
        super().__init__(detector, controller)
        self.controller = controller
        self.detector.RegisterDetectionCallback(self.detecion_handler)
        self.Tasks = Tasks.Tasks(self.controller)
        x = None

    def exception_handler(self):
        pass

    #this function should be registered as task end callback
    #f e        self.Tasks.FindGate.RegisterTaskCallback(self.choose_task)
    #is responsible for making decisions

    def choose_task(self, task, status):
        pass

    #this function is called once when the mission is started
    def run(self):
        self.detector.StartDetecting()
        self.controller.arm()
        self.Tasks.FindGate.RegisterTaskCallback(self.choose_task)
        self.Tasks.FindGate.Start(self.choose_task)

            
          
        Logger.write('Sllep with fishes', self.name)
                
   
    def detecion_handler(self,fps, detections):
        """
            obj.type = name
            obj.accuracy = 1
            obj.distance = dist;
            obj.boundingBox = [minx,miny,maxx,maxy]
            a,b,c = [self.controlThread.getAttitude()[0],self.controlThread.getAttitude()[1],self.controlThread.getAttitude()[2]]
            pos = h.posFromPicture(107,60,dist,center_width,center_height)
            obj.position = h.toGlobalRef(pos,[a,b,c])
            obj.width = 1.2;
            obj.height =1.4;
        """
        self.detections.clear()
        for det in detections:
             if det["type"] == "gate":
                 obj = GateDetection()
                 bbox = det["boundingBox"]
                 #[minx,miny,maxx,maxy]
                 obj.height = bbox[3]-bbox[1]   #det["maxy"]-det["miny"];
                 obj.width = bbox[2]-bbox[0]    #det["maxx"]-det["minx"]
                 obj.w_h_ratio = obj.width/obj.height
                 obj.width_to_x = obj.width/self.max_w
                 obj.width_to_y = obj.height/self.max_h    
                 obj.center_x =  (bbox[2]+bbox[0])/2
                 obj.center_y =  (bbox[1]+bbox[3])/2
                # obj.height_on_screen 
                 self.detections.append(obj)