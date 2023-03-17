from json import load
from PIL import Image
from pkg_resources import Requirement, resource_filename
from pyautogui import locateOnScreen,screenshot
import pytesseract
from time import sleep


# If you don't have tesseract executable in your PATH, include the following:
#pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
# Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
def find_on_screen(img_file):
    try:
        loc = locateOnScreen(img_file, confidence = 0.9)
        if loc is None:
            raise TypeError
    except TypeError:
        sleep(2)
        print("Couldnt find, retrying")
        loc = find_on_screen(img_file) 
    return loc

# Simple image to string
img_file_loc = resource_filename(Requirement.parse("czfacsautomation"), "config/gui_snippets/")
img_file = img_file_loc + 'mac/test3.png'

loc = find_on_screen(img_file)
offset = [2,2,2,2]
new_loc = [sum(x) for x in zip(loc,offset)]
screenie = screenshot(region=loc)
strng = pytesseract.image_to_string(screenie)