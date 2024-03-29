import cv2
import numpy as np
import pywt
from patchify import patchify
from scipy.linalg import svd
import pickle
from ff3 import FF3Cipher
import secrets
import pandas as pd
import csv
from pathlib import Path
 
key = "b09b18e4a298c513ad6236def0f6df7d" # secrets.token_hex(16)
p = 205891132094743
q = 1152921504606847067
M = p * q

class Iris:
    def __init__(self, path):
        self.path = path
        self.probeID = self.path[-5]
        self.id = Path(self.path).parent.name 
    
    def getTweak(self):
        tweaks = pd.read_csv('tweaks.csv')
        if (tweaks['ID'].eq(int(self.id)).any() == True):
            self.tweak = tweaks.set_index('ID').loc[int(self.id), 'tweaks']
        else:
            with open('tweaks.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                self.tweak = str(secrets.token_hex(7))
                writer.writerow([self.id, self.tweak])
       
    def getHashKey(self):
        hk = pd.read_csv('hashkeys.csv')
        if (hk['ID'].eq(int(self.id)).any() == True):
            self.hashkey = hk.set_index('ID').loc[int(self.id), 'hashkey']
        else:
            with open('hashkeys.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                self.hashkey = int(secrets.token_hex(16), 16)
                writer.writerow([self.id, self.hashkey])


    def generateTemplate(self):       
        try:
            #************ Image preparation **************#
            img = cv2.imread(self.path, 0)
            img = img[100:550, 150:650]

            #************ Gaussian Blur and Edge Map **************#
            img_blur = cv2.GaussianBlur(img, (7,7), 0)
            edge = cv2.Canny(img_blur, 25, 50)

            #************ Finding Pupil **************#
            img1 = img.copy()
            edge_crop = edge[120:350,100:350] # for better results in finding pupil
            circle1 = cv2.HoughCircles(edge_crop, method = cv2.HOUGH_GRADIENT, dp = 1, minDist=400,param1=250, param2=3,minRadius=30, maxRadius=60)
            if circle1 is not None:
                    circles = np.uint16(np.around(circle1))
                    for i in circles[0, :]:
                        center1 = (i[0]+100, i[1]+120)
                        radius1 = i[2]
            cv2.circle(img1, center1, radius1, (255, 0, 255), 1)

            #************ Finding Iris **************#
            circle2 = cv2.HoughCircles(edge, method=cv2.HOUGH_GRADIENT, dp=1, minDist=400, param1=200, param2=3,minRadius=130, maxRadius=200)
            if circle2 is not None:
                    circles = np.uint16(np.around(circle2))
                    for i in circles[0, :]:
                        center2 = (i[0], i[1])
                        radius2 = i[2]
            cv2.circle(img1, center2, radius2, (255, 0, 255), 1)
            
            #************ Normalization **************#
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
                a = int(radius1 * np.cos(alpha))
                b = int(radius1 * np.sin(alpha))
                c = int(radius2 * np.cos(alpha))
                d = int(radius2 * np.sin(alpha))
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
                i = np.linspace(0,len(values)-20, 100, dtype=int)
                new_val =[]
                for h in i:
                    new_val.append(values[h])
                norm[j] = np.array(new_val)
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

    def save(self):
        self.filename = 'ubiris/Sessao_1/'  + str(self.id) + "/" + str(self.probeID) + ".pkl"
        file = open(self.filename, 'wb')
        pickle.dump(self, file)
        file.close()

    def show_template(self):
        binary_img= np.zeros((25,90))
        for i in range(25):
            for j in range(90):
                if self.template[i][j] == 0:
                    binary_img[i][j] = 0
                else:
                    binary_img[i][j] = 255
        cv2.namedWindow("Template", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Template", 700, 200)           
        cv2.imshow("Template", binary_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

   
    def generateBloom(self):
        c = FF3Cipher.withCustomAlphabet(key, self.tweak, "01")
        t = np.transpose(self.template)
        fpe = np.zeros(t.shape)
        for i in range(t.shape[0]):
            col = ''
            for j in t[i]:
                col += str(int(j))
            cipher = c.encrypt(col)
            cipher = np.array(list(cipher), dtype=int)
            fpe[i] = cipher
        fpe = np.transpose(fpe)
        # cutting into blocks (5x15)
        h, w = fpe.shape
        blocks = (fpe.reshape(h//5, 5, -1, 15)
                .swapaxes(1,2)
                .reshape(-1, 5, 15))
        bloom_filter = np.zeros((blocks.shape[0], 2**5), dtype=int)
        for i in range(blocks.shape[0]):
            block = np.transpose(blocks[i])
            for row in block:
                row = [int(x) for x in row.tolist()]
                row = ''.join(map(str, row))
                dec = int(row, 2)
                bloom_filter[i][dec] = 1
        self.bloom = bloom_filter

    def generateBiohash(self):
        # Fature vector 
        features = []
        for i in range(25):
            for j in range(90):
                features.append(int(self.template[i][j]))
        n = len(features)
        m = 2000
        # Blum Blum Shub
        bbs = np.zeros((m,n))
        val = int(self.hashkey)
        for i in range(m):
            for j in range(n):              
                val = (val*val) % M
                bit = val & 1
                bbs[i][j] = bit
        bbs = np.array(bbs)
        # Gram-Schmidt
        gs = np.zeros((m,n))
        v1 = bbs[0]
        u1 = v1/np.sqrt(sum(pow(elem,2) for elem in v1))
        gs[0] = u1

        y2 = bbs[1] - (u1.dot(bbs[1])*u1)
        u2 = y2/np.sqrt(sum(pow(elem,2) for elem in y2))
        gs[1] = u2

        for i in range(2, m):
            y = 0
            for j in range(i):
                y += gs[j].dot(bbs[i])*gs[j]
            y = bbs[i] - y
            u = y/np.sqrt(sum(pow(elem,2) for elem in y))
            gs[i] = u
        # Inner product
        inner = []
        for vector in gs:
            inner.append(vector.dot(features))
        # Generating BioHashing Code
        avg = np.mean(inner)
        b = []
        for elem in inner:
            if elem <= avg:
                b.append(0)
            else:
                b.append(1)     
        self.biohash = b


