import mss
import os, sys
from screeninfo import get_monitors
import time
import cv2
import numpy as np
import pygame
import tkinter as tk
import pygetwindow as gw
#import pyautogui
#from pynput import keyboard, Controller
#import psutil

for m in get_monitors(): # loops for every monitor to find their data.
    print(f'Monitor Width is {m.width}, Length is {m.height}') #m.width finds the width of the monitor specifically.

definedIcons = ["precision", "redbloom"]

imgInfo = {
    "precision": {
        "width": 38,
        "backgroundTransparency": False,
        "backgroundColour": [180, 78, 143], #RGB = 143, 78, 180, HSV = 278, 57, 71, BGR = 180, 78, 143
        "foregroundColour": [27, 27, 30], #RGB = 30, 27, 27, HSV = 0, 10, 88, BGR = 27, 27, 30
        "tolerance": 10,
        "imageComparePath" : "comparison/precision.png",
        "timeRemaining": 0,
        "refresh": 60,
        "announceTime": 15,
        "announceDirectory": "announce/precision.wav",
    },
    "redbloom": {
        "width": 1,
        "backgroundTransparency": True,
        "backgroundColourDifference": 31.5,
        "backgroundColourAverage": [112.5, 112.5, 189.5], #RGB = 190, 112.5, 112.5, HSV = 0, 41, 75, BGR = 112.5, 112.5, 190
        "backgroundColourUpper": [154, 154, 221], #RGB = 221, 154, 154, HSV = 0, 30, 87, BGR = 154, 154, 221
        "backgroundColourLower": [91, 91, 158], #RGB = 158, 91, 91, HSV = 0, 42, 62, BGR = 91, 91, 158
        "foregroundPixelx": 19,
        "foregroundPixely": 10, # 44  43 243, 47  47 243, 44  43 243, 41  40 229
        "foregroundColour": [41, 40,229], #RGB = 236, 41, 42, HSV = 0, 82, 92, BGR = 42, 41, 236
        "tolerance": 15,
        "imageComparePath" : "comparison/redbloom.png",
        "foregroundColourTolerance": 10, #This is the tolerance for the foreground colour.
        "timeRemaining": 0,
        "refresh": 8, #In game time for how long the buff lasts. This is in seeconds.
        "announceTime": 4, #The time at which the audio will play to announce that the buff is about to run out. This is in seconds.
        "announceDirectory": "announce/blooms.wav",
    }
}


root = tk.Tk()
root.title("Buff Tracker")
root.geometry("200x100")
root.attributes("-topmost", True) #Keeps the window on top of all other windows

root.resizable(False, False) #Prevents the window from being resized

label = tk.Label(root, text="Buff Tracker is running...", font=("Consolas", 18))
label.pack()

def resourcePath(relative_path):
    base = getattr(sys, '_MEIPASS', os.getcwd())
    return os.path.join(base, relative_path)


#Audio Setup
pygame.init()
pygame.mixer.init()

soundprecision = pygame.mixer.Sound(resourcePath(imgInfo["precision"]["announceDirectory"]))
soundredbloom = pygame.mixer.Sound(resourcePath(imgInfo["redbloom"]["announceDirectory"]))

precisionChannel = None
redBloomChannel = None

updatedTimer = {icon: imgInfo[icon]["timeRemaining"] for icon in imgInfo}

previousTime = time.time()


#ICONS
#FOR RECORDINGS
"""iconTop:int = 55
iconLeft:int = 42 ##1
iconLength:float = 37.
iconOverlapVal = 0.25"""

#FOR REAL TIME
iconTop:int = 58
iconLeft:int = 0 
iconLength:int = 38
iconOverlapVal = 0 #0 was the best



monitor = 0 #Defines which monitor to look at
#folderName = "BuffBarScreenshots"
#os.makedirs(folderName, exist_ok=True)


def checkActiveScreen():
    # Get all windows

    # Search for a specific window title
    target_title = "Roblox"
    windows = gw.getAllWindows()
    for w in windows:
        if w.title == target_title:
            win = w
            print(win.width)
            if win.left == -8:
                iconTop = 81
            elif win.left == 0:
                iconTop = 58
            else:
                win.maximize()
                iconTop = 58
    return iconTop

def updateByElapsed(elapsed, icon):
    if icon in updatedTimer:                        
        updatedTimer[icon] = updatedTimer[icon] - elapsed

        if updatedTimer[icon] > 0:
            print(f"'{icon}' timer is at {round(updatedTimer[icon], 0)}s")
        else:
            #print(f"'{icon}' has reached 0")
            updatedTimer[icon] = max(updatedTimer[icon], 0) #Ensures that the timer does not go below 0

def opaqueBackgroundTimer(iconCapture, icon):
    target_colour = np.array(imgInfo[icon]["backgroundColour"], dtype=np.uint8)
    mask = np.all(iconCapture == target_colour, axis=2)
    iconCapture[mask] = [255,255,255]
    white = np.array([255, 255, 255], dtype=np.uint8)
    white_mask = np.all(iconCapture == white, axis=2) #CHATGPT SECTION
    white_per_row = np.sum(white_mask, axis=1)
    #print(f"White Per Row: {white_per_row}")
    first_row = np.where(white_per_row > 0)[0]
    
    #rows_with_background = np.where(np.any(mask, axis=1))[0]
    #print(first_row)
    if len(first_row) == 0:
        first_row = int(iconLength)
    else:
        first_row = first_row[0]
    #print(f"First Row {first_row}")
    #print(f"White Per Row {white_per_row}")
    return first_row

def transparentBackgroundTimer(iconCapture, icon, **kvargs):
    lower = np.array(imgInfo[icon]["backgroundColourLower"], dtype=np.uint8)
    upper = np.array(imgInfo[icon]["backgroundColourUpper"], dtype=np.uint8)
    #icon_int = iconCapture.astype(np.uint8)
    #Timer = kvargs.get("Timer", 5)
    mask = np.all((lower <= iconCapture) & (iconCapture <= upper), axis=2)
    iconCapture[mask] = [255,255,255]
    white = np.array([255, 255, 255], dtype=np.uint8)
    white_mask = np.all(iconCapture == white, axis=2) #CHATGPT SECTION
    white_per_row = np.sum(white_mask, axis=1)

    #print(type(white_per_row))
    first_row = np.where(white_per_row > 0)[0]
    #print(len(first_row))
    if len(first_row) == 0:
        first_row = int(iconLength)
    else:
        first_row = first_row[0]

    #print(f"First Row {first_row} with type {type(first_row)}")
    #print(f"White Per Row {white_per_row}")

    return first_row

def soundPlayer(updatedTimer, icon):
    if 0 < updatedTimer[icon] <= imgInfo[icon]["announceTime"]:
        if not f"sound{icon}".get_busy(): #Checks if audio is already playing
            f"sound{icon}".play()

def updateScreenshot():
    with mss.mss() as sct:
        global previousTime, redBloomChannel, precisionChannel, iconTop
        currentTime = time.time()
        elapsed = currentTime - previousTime
        elapsed = elapsed
        print(elapsed)
        try:
            iconTop = checkActiveScreen()
            failText = None
        except:
            failText = "Roblox Is\nNot Open"
            print(failText)
        
        captureArea = {"top": iconTop, "left": iconLeft, "width": m.width, "height": int(iconLength)} #Defines the screenshotting area using a dictionary.

        sct_image = sct.grab(captureArea) #Takes the image and stores in memory
        isInList = []
        iconImage = {}
        iconAmount = int((m.width // iconLength) - 1)
        for amount in range(iconAmount):
            x1:int = int(round(amount * (iconLength - iconOverlapVal)))
            x2:int = int(round(x1 + iconLength))
            y1 = 0
            y2 = int(round(iconLength))
       
            iconCapture = np.array(sct_image)[:, :, :3] #Format Screenshot
            iconCapture = iconCapture[y1:y2, x1:x2] #Crop the screenshot to only include the current icon
            for icon in definedIcons:
                maskedIconCapture = iconCapture.copy()
                base = np.array(imgInfo[icon]["foregroundColour"], dtype=np.int16)
                tolerance = imgInfo[icon]["tolerance"]

                upper = np.clip(base + tolerance, 0, 255).astype(np.uint8)
                lower = np.clip(base - tolerance, 0, 255).astype(np.uint8)

                mask = np.all((lower <= iconCapture) & (iconCapture <= upper), axis=2)
                mask = ~mask
                maskedIconCapture[mask] = [255,255,255]
                  

                comparison = cv2.imread(resourcePath(imgInfo[icon]["imageComparePath"]))
                #Template Matching
                gray_img = cv2.cvtColor(maskedIconCapture, cv2.COLOR_BGR2GRAY)
                gray_template = cv2.cvtColor(comparison, cv2.COLOR_BGR2GRAY)
                result = cv2.matchTemplate(gray_img, gray_template, cv2.TM_CCOEFF_NORMED)
                confidence = np.max(result)

                #cv2.imshow(f"grayTemplate", gray_template)

                if confidence > 0.75 and icon not in isInList: #Precision threshold is around 0.4
                    isInList.append(icon)
                    iconImage[icon] = iconCapture
                    print(f"Template matching confidence for {icon} at {amount}: {confidence}")

        if True: #>= 1:
            #print(f"{isInList}")
            previousTime = time.time()
            for icon in isInList: 
                iconCapture = iconImage[icon]
                if imgInfo[icon]["backgroundTransparency"] == True:
                    first_row = transparentBackgroundTimer(iconCapture, icon)
                if imgInfo[icon]["backgroundTransparency"] == False:
                    first_row = opaqueBackgroundTimer(iconCapture, icon)
                #print(f"First Row: {first_row}")

                #Calculating Remaining time
                remaingingTime = (1 - (int(first_row) / int(iconLength))) * imgInfo[icon]["refresh"]

                #print(f"{remaingingTime:.1f}")

                #updateByElapsed(updatedTimer, elapsed, icon)
                updatedTimer[icon] = max(remaingingTime, 0) #Ensures that the timer does not go below 0
                """if remaingingTime >= imgInfo[icon]["refresh"] * (int(iconLength) - 1)/(int(iconLength)): #Function to update the timer with a newer one if 
                    updatedTimer[icon] = remaingingTime
                    print(f"Timer has been refreshed")
                
                upperBound = remaingingTime * 1.1
                lowerBound = remaingingTime * 0.9

                if lowerBound < updatedTimer[icon] < upperBound or updatedTimer[icon] < 0:
                    updatedTimer[icon] = remaingingTime
                    #print(f"Timer has been adjusted to {updatedTimer[icon]:.1f}s")"""

    for icon in updatedTimer:
        updateByElapsed(elapsed, icon)
        #print(f"{updatedTimer[icon]} '{icon}' has been updated.")
        if 0 < updatedTimer["precision"] <= imgInfo["precision"]["announceTime"]:
                if precisionChannel is None or not precisionChannel.get_busy(): #Checks if audio is already playing
                    precisionChannel = soundprecision.play()#print("Playing precision sound")#precisionChannel = soundprecision.play()
        if 0 < updatedTimer["redbloom"] <= imgInfo["redbloom"]["announceTime"]:
                if redBloomChannel is None or not redBloomChannel.get_busy(): #Checks if audio is already playing
                    redBloomChannel = soundredbloom.play()

        #soundPlayer(updatedTimer, icon)
    text = text = "\n".join(
        f"{k}: {int(round(updatedTimer[k], 0))}s"
        for k in definedIcons
    )

    if failText != None:
        text = failText

    label.config(text=text)
    root.after(100, updateScreenshot) #Updates the screenshot every second, this is a recursive function call

updateScreenshot()

root.mainloop()