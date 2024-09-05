import cv2
import math
import utils
import numpy as np
from point import Point
from datetime import datetime


class image_processor:
    def __init__(self):
        self.img = None
        self.exit = None
        self.last_token_position = Point(10000, 10000)
        self.last_token_rotation = 150.8
        self.last_camera = 'j'

    def debug_show(self, image):
        cv2.imshow("V", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

#    def es_victima(self):
#        if self.img is None or self.img.size == 0:
#            return None
#        
#        grey = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
#        _, thresh = cv2.threshold(grey, 100, 255, cv2.THRESH_BINARY)
#        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#
#        return contours if len(contours) == 1 and len(contours[0]) <= 10 else None
    
#    def devolver_letra_victimas(self):
#        self.exit = None
#        crop=0 # Este crop lo vamos a utilizar cuando realizamos una transformación del cartel deformado
        # para sacarle algunos bordes negritos que nos quedan

        
        grey = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(grey, 160, 255, cv2.THRESH_BINARY)
        paraMostrarDespues=thresh.copy()
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            return self.exit


        if len(contours) == 1:
            if len(contours[0]) > 10:
                # print("Encontré un cartel que parece una letra pero tiene demasiados puntos su contorno")

                # ¿Tiene thresh una cantidad de pixeles whites razonables?
                # pixeles_whites = np.count_nonzero(thresh == 255)
                # size = thresh.shape[0] * thresh.shape[1]
                # porcentaje_whites = pixeles_whites / size
                # print("Porcentajes")
                # print(pixeles_whites, size, porcentaje_whites)
                # if porcentaje_whites < 0.05: #Si tengo pocos whites me voy
                #     return None
                


                # get the convex hull
                hull = cv2.convexHull(contours[0])
                # get the corners
                ori_points = cv2.approxPolyDP(hull, 0.01*cv2.arcLength(hull, True), True)
                if(len(ori_points) != 4):
                    # print("No es un cuadrado")
                    return self.exit

                else:
                    # get the min value of x in ori_points
                    min_x = min(ori_points[:,0,0])
                    # get the max value of x in ori_points
                    max_x = max(ori_points[:,0,0])
                    # get the min value of y in ori_points
                    min_y = min(ori_points[:,0,1])
                    # get the max value of y in ori_points
                    max_y = max(ori_points[:,0,1])
                    #Vamos a tratar de que el cartel quede cuadrado en la transformación
                    # Me fijo si lo agrando de width o de height
                    difx = max_x - min_x
                    dify = max_y - min_y
                    plusx=0
                    plusy=0
                    # calculo la mitad de lo que tengo que estirarlo, así lo corro un poquito menos en el mínimo y un poquito mas en máximo
                    if difx > dify:
                        plusy = (difx - dify) / 2
                    else:
                        plusx = (dify - difx) / 2

                    dstPoints = np.array([[min_x-plusx, min_y-plusy], [max_x+plusx, min_y-plusy], [max_x+plusx, max_y+plusy], [min_x-plusx, max_y+plusy]], dtype=np.float32)

                    ori_points = ori_points.reshape(4, 2)
                    ori_points = ori_points.astype(np.float32)

                    ori_points= utils.sortCw(ori_points)
                    dstPoints= utils.sortCw(dstPoints)
                    
                    minXPoint = ori_points[0]
                    maxXPoint = ori_points[1]
                    # print("Llegué a calcular los puntos")
                    M = cv2.getPerspectiveTransform(ori_points, dstPoints)
                    thresh = cv2.warpPerspective(thresh, M, (64, 64))
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


                    # print("Quedó de ", len(contours), len(contours[0]))
                    crop=2 # cantidad de pixels que recorto de cada lado para sacar bordes blacks
                    # print("MinXPoint: ",minXPoint)
                    # print("MaxXPoint: ",maxXPoint)
            else:
                pass
                # print("Encontró una letra copada sin tener que transformarla")

            if len(contours) == 1 and len(contours[0]) <=40:    
                
                approx = cv2.minAreaRect(contours[0])
                angle = approx[2]
                if angle % 90 == 0:
                    # print("Encontré un cartel que parece una letra")
                    x = int(approx[0][0])
                    y = int(approx[0][1])                
                    if x < 26 or x > 38:
                        # print("CHAU porque x no está en el rango", x) 
                        return None
                    if y < 26 or y > 38: 
                        # print("CHAU porque y no está en el rango")
                        return None
                    half_width = int(approx[1][0] / 2)-crop
                    half_height = int(approx[1][1] / 2)-crop
                    
                    rect = thresh[y - half_height:y + half_height, x - half_width:x + half_width]
                    size = rect.shape[0] * rect.shape[1]
                    if size == 0: 
                        # print("Me dio tamaño 0")
                        return None
                    if abs(rect.shape[0] - rect.shape[1]) > 2:
                        # print("CHAU porque no es un cuadrado")
                        return None
 
                    
                    black_pixels = np.count_nonzero(rect == 0)
                    if black_pixels == 0: 
                        # print("CHAU porque no hay pixeles blacks")
                        return None
                    
                    black_percentaje = black_pixels / size
                    if black_percentaje < 0.1:
                        # print("CHAU porque hay muy pocos porcentaje de blacks")
                        return None
                    
                    
                    top_square = thresh[y - half_height:y - int(half_height / 3), x - int(half_width / 3):x + int(half_width / 3)]
                    bottom_square = thresh[y + int(half_height / 3):y + half_height, x - int(half_width / 3):x + int(half_width / 3)]
                    top_central = y - int(half_height / 3)
                    bottom_central = y + int(half_height / 3)
                    left_central = x - int(half_width / 3)
                    right_central = x + int(half_width / 3)
                    central_square = thresh[top_central:bottom_central, left_central:right_central]
                    black_pixels_central = np.count_nonzero(central_square == 0)
                    black_pixels_top = np.count_nonzero(top_square == 0)
                    black_pixels_bottom = np.count_nonzero(bottom_square == 0)

                    if black_pixels_bottom <= 3 and black_pixels_top <= 6 and black_pixels_central >= 30: #ACAACA decía 35 lo relajamos
                        self.exit = 'H'
                    elif black_pixels_bottom >= 13 and black_pixels_top >= 13:
                        self.exit = 'S'
                    elif black_pixels_bottom >= 15 and black_pixels_top <= 8: #ACAACA Antes decía 5, lo relajamos
                        self.exit = 'U'
                    elif black_pixels_bottom >= 1 and black_pixels_top >= 1:
                        return self.exit
                    # print("Pixeles")
                    # print(black_pixels_top, black_pixels_central, black_pixels_bottom)
                    # print(self.exit)
                    # # Descomentar para ver si hay falsos positivos
                    # self.debug_show(self.img)
                    # self.debug_show(paraMostrarDespues)
                    # self.debug_show(rect)
            return self.exit
        
    def recognize_clean_sign(self):
        if self.img is None or self.img.size == 0:
            return None
        
        grey = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(grey, 120, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            return None
        
            
        approx = cv2.minAreaRect(contours[0])
        angle = approx[2]
        if abs(angle)%45 == 0:
            height, width = thresh.shape[0], thresh.shape[1]
            M = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
            thresh_rot = cv2.warpAffine(thresh, M, (width, height))
            image_rot = cv2.warpAffine(self.img, M, (width, height))
            contours, _ = cv2.findContours(thresh_rot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) == 0:
                return None
            
            x = int(approx[0][0])
            y = int(approx[0][1])
            half_width = int(approx[1][0] / 2)
            half_height = int(approx[1][1] / 2)

            if y - half_height < 0 or y + half_height > image_rot.shape[0] or x - half_width < 0 or x + half_width > image_rot.shape[1]:
                return None
            rect = image_rot[y - half_height:y + half_height, x - half_width:x + half_width]
            return rect, True
        return None
    
    def return_sign_text(self):
        self.exit = None
        grey = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(grey, 120, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            return None
        
        area=cv2.contourArea(contours[0])
        # print("Area: ", area)
        if area< 100:
            return None
        
        approx = cv2.minAreaRect(contours[0])
        angle = approx[2]
        if abs(angle) == 45:
            height, width = thresh.shape[0], thresh.shape[1]
            M = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
            thresh_rot = cv2.warpAffine(thresh, M, (width, height))
            image_rot = cv2.warpAffine(self.img, M, (width, height))
            contours, _ = cv2.findContours(thresh_rot, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) == 0:
                return None
            
            x = int(approx[0][0])
            y = int(approx[0][1])
            
            if x < 26 or x > 38: return None
            if y < 26 or y > 38: return None

            half_width = int(approx[1][0] / 2)
            half_height = int(approx[1][1] / 2)
            
            if y - half_height < 0 or y + half_height > image_rot.shape[0] or x - half_width < 0 or x + half_width > image_rot.shape[1]:
                return None
            rect = image_rot[y - half_height:y + half_height, x - half_width:x + half_width]
            
            size = rect.shape[0] * rect.shape[1]
            if size == 0: return None
                       
            if abs(rect.shape[0] - rect.shape[1]) > 2:
                #print("CHAU porque no es un cuadrado")
                return None

            yellow, red, black, white = 0, 0, 0, 0
            for x in range(rect.shape[0]):
                for y in range(rect.shape[1]):
                    pixel = rect[x, y]
                    b, g, r = pixel[:3]
                    if b > 200 and g > 200 and r > 200:
                        white += 1
                    elif b <= 1 and g <= 1 and r <= 1:
                        black += 1
                    elif b > 70 and g < 5 and r > 190:
                        red += 1
                    elif b < 10 and g > 190 and r > 195:
                        yellow += 1
            if red > 0 and red > white and red > black and red > yellow and white == 0 and black == 0 and yellow == 0:
                self.exit = 'F'
            elif (white + black) > (yellow + red) and white > black:
                self.exit = 'P'
            elif (white + black) > (yellow + red):
                self.exit = 'C'
            elif red > 0 and yellow > 0 and red > white and red > black and red > yellow and yellow > white and yellow > black:
                self.exit = 'O'
            return self.exit
        
    def procesar(self, converted_img, lastPosition, lastRotation, camera):
        # if converted_img is None or converted_img.size == 0:
        #     return None
        # # si es la misma cámara, se movió y rotó poquito: None!!
        # print(utils.normalizacion_radianes(self.last_token_rotation - lastRotation))
        if camera == self.last_camera and lastPosition.distance_to(self.last_token_position) < 0.015 and utils.normalizacion_radianes(self.last_token_rotation - lastRotation) < math.pi/8:
            # print('no analizo', lastPosition.distance_to(self.last_token_position))
            return None
        # si no, antes de procesar, guardamos la última, cámara, 
        # #posición y rotación, luego procesamos

        self.img = converted_img
        victima = self.devolver_letra_victimas()
        if victima is not None:
            # print('letra', victima, lastPosition)
            self.last_token_position = lastPosition
            self.last_token_rotation = lastRotation
            self.last_camera = camera
            return victima
        else:
            cartel = self.recognize_clean_sign()
            if cartel is not None:
                exit = self.return_sign_text()
                if exit is not None:
                    # print('exit', exit, lastPosition)
                    self.last_token_position = lastPosition
                    self.last_token_rotation = lastRotation
                    self.last_camera = camera
                return exit
        return None
    
    def see_hole(self, img):
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mitad = grey[43:, :]
        size = mitad.shape[0] * mitad.shape[1]
        black_pixels = np.count_nonzero(mitad < 31)
        black_percentaje = black_pixels / size
        black_Hole = False
        if black_percentaje >=0.85 and black_percentaje <= 0.97:
            black_Hole = True
        return black_Hole
