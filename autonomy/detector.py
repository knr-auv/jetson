import autonomy.darknet.darknet as darknet
import cv2,logging
def draw_rectangle(img,centerx, centery, width, height):
    top_left = (int((centerx-width/2)),int(centery-height/2))
    bottom_right = (int((centerx+width/2)),int(centery+height/2))
    cv2.rectangle(img,top_left,bottom_right,(0,255,0),1)

class detector:
    def __init__(self, config, data, weights):
        self.network, self.class_names, self.colors = darknet.load_network(config, data, weights, 1)
        self.width = darknet.network_width(self.network)
        self.height = darknet.network_height(self.network)
        self.darknet_image = darknet.make_image(self.width, self.height, 3)

    def detect_distance(self, img, gray_scale):
            image, detections= self.detect(img,0.8)
            for i in range(len(detections)):
                name, pr, pos = detections[i]
                print(detections[i])
                dist = 0
                try:
                    dist = self.distance_to_gate(image,gray_scale,pos)
                except:
                    dist =0
                detections[i].insert(2,dist)
            return image, detections

    def detect(self, image, threshold):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (self.width, self.height), interpolation=cv2.INTER_LINEAR)
        darknet.copy_image_from_bytes(self.darknet_image, image_resized.tobytes())
        detections = darknet.detect_image(self.network, self.class_names, self.darknet_image,thresh=threshold)
        scaled_detections = list()
        for i in range(len(detections)):
            temp = list()
            temp.append(detections[i][0])
            temp.append(detections[i][1])
            h = image.shape[0]/self.height
            w= image.shape[1]/self.width
            temp.append((detections[i][2][0]*w,detections[i][2][1]*h,detections[i][2][2]*w,detections[i][2][3]*h ))
            scaled_detections.append(temp)
        return image ,scaled_detections

    def distance_to_gate(self, color_image,depth_map, pos): #przyjmuje normalne zdjecie,mape glebi i wspołrzedne ramki wykrycia bramki -> zwraca natezenie srednie RGB bramki
        centerx, centery,width, height = pos
        height = int(height)
        width = int(width)
        #konwersja zdjecia kolorowego zeby tlo bylo cale czarne a ramka pozostałą biała z drobnymi wtrąceniami innych kolorów
        changed_color=cv2.cvtColor(color_image,cv2.COLOR_BGR2HSV)
        ret,threshold=cv2.threshold(changed_color,128,255,1)
        black_background=cv2.cvtColor(threshold,cv2.COLOR_HSV2BGR)
        #zapis tylko tych pikseli z ramki które nie sa czarne
        rgb=[]
        top_left = (int(centerx - width / 2), int(centery - height / 2))
        for i in range(top_left[1],top_left[1]+height): #os y
            for j in range(top_left[0],top_left[0]+width): #os x
                if not(black_background[i,j,0]==0 and black_background[i,j,1]==0 and black_background[i,j,2]==0) and depth_map[i,j,0]>40:
                    rgb.append(depth_map[i,j,0])#tylko 1 element wszyskie piksele w depth_map maja wszystkie 3 wartowsci takie same
        #wyciągniecie sredniej
        sum=0
        for i in rgb:
            sum+=i
        distance=round(sum/len(rgb))
        return distance/40*0.3

      
