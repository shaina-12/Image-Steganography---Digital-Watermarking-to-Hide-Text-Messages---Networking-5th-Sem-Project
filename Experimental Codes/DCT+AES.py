# -*- coding: utf-8 -*-
"""
Created on Tue Oct 19 11:13:50 2021

@author: hp
"""

from PIL import Image
import numpy as np
import itertools
import types
import cv2
from Crypto.Cipher import AES
#creation of quantization matrix of quality factor as 50
quant = np.array([[16,11,10,16,24,40,51,61],
                    [12,12,14,19,26,58,60,55],
                    [14,13,16,24,40,57,69,56],
                    [14,17,22,29,51,87,80,62],
                    [18,22,37,56,68,109,103,77],
                    [24,35,55,64,81,104,113,92],
                    [49,64,78,87,103,121,120,101],
                    [72,92,95,98,112,100,103,99]])
class DiscreteCosineTransform:
    #created the constructor
    def __init__(self):
        self.message = None
        self.bitMessage = None
        self.oriCol = 0
        self.oriRow = 0
        self.numBits = 0
    #utility and helper function for DCT Based Steganography
    #helper function to stich the image back together
    def chunks(self,l,n):
        m = int(n)
        for i in range(0,len(l),m):
            yield l[i:i+m]
    #function to add padding to make the function dividable by 8x8 blocks
    def addPadd(self,img,row,col):
        img = cv2.resize(img,(col+(8-col%8),row+(8-row%8)))
        return img
    #function to transform the message that is wanted to be hidden from plaintext to a list of bits
    def toBits(self):
        bits = []
        for char in self.message:
            binval = bin(char)[2:].rjust(8,'0')
            #print('bin '+binval)
            bits.append(binval)
        self.numBits = bin(len(bits))[2:].rjust(8,'0')
        return bits
    #main part 
    #encoding function 
    #applying dct for encoding 
    def DCTEncoder(self,img,secret):
        self.message = str(len(secret)).encode()+b'*'+secret
        self.bitMessage = self.toBits()
        #get the size of the image in pixels
        row, col = img.shape[:2]
        self.oriRow = row
        self.oriCol = col
        if((col/8)*(row/8)<len(secret)):
            print("Error: Message too large to encode in image")
            return False
        if(row%8!=0 or col%8!=0):
            img = self.addPadd(img,row,col)
        row,col = img.shape[:2]
        #split image into RGB channels
        bImg,gImg,rImg = cv2.split(img)
        #message to be hid in blue channel so converted to type float32 for dct function
        #print(bImg.shape)
        bImg = np.float32(bImg)
        #breaking the image into 8x8 blocks
        imgBlocks = [np.round(bImg[j:j+8,i:i+8]-128) for (j,i) in itertools.product(range(0,row,8),range(0,col,8))]
        #print(imgBlocks[0])
        #blocks are run through dct / apply dct to it
        dctBlocks = [np.round(cv2.dct(ib)) for ib in imgBlocks]
        #print('DCT Blocks')
        #print(dctBlocks[0])
        #blocks are run through quantization table / obtaining quantized dct coefficients
        quantDCT = [np.round(dbk/quant) for dbk in dctBlocks]
        #print('Quant Blocks')
        #print(quantDCT[0])
        #set LSB in DC value corresponding bit of message
        messIndex=0
        letterIndex=0
        print(self.bitMessage)
        for qb in quantDCT:
            #find LSB in DCT cofficient and replace it with message bit
            #print(len(qb))
            DC = qb[0][0]
            #print(DC.shape)
            DC = np.uint8(DC)
            #print(DC)
            DC = np.unpackbits(DC)
            #print(DC[0])
            #print(self.bitMessage[messIndex][letterIndex])
            #print(DC[7])
            #print(type(DC[7]))
            #print(DC[7].shape)
            #print(type(self.bitMessage))
            #a=self.bitMessage[messIndex][letterIndex]
            #print(a)
            DC[7] = self.bitMessage[messIndex][letterIndex]
            DC = np.packbits(DC)
            DC = np.float32(DC)
            DC = DC - 255
            qb[0][0] = DC
            letterIndex = letterIndex + 1
            if (letterIndex == 8):
                letterIndex = 0
                messIndex = messIndex + 1
                if (messIndex == len(self.message)):
                    break
        #writing the stereo image
        #blocks run inversely through quantization table
        sImgBlocks = [quantizedBlock *quant+128 for quantizedBlock in quantDCT]
        #blocks run through inverse DCT
        #sImgBlocks = [cv2.idct(B)+128 for B in quantizedDCT]
        #puts the new image back together
        sImg=[]
        for chunkRowBlocks in self.chunks(sImgBlocks, col/8):
            for rowBlockNum in range(8):
                for block in chunkRowBlocks:
                    sImg.extend(block[rowBlockNum])
        print(len(sImg))
        sImg = np.array(sImg).reshape(row, col)
        #converted from type float32
        sImg = np.uint8(sImg)
        #show(sImg)
        sImg = cv2.merge((sImg,gImg,rImg))
        return sImg
    #decoding
    #apply dct for decoding 
    def DCTDecoder(self,img):
        row, col = img.shape[:2]
        messSize = None
        messageBits = []
        buff = 0
        #split the image into RGB channels
        bImg,gImg,rImg = cv2.split(img)
        #message hid in blue channel so converted to type float32 for dct fuction
        bImg = np.float32(bImg)
        #break into 8x8 blocks
        imgBlocks = [bImg[j:j+8,i:i+8]-128 for (j,i) in itertools.product(range(0,row,8),range(0,col,8))]
        #dctBlocks = [np.round(cv2.dct(ib)) for ib in imgBlocks]
        # the blocks are run through quantization table
        quantDCT = [ib/quant for ib in imgBlocks]
        i=0
        flag = 0
        nb = ''
        #message is extracted from LSB of DCT coefficients
        for qb in quantDCT:
            DC = qb[0][0]
            DC = np.uint8(DC)
            #unpacking of bits of DCT
            DC = np.unpackbits(DC)
            if (flag == 0):
                if (DC[7] == 1):
                    buff+=(0 & 1) << (7-i)
                elif (DC[7] == 0):
                    buff+=(1&1) << (7-i)
            else:
                if (DC[7] == 1):
                    nb+='0'
                elif (DC[7] == 0):
                    nb+='1'
            i=1+i
            #print(i)
            if (i == 8):
                #print(buff,end=' ')
                if (flag == 0):
                    messageBits.append(buff)
                    #print(buff,end=' ')
                    buff = 0
                else:
                    messageBits.append(nb)
                    #print(nb,end=' ')
                    nb = ''
                i =0
                if (messageBits[-1] == 42 and messSize is None):
                    try:
                        flag = 1
                        messSize = int(str(chr(messageBits[0]))+str(chr(messageBits[1])))#int(''.join(messageBits[:-1]))
                        print(type(messSize),'a')
                    except:
                        print('b')
                        pass
            if (len(messageBits) - len(str(messSize)) - 1 == messSize):
                #print(''.join(messageBits)[len(str(messSize))+1:])
                return messageBits
                pass
        #print(messageBits)
        #blocks run inversely throught quantization table
        sImgBlocks = [qb * quant+128 for qb in quantDCT]
        #blocks run through inverse DCT
        sImg=[]
        for chunkRowBlocks in self.chunks(sImgBlocks, col/8):
            for rowBlockNum in range(8):
                for block in chunkRowBlocks:
                    sImg.extend(block[rowBlockNum])
        sImg = np.array(sImg).reshape(row, col)
        #converted from type float32
        sImg = np.uint8(sImg)
        sImg = cv2.merge((sImg,gImg,rImg))
        ##sImg.save(img)
        #dct_decoded_image_file = "dct_" + original_image_file
        #cv2.imwrite(dct_decoded_image_file,sImg)
        return ''
def msg_encrypt(msg,cipher):
    if (len(msg)%16 != 0):
        #a = len(msg)%16 != 0 
        #print(a)
        msg = msg + ' '*(16 - len(msg)%16)
    #nonce = cipher.nonce
    t1 = msg.encode()
    enc_msg = cipher.encrypt(t1)
    return enc_msg
def msg_decrypt(ctext,cipher):
    dec_msg = cipher.decrypt(ctext)
    msg1 = dec_msg.decode()
    return msg1
image = cv2.imread('C://Users//hp//Desktop//Lenna.jpg',cv2.IMREAD_UNCHANGED)
secret_msg = 'Shaina'
key = b'Sixteen byte key'
#encryption of message
cipher = AES.new(key,AES.MODE_ECB)
enc_msg = msg_encrypt(secret_msg,cipher)
print(enc_msg)
d = DiscreteCosineTransform()
"""sm = str(enc_msg)
sm = sm[1:]
print('sm',sm)"""
dct_img_encoded = d.DCTEncoder(image, enc_msg)
cv2.imwrite('C://Users//hp//Desktop//DCT.png',dct_img_encoded)
eimg = cv2.imread('C://Users//hp//Desktop//DCT.png',cv2.IMREAD_UNCHANGED)

text = d.DCTDecoder(eimg)
ntext = []
print(text)
for i in range(len(text)):
    if(type(text[i]) == str):
        ntext.append(text[i])
print(ntext)
#print(type(text))
#print(ntext)
#binary_data = ''.join([ format(ord(i), "08b") for i in ntext ])
#all_bytes = [ binary_data[i: i+8] for i in range(0,len(binary_data),8)]
decoded_data = b''
for byte in ntext:
    try:
        decoded_data += int (byte,2).to_bytes (len(byte) // 8, byteorder='big')
        '''
        if (decoded_data[-5:] == b'#####'): #check if we have reached the delimeter which is '#####'
            break'''
    except Exception as e:
        print(byte)
        break
print(decoded_data)
'''
for i in range(len(decoded_data)):
    print(decoded_data[i])
'''
#decryption of message

dtext = msg_decrypt(decoded_data,cipher)
print(dtext)
