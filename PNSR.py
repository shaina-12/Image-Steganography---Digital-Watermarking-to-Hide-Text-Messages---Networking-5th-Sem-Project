# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 01:28:11 2021

@author: hp
"""
import math
import numpy as np
import signal
import cv2
class Compare():
    def correlation(self, img1, img2):
        return signal.correlate2d (img1, img2)
    def meanSquareError(self, img1, img2):
        error = np.sum((img1.astype('float') - img2.astype('float')) ** 2)
        error /= float(img1.shape[0] * img1.shape[1]);
        return error
    def psnr(self, img1, img2):
        mse = self.meanSquareError(img1,img2)
        if mse == 0:
            return 100
        PIXEL_MAX = 255.0
        return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))
    def addPadd(self,img,row,col):
         img = cv2.resize(img,(col+(8-col%8),row+(8-row%8)))
         return img
a = Compare()
img = cv2.imread('C://Users//hp//Desktop//Test RGB Images//Png Images//Original//Mountain1.png')
row, col = img.shape[:2]
img = a.addPadd(img,row,col)
simg = cv2.imread('C://Users//hp//Desktop//Test RGB Images//Png Images//Original//RMountain1.png')
b = a.psnr(img,simg)
print(b)
