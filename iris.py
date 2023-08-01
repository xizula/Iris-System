import cv2
import numpy as np
import pywt
from patchify import patchify
from scipy.linalg import svd
import pickle
 
part_path = 'ubiris/Sessao_1/'
fte = 0 
class Iris:
    def __init__(self, path):
        self.path = path
        self.probeID = self.path[-5]
        # self.tweak = 
    
    def getID(self):
        if self.path[18] == "/":
            self.id = self.path[16] + self.path[17]
        elif self.path[19] == "/":
            self.id = self.path[16] + self.path[17] + self.path[18]
        else:
            self.id = self.path[16]


    def generateTemplate(self):
        
        try:
            #************ Image preparation **************#
            img = cv2.imread(self.path, 0)
            img = img[100:550, 150:650]

            #************ Gaussian Blur and Edge Map **************#
            img_blur = cv2.GaussianBlur(img, (7,7), 0)
            edge = cv2.Canny(img_blur, 25, 50)

            #************ Finding Pupil **************#
            edge_crop = edge[120:350,100:350] # for better results in finding pupil
            circle1 = cv2.HoughCircles(edge_crop, cv2.HOUGH_GRADIENT, 2, 200,param1=250, param2=20,minRadius=30, maxRadius=60)
            if circle1 is not None:
                    circles = np.uint16(np.around(circle1))
                    for i in circles[0, :]:
                        center1 = (i[0]+100, i[1]+120)
                        radius1 = i[2]

            #************ Finding Iris **************#
            circle2 = cv2.HoughCircles(edge, cv2.HOUGH_GRADIENT, 1, 400,param1=200, param2=18,minRadius=130, maxRadius=200)
            if circle2 is not None:
                    circles = np.uint16(np.around(circle2))
                    for i in circles[0, :]:
                        center2 = (i[0], i[1])
                        radius2 = i[2]
            
            #************ Normalization **************#
            rad2 = radius1 + 140 # Taken distance (140px)
            angle = np.arange(0, 2*np.pi, 2*np.pi/360) 
            # Coordinates of the starting point (pupil center)
            x = center1[0]
            y = center1[1]
            norm = np.zeros((360,100))
            j = 0
            # Iterating every single degree
            for alpha in angle:
                values = []
                # Calculating the beginning and the end point coordinates
                a = int(radius1*np.cos(alpha))
                b = int(radius1*np.sin(alpha))
                c = int(rad2 * np.cos(alpha))
                d = int(rad2 * np.sin(alpha))
                # The beginning
                x1 = x + a
                y1 = y + b
                # The end
                x2 = x + c
                y2 = y + d

                # Bresenham's Algorithm https://eduinf.waw.pl/inf/utils/002_roz/2008_06.php
                # K01-2
                if x1<=x2:
                    kx = 1
                else:
                    kx = -1
                if y1<=y2:
                    ky = 1
                else:
                    ky = -1
                # K03-4
                dx = abs(x2-x1)
                dy = abs(y2-y1)
                # K05
                values.append(img[y1,x1])
                # K06
                if dx < dy:
                    # K16
                    e = dy/2
                    for i in range(dy):
                        y1 += ky
                        e -= dx
                        if e >= 0:
                            # K23
                            values.append(img[y1,x1])
                        else:
                            x1 += kx
                            e += dy
                            values.append(img[y1,x1])
                else:
                    # K07
                    e = dx/2
                    for i in range(dx):
                        x1 += kx
                        e -= dy
                        if e >= 0: # K11
                            # K14
                            values.append(img[y1,x1])
                        else:
                            # K12
                            y1 += ky
                            e += dx
                            values.append(img[y1,x1])       
                norm[j] = np.array(values[:100])
                j += 1
            norm = np.transpose(np.array(norm))

            #************ LL subband **************#
            coeffs = pywt.dwt2(norm, 'haar')
            LL, (LH, HL, HH) = coeffs

            #************ SVD **************#
            patches = patchify(LL,(2,2),step=2)
            smatrix =np.zeros((25,90))
            for i in range(patches.shape[0]):
                for j in range(patches.shape[1]):
                    U,s,VT = svd(patches[i][j])
                    smatrix[i][j]=s[0]
            smatrix = np.array(smatrix)

            #************ Template Generation **************#
            binary = np.zeros((25,90))
            for i in range(25):
                for j in range(90):
                    if j == 89 and i == 24:
                        binary[i][j] = 1
                        continue
                    if j == 89:
                        if smatrix[i][j] >= smatrix[i+1][0]:
                            binary[i][j] = 1
                            continue
                        else:
                            binary[i][j] = 0
                            continue
                    if smatrix[i][j] >= smatrix[i][j+1]:
                        binary[i][j] = 1
                    else:
                        binary[i][j] = 0
            self.template = binary
            self.fail = 'no'
        except:
            print("Fail to enroll")
            self.fail = 'yes'
            global fte
            fte += 1
            print(fte)

    def save(self):
        self.filename = part_path  + str(self.id) + "/" + str(self.probeID) + ".pkl"
        file = open(self.filename, 'wb')
        pickle.dump(self, file)
        file.close()
   
    def generateBloom(self):
        pass
    def generateBiohash(self):
        pass

# test

# path = 'ubiris/Sessao_1/1/Img_1_1_1.jpg'
# heh = Iris(path)
# heh.generateTemplate()
# heh.getID()
# heh.save()
# file = open('ubiris/Sessao_1/1/1.pkl', 'rb')
# xd = pickle.load(file)
# print(xd.filename, xd.id, xd.probeID, xd.template)