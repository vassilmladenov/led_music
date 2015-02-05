##
# Vassil Mladenov
# Serial monitor and spectrum visualizer for Arduino
##

import serial
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

window = 0                                             # glut window number
width, height = 1920, 1080                              # window size
uno = serial.Serial("/dev/tty.usbmodemfd131", 57600)   # initialize serial connection, 57600 baud rate

# typical keyboard callback 
def keyboard(key, x, y):
    if key == chr(27): # key to exit
        sys.exit(0)

def draw_rect(x, y, width, height):
    glBegin(GL_QUADS)                                  # start drawing a rectangle
    glVertex2f(x, y)                                   # bottom left point
    glVertex2f(x + width, y)                           # bottom right point
    glVertex2f(x + width, y + height)                  # top right point
    glVertex2f(x, y + height)                          # top left point
    glEnd()

def refresh2d(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, width, 0.0, height, 0.0, 1.0)
    glMatrixMode (GL_MODELVIEW)
    glLoadIdentity()

def drawMicrophoneBackground():
    glColor3f(0.5, 0.5, 0.5)                           # secondary dividers, mark at 50
    draw_rect(3, 110, 1914, 1)
    draw_rect(3, 310, 1914, 1)
    draw_rect(3, 510, 1914, 1)
    draw_rect(3, 710, 1914, 1)
    glColor3f(1.0, 1.0, 1.0)                           # main dividers, mark at 100
    draw_rect(3, 210, 1914, 1)
    draw_rect(3, 610, 1914, 1)                        
    draw_rect(3, 410, 1914, 1)
    draw_rect(3, 810, 1914, 1)

def draw35mmBackground():
    glColor3f(0.5, 0.5, 0.5)                           # secondary dividers, mark at 50
    draw_rect(3, 110, 1914, 1)
    draw_rect(3, 310, 1914, 1)
    draw_rect(3, 510, 1914, 1)
    draw_rect(3, 710, 1914, 1)
    glColor3f(1.0, 1.0, 1.0)                           # main dividers, mark at 100
    draw_rect(3, 210, 1914, 1)
    draw_rect(3, 610, 1914, 1)                        
    draw_rect(3, 410, 1914, 1)
    draw_rect(3, 810, 1914, 1)

def drawMicrophone(data):
    drawMicrophoneBackground()
    for i in range(len(data)):
        if (i < 3):
            setRGB(255, 255, 255)                      # white
        elif (i < 6):
            setRGB(0, 255, (i-3)*85)
        elif (i < 9):
            setRGB(0, (255-(i-6)*85), 255)
        elif (i < 16):
            setRGB((i-9)*51, 0, 255)
        elif (i < 33):
            setRGB(255, 0, (255-(i-16)*15))
        else:
            setRGB(255, (i-33)*7, 0)
        draw_rect(3 + i*30, 10, 23, data[i]*4)    # rect width 16, height proportional to data[i]

def draw35mm(data):
    draw35mmBackground()
    for i in range(len(data) / 2):
        if (i == 0):
            setRGB(255, 255, 255)
        elif (i == 1):
            setRGB(0, 255, 0)                      # white
        elif (i == 2):
            setRGB(0, 255, 255)
        elif (i == 3):
            setRGB(0, 0, 255)
        elif (i == 4):
            setRGB(255, 0, 255)
        elif (i == 5):
            setRGB(255, 0, 0)
        elif (i == 6):
            setRGB(255, 255, 0)
        draw_rect(5 + 2*i*137, 10, 127, data[i])    # rect width 16, height proportional to data[i]
        if (i == 0):
            setRGB(255, 255, 255)
        elif (i == 1):
            setRGB(0, 255, 127)                      # white
        elif (i == 2):
            setRGB(0, 127, 255)
        elif (i == 3):
            setRGB(127, 0, 255)
        elif (i == 4):
            setRGB(255, 0, 127)
        elif (i == 5):
            setRGB(255, 0, 0)
        elif (i == 6):
            setRGB(255, 255, 0)
        draw_rect(5 + 2*i*137+127, 10, 127, data[i+7])    # rect width 16, height proportional to data[i]

def draw():                                            # ondraw is called all the time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the screen
    glLoadIdentity()                                   # reset position
    refresh2d(width, height)                           # set mode to 2d
    data = uno.readline().rstrip().split("\t")         # read line, strip line endings (\r\n), split into array by tabs
    if (len(data) == 64):                              # need if statement, sometimes get bad data initially
        data = map(int, data)						   # string to int for entire array
        # print data                                     # debug statement to print array
        drawMicrophone(data)
    elif (len(data) == 14):
        data = map(int, data)
        draw35mm(data)

    glutSwapBuffers()                                  # important for double buffering

def setRGB(r, g, b):
    glColor3f(r / 255.0, g / 255.0, b / 255.0)    

# initialization
glutInit()                                             # initialize glut
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
glutInitWindowSize(width, height)                      # set window size
glutInitWindowPosition(0, 0)                           # set window position
window = glutCreateWindow("Arduino Visualizer")        # create window with title
glutKeyboardFunc(keyboard)                             # ESC to exit
glutDisplayFunc(draw)                                  # set draw function callback
glClearColor(0,0,0,0)                                  # white background, easier to see
glutIdleFunc(draw)                                     # draw all the time
glutMainLoop()