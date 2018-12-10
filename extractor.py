
from pynput.mouse import Listener
from pytesseract import image_to_string
from PIL import Image 

import os
import time

import cv2
import pyperclip
import pytesseract
import numpy as np
import pyautogui as gui


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"

gui.FAILSAFE = False # disable pyautogui's failsafe exception
num = 0 # counter for mapping mouse clicks to positions

save_location = os.path.abspath(os.path.dirname(__file__))

coordinates = { 'top_left': None, 'top_right': None, 'bottom_left': None, 'bottom_right': None }

def on_click(x, y, button, pressed):
    """Mouse-click callback from listener object"""

    global num
    if pressed:
        num += 1
        if num == 1:
            coordinates['top_left'] = (x, y)
            return False # stop the listener

        elif num == 2:
            coordinates['top_right'] = (x, y)
            return False

        elif num == 3:
            coordinates['bottom_left'] = (x, y)
            return False

        elif num == 4:
            coordinates['bottom_right'] = (x, y)
            return False

def activateListener():
    """Creates the listener object that tracks mouse clicks"""

    with Listener(on_click=on_click) as listener:
        listener.join()

def imageFormatter(coordinates):
    """Formats the coordinates for use with PyAutoGui"""

    width = max( coordinates['top_right'][0] - coordinates['top_left'][0], coordinates['bottom_right'][0] - coordinates['bottom_left'][0] )
    height = max( coordinates['bottom_right'][1] - coordinates['top_right'][1], coordinates['bottom_left'][1] - coordinates['top_left'][1] )
    left = coordinates['top_left'][0]
    top = coordinates['top_left'][1]

    return (left, top, width, height)


def imageCreator(left, top, width, height):
    """Creates the actual screenshot"""

    image_file = gui.screenshot(region=(left, top, width, height))
    image = os.path.join(save_location, 'screenshot_' + time.strftime('%H%M%S') + '.png')
    image_file.save(image)

    return image

def textExtractor(img):
    """Extracts the text from the image"""

    image = cv2.imread(img)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Morphological transformations for noise removal
    kernel = np.ones((1, 1), np.uint8)
    image = cv2.erode(image, kernel, iterations = 1)
    image = cv2.dilate(image, kernel, iterations = 1)
    
    image_path = os.path.join(save_location, "image_" + time.strftime("%H%M%S") + ".png")
    cv2.imwrite(image_path, image)
    
    result = pytesseract.image_to_string(Image.open(image_path))
    
    return result


def main():
    """Main application"""

    # Minimize the terminal immediately so it won't obstruct screenshot selection. (Tested only on Ubuntu 16.04)
    gui.hotkey('altleft', 'space'); gui.press('n') 

    positions = ['top left', 'top right', 'bottom left', 'bottom right']
    for i in positions:
        print('Click the {} of the screenshot'.format(i))
        activateListener() # start the listener

    image_details = imageFormatter(coordinates)
    image = imageCreator(*image_details) # create the picture (possibly with extractable text)

    gui.hotkey('altleft', 'tab') # return the terminal

    image_text = textExtractor(image) # extract the text from the image

    print('\nText in image is: ', image_text) # print the extracted text
        
if __name__ == '__main__':
    main()
