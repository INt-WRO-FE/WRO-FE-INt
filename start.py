from threading import Thread
import serial
from time import sleep, time
import cv2
import numpy as np

cam = cv2.VideoCapture(0)

mServo = 90
direction = "U"
mDC = 0
Sonar1 = 0
Sonar2 = 0
Sonar3 = 0
Sonar4 = 0

centGreen = 'None'
centRed = 'None'
y_green = 0
y_red = 0

def Sonars():
    global Sonar1, Sonar2, Sonar3, Sonar4, mServo
    serSonar = serial.Serial('/dev/ttyUSB0', 9600)
    serSonar.flush()
    message = ""
    while True:
        try:
            simbol = serSonar.read().decode('utf-8')
            if simbol != "\n":
                message += simbol
            else:
                valueSensor = message.split(";")
                Sonar1 = int(valueSensor[0][1:len(valueSensor[0])])
                Sonar2 = int(valueSensor[1][1:len(valueSensor[1])])
                Sonar3 = int(valueSensor[2][1:len(valueSensor[2])])
                Sonar4 = int(valueSensor[3][1:len(valueSensor[3])])
                if Sonar1 == 0:
                    Sonar1 = 200
                if Sonar2 == 0:
                    Sonar2 = 200
                if Sonar3 == 0:
                    Sonar3 = 200
                if Sonar4 == 0:
                    Sonar4 = 200
                print(Sonar1, Sonar2, Sonar3, Sonar4)
                message = ""
                sleep(0.02 - time() % 0.02)
        except UnicodeDecodeError:
            message = ''
            serSonar.flush()
            continue
        
def MotorSender():
    global mServo, direction, mDC
    ser = serial.Serial('/dev/ttyUSB1', 9600)
    ser.flush()
    while True:
        
        if int(mServo) < 20:
            mServo = 20
        elif int(mServo) > 160:
            mServo = 160
        #print(int(mServo))
        message1 = "S" + str(int(mServo)) + ";"  
        message2 = "M" + str(direction) + str(mDC) + ";"
      
        ser.write(message1.encode('utf-8'))
        ser.write(message2.encode('utf-8'))
        
        sleep(0.02 - time() % 0.02)


def camera():
    global  centGreen, centRed, y_green, y_red, cent
    #cam.set(cv2.CAP_PROP_EXPOSURE, 1000) #выдержка? не работает
    cam.set(cv2.CAP_PROP_BRIGHTNESS,150) #яркость
    #cam.set(cv2.CAP_PROP_CONTRAST, 500)
    tempRed = []
    tempGreen = []
    while True:
        ret, img = cam.read()
        img_hsv=cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        #----красный
        lower_red = np.array([0,100,20]) #нижняя позиция красного
        upper_red = np.array([8,255,255]) #верхняя позиция красного
        mask0 = cv2.inRange(img_hsv, lower_red, upper_red) #маска нижнего красного

        lower_red = np.array([170,80,10]) #н.п. красного
        upper_red = np.array([180,255,255]) #в.п. красного
        mask1 = cv2.inRange(img_hsv, lower_red, upper_red) #маска в.к.
     
        mask_red = mask0+mask1

        contours, hier  = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key =lambda x:cv2.contourArea(x), reverse = True)

        #-----зеленый
        lower_green = np.array([40,40,80]) 
        upper_green = np.array([70,255,255])
        mask_green = cv2.inRange(img_hsv, lower_green, upper_green)

        contours2, hier2  = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours2 = sorted(contours2, key =lambda x:cv2.contourArea(x), reverse = True)

        for cnt_red in contours:
            area_red = cv2.contourArea(cnt_red)
            if area_red > 5000:
                (x,y,w,h) = cv2.boundingRect(cnt_red)
                cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                centRed = int(x+(w/2))
                cv2.circle(img, (centRed,y), 8, (87,255,255), -1)
                y_red = (y+h)/2
            else:
                break
                                 
        for cnt_green in contours2:
            area_green = cv2.contourArea(cnt_green)

            if area_green > 5000:
                (x,y,w,h) = cv2.boundingRect(cnt_green)
                cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                centGreen = int(x+(w/2))
                cv2.circle(img, (centGreen,y), 8, (87,255,255), -1)
                y_green = (y+h)/2
            else:
                break
        if centRed != 'None':
            if len(tempRed) < 10:
                tempRed.append(centRed)
            else:
                summ = 0
                for i in tempRed:
                    summ = summ + i
                if summ / 10 == tempRed[0]:
                    centRed = 'None'
                    y_red = 0
                tempRed = []
                
        if centGreen != 'None':
            if len(tempGreen) < 10:
                tempGreen.append(centGreen)
            else:
                summ = 0
                for i in tempGreen:
                    summ = summ + i
                if summ / 10 == tempGreen[0]:
                    centGreen = 'None'
                    y_green = 0
                tempGreen = []

            
        #cv2.imshow('1',img)
        #cv2.imshow('2',mask_red)
        #cv2.imshow('3',mask_green)
        
        ch = cv2.waitKey(5)
        if ch == 27:
            break




def DegreeServo():
    global mServo, direction, mDC, Sonar1, Sonar2, Sonar3, Sonar4, centGreen, centRed,y_red, y_green
    Kp14 = 0.5
    Kp23 = 1
    while True:
        if Sensor1  < 30 or Sensor4 < 30 :
            if Sensor1 < 30:
                mServo = 160
            elif Sensor4 < 30:
                mServo = 20
        elif centGreen == 'None' and centRed == 'None'  
            mServo = 90 - (Sonar1 - Sonar4) * Kp14 - (Sonar2 - Sonar3) * Kp23 
        else:
            if centGreen != 'None' and centRed != 'None':
                #по игрикам
                if y_red > y_green:
                    otklon = (640 - centRed)
                    nOtklon = (otklon - 0) * ((90 - 0) / (640 - 0))
                    mServo = 90 - nOtklon * 2
                else:
                    otklon = (0 - centGreen)
                    nOtklon = (otklon - 0) * ((90 - 0) / (0 + 640))
                    mServo = 90 - nOtklon * 2
            elif centGreen != 'None':
                #по зеленому
                otklon = (0 - centGreen)
                nOtklon = (otklon - 0) * ((90 - 0) / (0 + 640))
                mServo = 90 - nOtklon * 2
            elif centRed != 'None':
                #по красному
                otklon = (640 - centRed)
                nOtklon = (otklon - 0) * ((90 - 0) / (640 - 0))
                mServo = 90 - nOtklon * 2
        #print(mServo)
        sleep(0.02 - time() % 0.02)


if __name__ == "__main__":
    ThreadMotors = Thread(target = MotorSender)
    ThreadCamera = Thread(target = camera)
    ThreadSonars = Thread(target = Sonars)
    ThreadServo = Thread(target = DegreeServo)
    
    ThreadMotors.start()
    ThreadCamera.start()
    ThreadSonars.start()
    ThreadServo.start()
    
    ThreadMotors.join()
    ThreadCamera.join()
    ThreadSonars.join()
    ThreadServo.join()
    
