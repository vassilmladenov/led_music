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
            if (i < 32):
                glColor3f(1.0 - 1.0/32 * i, i*1.0/32, 0.0)
            else:
                glColor3f(0.0, 1.0 - 1.0/31*(i-32), (i-32)*1.0/31)
            draw_rect(10 + i*20, 10, 16, data[i]*4)    # rect width 16, height proportional to data[i]
    glutSwapBuffers()                                  # important for double buffering
    

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