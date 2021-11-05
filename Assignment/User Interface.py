from PIL import Image
import numpy as np
import itertools
import cv2
from Crypto.Cipher import AES
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox  
from tkinter import filedialog
from tkinter.scrolledtext import *
#import tkinter as tk
import ntpath

class DiscreteCosineTransform:
    #created the constructor
    def __init__(self):
        self.message = None
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

    #main part 
    #encoding function 
    #applying dct for encoding 
    def DCTEncoder(self,img,secret):
        self.message = str(len(secret)).encode()+b'*'+secret
        #get the size of the image in pixels
        row, col = img.shape[:2]
        if((col/8)*(row/8)<len(secret)):
            print("Error: Message too large to encode in image")
            return False
        if row%8 or col%8:
            img = self.addPadd(img,row,col)
        row,col = img.shape[:2]
        #split image into RGB channels
        hImg,sImg,vImg = cv2.split(img)
        #message to be hid in saturation channel so converted to type float32 for dct function
        #print(bImg.shape)
        sImg = np.float32(sImg)
        #breaking the image into 8x8 blocks
        imgBlocks = [np.round(sImg[j:j+8,i:i+8]-128) for (j,i) in itertools.product(range(0,row,8),range(0,col,8))]
        #print('imgBlocks',imgBlocks[0])
        #blocks are run through dct / apply dct to it
        dctBlocks = [np.round(cv2.dct(ib)) for ib in imgBlocks]
        print('imgBlocks', imgBlocks[0])
        print('dctBlocks', dctBlocks[0])
        #blocks are run through quantization table / obtaining quantized dct coefficients
        quantDCT = dctBlocks
        print('quantDCT', quantDCT[0])
        #set LSB in DC value corresponding bit of message
        messIndex=0
        letterIndex=0
        print(self.message)
        for qb in quantDCT:
            #find LSB in DCT cofficient and replace it with message bit
            bit = (self.message[messIndex] >> (7-letterIndex)) & 1
            DC = qb[0][0]
            #print(DC)
            DC = (int(DC) & ~31) | (bit * 15)
            #print(DC)
            qb[0][0] = np.float32(DC)
            letterIndex += 1
            if letterIndex == 8:
                letterIndex = 0
                messIndex += 1
                if messIndex == len(self.message):
                    break
        #writing the stereo image
        #blocks run inversely through quantization table
        #blocks run through inverse DCT
        sImgBlocks = [cv2.idct(B)+128 for B in quantDCT]
        #puts the new image back together
        aImg=[]
        for chunkRowBlocks in self.chunks(sImgBlocks, col/8):
            for rowBlockNum in range(8):
                for block in chunkRowBlocks:
                    aImg.extend(block[rowBlockNum])
        aImg = np.array(aImg).reshape(row, col)
        #converted from type float32
        aImg = np.uint8(aImg)
        #show(sImg)
        Label(hide,text="Message is hidden successfully.", background="#dfdfdf", foreground='green',font=("Bold",10)).pack()
        return cv2.merge((hImg,aImg,vImg))

    #decoding
    #apply dct for decoding 
    def DCTDecoder(self,img):
        row, col = img.shape[:2]
        messSize = None
        messageBits = []
        buff = 0
        #split the image into RGB channels
        hImg,sImg,vImg = cv2.split(img)
        #message hid in saturation channel so converted to type float32 for dct function
        sImg = np.float32(sImg)
        #break into 8x8 blocks
        imgBlocks = [sImg[j:j+8,i:i+8]-128 for (j,i) in itertools.product(range(0,row,8),range(0,col,8))]
        dctBlocks = [np.round(cv2.dct(ib)) for ib in imgBlocks]
        # the blocks are run through quantization table
        print('imgBlocks',imgBlocks[0])
        print('dctBlocks',dctBlocks[0])
        quantDCT = dctBlocks
        i=0
        flag = 0
        #message is extracted from LSB of DCT coefficients
        for qb in quantDCT:
            if qb[0][0] > 0:
                DC = int((qb[0][0]+7)/16) & 1
            else:
                DC = int((qb[0][0]-7)/16) & 1
            #print('qb',qb[0][0],'dc',DC)
            #unpacking of bits of DCT
            buff += DC << (7-i)
            i += 1
            #print(i)
            if i == 8:
                messageBits.append(buff)
                #print(buff,end=' ')
                buff = 0
                i =0
                if messageBits[-1] == 42 and not messSize:
                    try:
                        messSize = chr(messageBits[0])
                        for j in range(1,len(messageBits)-1):
                            messSize += chr(messageBits[j])
                        messSize = int(messSize)
                        print(messSize,'a')
                    except:
                        print('b')
            if len(messageBits) - len(str(messSize)) - 1 == messSize:
                return messageBits
        print("msgbits", messageBits)
        return None
    
class DCTGrayscale:
    #created the constructor
    def __init__(self):
        self.message = None
        self.numBits = 0

    #utility and helper function for DCT Based Steganography
    #helper function to stich the image back together
    def chunks1(self,l,n):
        m = int(n)
        for i in range(0,len(l),m):
            yield l[i:i+m]
    #function to add padding to make the function dividable by 8x8 blocks
    def addPadd1(self,img,row,col):
         img = cv2.resize(img,(col+(8-col%8),row+(8-row%8)))
         return img

    #main part 
    #encoding function 
    #applying dct for encoding 
    def DCTEncoder1(self,img,secret):
        self.message = str(len(secret)).encode()+b'*'+secret
        #get the size of the image in pixels
        row, col = img.shape[:2]
        if((col/8)*(row/8)<len(secret)):
            print("Error: Message too large to encode in image")
            return False
        if row%8 or col%8:
            img = self.addPadd1(img,row,col)
        row,col = img.shape[:2]
        print(row,col)
        #split image into RGB channels
        #hImg,sImg,vImg = cv2.split(img)
        #message to be hid in saturation channel so converted to type float32 for dct function
        #print(bImg.shape)
        img = np.float32(img)
        #breaking the image into 8x8 blocks
        imgBlocks = [np.round(img[j:j+8,i:i+8]-128) for (j,i) in itertools.product(range(0,row,8),range(0,col,8))]
        #print('imgBlocks',imgBlocks[0])
        #blocks are run through dct / apply dct to it
        dctBlocks = [np.round(cv2.dct(ib)) for ib in imgBlocks]
        print('imgBlocks', imgBlocks[0])
        print('dctBlocks', dctBlocks[0])
        #blocks are run through quantization table / obtaining quantized dct coefficients
        quantDCT = dctBlocks
        print('quantDCT', quantDCT[0])
        #set LSB in DC value corresponding bit of message
        messIndex=0
        letterIndex=0
        print(self.message)
        for qb in quantDCT:
            #find LSB in DCT cofficient and replace it with message bit
            bit = (self.message[messIndex] >> (7-letterIndex)) & 1
            DC = qb[0][0]
            #print(DC)
            DC = (int(DC) & ~31) | (bit * 15)
            #print(DC)
            qb[0][0] = np.float32(DC)
            letterIndex += 1
            if letterIndex == 8:
                letterIndex = 0
                messIndex += 1
                if messIndex == len(self.message):
                    break
        #writing the stereo image
        #blocks run inversely through quantization table
        #blocks run through inverse DCT
        sImgBlocks = [cv2.idct(B)+128 for B in quantDCT]
        #puts the new image back together
        aImg=[]
        for chunkRowBlocks in self.chunks1(sImgBlocks, col/8):
            for rowBlockNum in range(8):
                for block in chunkRowBlocks:
                    aImg.extend(block[rowBlockNum])
        aImg = np.array(aImg).reshape(row, col)
        #converted from type float32
        aImg = np.uint8(aImg)
        #show(sImg)
        return aImg

    #decoding
    #apply dct for decoding 
    def DCTDecoder1(self,img):
        row, col = img.shape[:2]
        messSize = None
        messageBits = []
        buff = 0
        #split the image into RGB channels
        #hImg,sImg,vImg = cv2.split(img)
        #message hid in saturation channel so converted to type float32 for dct function
        img = np.float32(img)
        #break into 8x8 blocks
        imgBlocks = [img[j:j+8,i:i+8]-128 for (j,i) in itertools.product(range(0,row,8),range(0,col,8))]
        dctBlocks = [np.round(cv2.dct(ib)) for ib in imgBlocks]
        # the blocks are run through quantization table
        print('imgBlocks',imgBlocks[0])
        print('dctBlocks',dctBlocks[0])
        quantDCT = dctBlocks
        i=0
        flag = 0
        #message is extracted from LSB of DCT coefficients
        for qb in quantDCT:
            if qb[0][0] > 0:
                DC = int((qb[0][0]+7)/16) & 1
            else:
                DC = int((qb[0][0]-7)/16) & 1
            #print('qb',qb[0][0],'dc',DC)
            #unpacking of bits of DCT
            buff += DC << (7-i)
            i += 1
            #print(i)
            if i == 8:
                messageBits.append(buff)
                #print(buff,end=' ')
                buff = 0
                i =0
                if messageBits[-1] == 42 and not messSize:
                    try:
                        messSize = chr(messageBits[0])
                        for j in range(1,len(messageBits)-1):
                            messSize += chr(messageBits[j])
                        messSize = int(messSize)
                        print(messSize,'a')
                    except:
                        print('b')
            if len(messageBits) - len(str(messSize)) - 1 == messSize:
                return messageBits
        print("msgbits", messageBits)
        return None

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

def get_path1(hide_or_extract):
        # Browse button to search for files
        filename = filedialog.askopenfilename(filetypes=(("Template files", "*.png"), ("All files", "*.*") ))
        if hide_or_extract == 0:
            tp1.set(filename)
        else:
            sp1.set(filename)
            
def update1(event):
        retrieved_text = textbox1.get("1.0", END)
        counter1.set('Charcters count: ' + str(len(retrieved_text)) + ' | Max allowed characters = 96')
        
def get_path(hide_or_extract):
        # Browse button to search for files
        filename = filedialog.askopenfilename(filetypes=(("Template files", "*.png"), ("All files", "*.*") ))
        if hide_or_extract == 0:
            tp.set(filename)
        else:
            sp.set(filename)
            
def update(event):
        retrieved_text = textbox.get("1.0", END)
        counter.set('Charcters count: ' + str(len(retrieved_text)) + ' | Max allowed characters = 96')
        
        
def hidetext1():
    message = textbox1.get("1.0", END) 
    image = ip1.get()
    print(image)
    print(message)
    if(len(message) > 96):
        messagebox.showwarning("The message is too long. Shorten the message.")
    else:
        img = cv2.imread(image,cv2.IMREAD_UNCHANGED)
        key = b'Sixteen byte key'
        cipher = AES.new(key,AES.MODE_ECB)
        enc_msg = msg_encrypt(message,cipher)
        d = DCTGrayscale() 
        dct_img_encoded = d.DCTEncoder1(img, enc_msg) 
        path = ntpath.split(image)[0] + "/enc_" + ntpath.basename(image)[:-4]+".png"
        cv2.imwrite(path,dct_img_encoded)

def hide1():
    global hide1
    global tp1
    global ip1
    global textvar1
    global counter1
    global char_count1
    global textbox1
    hide1 = Toplevel(hm)
    hide1.title("hide")
    hide1.geometry("1200x700")
    hide1.configure(bg='#dfdfdf')
    #Label(hide, text="", bg ='#dfdfdf').pack()
    Label(hide1, text='                                                        Hide Message                                                         ', fg='white', font=("Bold", 36),bg ='#6a057e').pack()
    Label(hide1, text='', bg ='#dfdfdf').pack()
    Label(hide1, bg='#dfdfdf', fg='black',font=("Bold", 16), text="Choose The Image (Image Should Be In JPG and PNG Format):").pack()
    Label(hide1, text='', bg ='#dfdfdf').pack()
    tp1 = StringVar()
    ip1 = Entry(hide1, width=55, textvariable=tp1)
    ip1.pack()
    Label(hide1, text='', bg ='#dfdfdf').pack()
    Button(hide1, text="Select target image", bg='#6a057e', fg='white',font=("Bold", 10),command=lambda: get_path1(0)).pack()
    Label(hide1, text='', bg ='#dfdfdf').pack()
    #print(str(tp))
    #print(ip)
    #button2.configure(bg="black", fg='white', activebackground='#0080ff', activeforeground='white')
    Label(hide1, text=" Enter The Text to hide: ",  background="#dfdfdf", foreground='black',font=("Bold", 16)).pack()
    Label(hide1, text='', bg ='#dfdfdf').pack()
    textvar1 = StringVar()
    textbox1 = Text(hide1, height=5, width=70,  wrap='word', undo=True)
    textbox1.pack()
    textbox1.bind("<Key>", update1)
    Label(hide1, text='', bg ='#dfdfdf').pack()
    counter1 = StringVar()
    counter1.set('Charcters count: ' +'0'+ ' | Max allowed characters = 96')
    char_count1 = Label(hide1, textvariable=counter1, bg="#dfdfdf", fg= '#0080ff').pack()
    Label(hide1, text='', bg ='#dfdfdf').pack()
    Button(hide1, text="Hide Text",bg='#6a057e', fg='white',font=("Bold", 10),command=lambda: hidetext1()).pack()

def showtext1():
    #message = textbox.get("1.0", END) 
    image = imp1.get()
    print(image)
    #print(message)
    img = cv2.imread(image,cv2.IMREAD_UNCHANGED)
    key = b'Sixteen byte key'
    cipher = AES.new(key,AES.MODE_ECB)
    #enc_msg = msg_encrypt(message,cipher)
    d = DCTGrayscale() 
    msg = d.DCTDecoder1(img) 
    #Exception Handling need to be done in decoding phase using tkinter messagebox or labels
    try:
        a = msg.index(42)
        decoded = bytes(msg[a+1:])
        text = msg_decrypt(decoded,cipher)
        extmsg1.set(text)
    except UnicodeDecodeError:
        extmsg1.set('\nError 1: Falied To Decode The Message.\n')
    except AttributeError:
        extmsg1.set('\nError 2: Failed To Extract The Message.\n')
    except ValueError:
        extmsg1.set('\nError 3: Failed To Extract The Message.\n')
    except:
        extmsg1.set('\nError 4: Unexpected Error\n')

def show1():
    pass
    global show1
    global imp1
    global sp1
    global u1
    global extmsg1
    global exm1
    show1 = Toplevel(sm)
    show1.title("Show")
    show1.geometry("1200x800")
    show1.configure(bg='#dfdfdf')
    #Label(hide, text="", bg ='#dfdfdf').pack()
    Label(show1, text='                                                        Show Message                                                         ', fg='white', font=("Bold", 36),bg ='#6a057e').pack()
    Label(show1, text='', bg ='#dfdfdf').pack()
    Label(show1, bg='#dfdfdf', fg='black',font=("Bold", 16), text="Choose The Image (Image Should Be In PNG Format Only):").pack()
    Label(show1, text='', bg ='#dfdfdf').pack()
    sp1 = StringVar()
    imp1 = Entry(show1, width=55, textvariable=sp1)
    imp1.pack()
    Label(show1, text='', bg ='#dfdfdf').pack()
    Button(show1, text="Select target image", bg='#6a057e', fg='white',font=("Bold", 10),command=lambda: get_path1(1)).pack()
    Label(show1, text='', bg ='#dfdfdf').pack()
    u1 = LabelFrame(show1, bg='white', fg='#6a057e', text=" Extracted text ",font=("Bold", 14))
    u1.pack(expand=1, fill="both",padx=5, pady=5)
    extmsg1 = StringVar()
    extmsg1.set('\nExtracted Text\n')
    exm1 = Label(u1, textvariable=extmsg1, background='white', foreground="black",font=("Bold", 12))
    exm1.pack(expand=1, fill="both", padx=5, pady=5)
    Label(show1, text='', bg ='#dfdfdf').pack()
    Button(show1,text="Extract Text",bg='#6a057e', fg='white',font=("Bold", 10),command=lambda: showtext1()).pack()
    #mainloop()


def hidetext():
    message = textbox.get("1.0", END) 
    image = ip.get()
    print(image)
    print(message)
    if(len(message) > 96):
        messagebox.showwarning("The message is too long. Shorten the message.")
    else:
        img = cv2.imread(image,cv2.IMREAD_UNCHANGED)
        key = b'Sixteen byte key'
        cipher = AES.new(key,AES.MODE_ECB)
        enc_msg = msg_encrypt(message,cipher)
        d = DiscreteCosineTransform() 
        dct_img_encoded = d.DCTEncoder(img, enc_msg) 
        path = ntpath.split(image)[0] + "/enc_" + ntpath.basename(image)[:-4]+".png"
        cv2.imwrite(path,dct_img_encoded)
        
def hide_menu():
    global hm
    hm = Toplevel(main_win)
    hm.title("Hide Menu")
    hm.geometry("400x200")
    hm.configure(bg='#dfdfdf')
    Label(hm, text='                                Choose The Image Type                                 ', fg='white', font=("Bold", 24),bg ='#6a057e').pack()
    Label(hm, text='', bg ='#dfdfdf').pack()
    Button(hm, text="GrayScale - 8 Bit Depth", width=30, height=1, fg='white', bg="#6a057e", font=("Bold", 12),command=hide1).pack()
    Label(hm, text='', bg ='#dfdfdf').pack()
    Button(hm, text="RGB - 24 Bit Depth", width=30, height=1, fg='white', bg="#6a057e", font=("Bold", 12),command=hide).pack()

def hide():
    global hide
    global tp
    global ip
    global textvar
    global counter
    global char_count
    global textbox
    hide = Toplevel(hm)
    hide.title("hide")
    hide.geometry("1200x700")
    hide.configure(bg='#dfdfdf')
    #Label(hide, text="", bg ='#dfdfdf').pack()
    Label(hide, text='                                                        Hide Message                                                         ', fg='white', font=("Bold", 36),bg ='#6a057e').pack()
    Label(hide, text='', bg ='#dfdfdf').pack()
    Label(hide, bg='#dfdfdf', fg='black',font=("Bold", 16), text="Choose The Image (Image Should Be In JPG and PNG Format):").pack()
    Label(hide, text='', bg ='#dfdfdf').pack()
    tp = StringVar()
    ip = Entry(hide, width=55, textvariable=tp)
    ip.pack()
    Label(hide, text='', bg ='#dfdfdf').pack()
    Button(hide, text="Select target image", bg='#6a057e', fg='white',font=("Bold", 10),command=lambda: get_path(0)).pack()
    Label(hide, text='', bg ='#dfdfdf').pack()
    #print(str(tp))
    #print(ip)
    #button2.configure(bg="black", fg='white', activebackground='#0080ff', activeforeground='white')
    Label(hide, text=" Enter The Text to hide: ",  background="#dfdfdf", foreground='black',font=("Bold", 16)).pack()
    Label(hide, text='', bg ='#dfdfdf').pack()
    textvar = StringVar()
    textbox = Text(hide, height=5, width=70,  wrap='word', undo=True)
    textbox.pack()
    textbox.bind("<Key>", update)
    Label(hide, text='', bg ='#dfdfdf').pack()
    counter = StringVar()
    counter.set('Charcters count: ' +'0'+ ' | Max allowed characters = 96')
    char_count = Label(hide, textvariable=counter, bg="#dfdfdf", fg= '#0080ff').pack()
    Label(hide, text='', bg ='#dfdfdf').pack()
    Button(hide, text="Hide Text",bg='#6a057e', fg='white',font=("Bold", 10),command=lambda: hidetext()).pack()#command=lambda: self.hidetext())
    #button21.pack(side=tk.RIGHT, padx=5, pady=5)
    #button21.configure(bg="black", fg='white', activebackground='#0080ff', activeforeground='white')
    #mainloop()

def showtext():
    #message = textbox.get("1.0", END) 
    image = imp.get()
    print(image)
    #print(message)
    img = cv2.imread(image,cv2.IMREAD_UNCHANGED)
    key = b'Sixteen byte key'
    cipher = AES.new(key,AES.MODE_ECB)
    #enc_msg = msg_encrypt(message,cipher)
    d = DiscreteCosineTransform() 
    msg = d.DCTDecoder(img) 
    #Exception Handling need to be done in decoding phase using tkinter messagebox or labels
    try:
        a = msg.index(42)
        decoded = bytes(msg[a+1:])
        text = msg_decrypt(decoded,cipher)
        extmsg.set(text)
    except UnicodeDecodeError:
        extmsg.set('\nError 1: Falied To Decode The Message.\n')
    except AttributeError:
        extmsg.set('\nError 2: Failed To Extract The Message.\n')
    except ValueError:
        extmsg.set('\nError 3: Failed To Extract The Message.\n')
    except:
        extmsg.set('\nError 4: Unexpected Error\n')
    #path = ntpath.split(image)[0] + "/enc_" + ntpath.basename(image)[:-4]+".png"
    #cv2.imwrite(path,dct_img_encoded)
    
def show_menu():
    global sm
    sm= Toplevel(main_win)
    sm.title("Show Menu")
    sm.geometry("400x200")
    sm.configure(bg='#dfdfdf')
    Label(sm, text='                                Choose The Image Type                                 ', fg='white', font=("Bold", 24),bg ='#6a057e').pack()
    Label(sm, text='', bg ='#dfdfdf').pack()
    Button(sm, text="GrayScale - 8 Bit Depth", width=30, height=1, fg='white', bg="#6a057e", font=("Bold", 12),command=show1).pack()
    Label(sm, text='', bg ='#dfdfdf').pack()
    Button(sm, text="RGB - 24 Bit Depth", width=30, height=1, fg='white', bg="#6a057e", font=("Bold", 12),command=show).pack()
    
def show():
    pass
    global show
    global imp
    global sp
    global u
    global extmsg
    global exm
    show = Toplevel(sm)
    show.title("Show")
    show.geometry("1200x800")
    show.configure(bg='#dfdfdf')
    #Label(hide, text="", bg ='#dfdfdf').pack()
    Label(show, text='                                                        Show Message                                                         ', fg='white', font=("Bold", 36),bg ='#6a057e').pack()
    Label(show, text='', bg ='#dfdfdf').pack()
    Label(show, bg='#dfdfdf', fg='black',font=("Bold", 16), text="Choose The Image (Image Should Be In PNG Format Only):").pack()
    Label(show, text='', bg ='#dfdfdf').pack()
    sp = StringVar()
    imp = Entry(show, width=55, textvariable=sp)
    imp.pack()
    Label(show, text='', bg ='#dfdfdf').pack()
    Button(show, text="Select target image", bg='#6a057e', fg='white',font=("Bold", 10),command=lambda: get_path(1)).pack()
    Label(show, text='', bg ='#dfdfdf').pack()
    u = LabelFrame(show, bg='white', fg='#6a057e', text=" Extracted text ",font=("Bold", 14))
    u.pack(expand=1, fill="both",padx=5, pady=5)
    extmsg = StringVar()
    extmsg.set('\nExtracted Text\n')
    exm = Label(u, textvariable=extmsg, background='white', foreground="black",font=("Bold", 12))
    exm.pack(expand=1, fill="both", padx=5, pady=5)
    Label(show, text='', bg ='#dfdfdf').pack()
    Button(show,text="Extract Text",bg='#6a057e', fg='white',font=("Bold", 10),command=lambda: showtext()).pack()
    #mainloop()

def main_win():
    global main_win
    main_win = Tk()
    main_win.title("Image Steganography")
    main_win.geometry("626x417")
    bg = PhotoImage(file = "C:/Users/hp/Desktop/IS.png")
    canvas1 = Canvas( main_win, width = 626,height = 417)
    canvas1.pack(fill = "both", expand = True)
    canvas1.create_image( 0, 0, image = bg, anchor = NW)
    b1 = Button(main_win, text="Hide Message", font=("Bold", 16), fg='black',bg='white', command = hide_menu)
    b2 = Button(main_win, text="Show Message", font=("Bold", 16), fg='black', bg='white',command = show_menu)
    button1_canvas = canvas1.create_window( 235,  175, anchor = "nw", window = b1)
    button2_canvas = canvas1.create_window( 230, 275,anchor = "nw", window = b2)
    mainloop()

main_win()
