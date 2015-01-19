##
# Vassil Mladenov
# Serial monitor and spectrum visualizer for Arduino
##

import serial
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

window = 0                                             # glut window number
width, height = 1296, 820                              # window size
uno = serial.Serial("/dev/tty.usbmodemfd141", 57600)   # initialize serial connection, 57600 baud rate

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

def drawBackground():
    glColor3f(0.5, 0.5, 0.5)                           # secondary dividers, mark at 50
    draw_rect(10, 110, 1276, 1)
    draw_rect(10, 310, 1276, 1)
    draw_rect(10, 510, 1276, 1)
    draw_rect(10, 710, 1276, 1)
    glColor3f(1.0, 1.0, 1.0)                           # main dividers, mark at 100
    draw_rect(10, 210, 1276, 1)
    draw_rect(10, 610, 1276, 1)                        
    draw_rect(10, 410, 1276, 1)
    draw_rect(10, 810, 1276, 1)

def draw():                                            # ondraw is called all the time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the screen
    glLoadIdentity()                                   # reset position
    refresh2d(width, height)                           # set mode to 2d
    drawBackground()
    data = uno.readline().rstrip().split("\t")         # read line, strip line endings (\r\n), split into array by tabs
    if (len(data) == 64):                              # need if statement, sometimes get bad data initially
        data = map(int, data)						   # string to int for entire array
        # print data                                     # debug statement to print array
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
            draw_rect(10 + i*20, 10, 16, data[i]*4)    # rect width 16, height proportional to data[i]
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