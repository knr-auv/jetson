import tools.Logger as Logger
from.TaskBaseClass import TaskBaseClass

class FindGateTask(TaskBaseClass):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    def adjust_y_pos(self, offset):
        Logger.write("y offset" + str(offset), self.name)
        if abs(offset)>0.006:
            self.controller.set_depth(self.controller.current_position[2] + offset*5)
            Logger.write("adjusting y position" + str(offset*2), self.name)

    def adjust_x_pos(self, offset):
        if(abs(offset)>0.025):
            self.controller.turn_right(offset*10)
            Logger.write("adjusting x position" + str(offset*50), self.name)

    def Worker(self, *args):
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
                y_offset = 0.5 - gate.center_y 
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
        self.InvokeCallback(1,1)