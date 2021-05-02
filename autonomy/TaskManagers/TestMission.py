import autonomy.Tasks.Tasks as Tasks
from .TaskManagerBase import TaskManager
import threading, time
import tools.Logger as Logger
class GateDetection:
    center_x = 0
    center_y =0 
    width = 0
    height = 0
    width_to_x =0 
    width_to_y = 0
    w_h_ratio = 0
    width_on_screen = 0 
    height_on_screen = 0

class Mission(TaskManager):
    name = "test mission"
    should_work = True
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
        x = None

    def exception_handler(self):
        pass

    def adjust_y_pos(self, offset):
        Logger.write("y offset" + str(offset), self.name)
        if abs(offset)>0.006:
            self.controller.set_depth(self.controller.current_position[2] + offset*5)
            Logger.write("adjusting y position" + str(offset*2), self.name)

    def adjust_x_pos(self, offset):
        if(abs(offset)>0.025):
            self.controller.turn_right(offset*10)
            Logger.write("adjusting x position" + str(offset*50), self.name)
    def run(self):
        self.detector.StartDetecting()
        self.controller.arm()

        while self.should_work:
            #searching routine
            Logger.write('Starting autonomy loop', self.name)
            while len(self.detections)==0:
                Logger.write('Looking for gate', self.name)
                for i in range(8):
                    if(len(self.detections)==0):
                        time.sleep(0.2)
                        self.controller.turn_right(5)
                self.controller.turn_left(40)
                for i in range(8):
                    if(len(self.detections)==0):
                        time.sleep(0.2)
                        self.controller.turn_left(5)
            Logger.write('Gate found', self.name)
            gate = self.detections[0]
            y_offset = gate.center_y -0.5
            self.controller._Controller__get_current_position()
            self.adjust_y_pos(y_offset)
            x_offset = gate.center_x -0.5
            self.adjust_x_pos(x_offset)
            swim_forward = True
            while swim_forward:
                if len(self.detections)==0:
                    break
                gate = self.detections[0]
                self.controller.move_forward(700)
                time.sleep(1)
                self.controller.stop()
                should_turn = True
                while should_turn:
                    time.sleep(0.5)
                    if len(self.detections)==0:
                        break
                    gate = self.detections[0]
                    y_offset = gate.center_y -0.5
                    self.controller._Controller__get_current_position()
                    self.adjust_y_pos(y_offset)
                    x_offset = gate.center_x -0.5
                    self.adjust_x_pos(x_offset)
                    Logger.write('Adjustuing positon', self.name)
                    if(x_offset<0.2):
                        should_turn = False
                swim_forward = (gate.height_on_screen <0.6)
                Logger.write("gate h: " + str(gate.height), self.name)
                Logger.write('Swiming to gate', self.name)
            Logger.write('Swiming throught gate', self.name)
            self.controller.move_forward(700)
            time.sleep(2)
            self.controller.stop()
            self.should_work = False
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
     
        


   