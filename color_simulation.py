##
# Vassil Mladenov
##

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

window = 0                                             # glut window number
width, height = 1296, 420                              # window size

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

def draw():                                            # ondraw is called all the time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the screen
    glLoadIdentity()                                   # reset position
    refresh2d(width, height)                           # set mode to 2d
    for i in range(64):
        if (i < 1):
            setRGB(255, 255, 255)                      # white
        elif (i < 6):
            setRGB(255, (i-1)*51, 0.0)
        elif (i < 11):
            setRGB((255-(i-6)*51), 255, 0.0)
        elif (i < 16):
            setRGB(0, 255, (i-11)*51)
        elif (i < 33):
            setRGB(0, (255-(i-16)*15), 255)
        else:
            setRGB((i-33)*7, 0, 255)
        draw_rect(10 + i*20, 10, 16, 400)              # rect width 16, height
    glutSwapBuffers()                                  # important for double buffering
    
def setRGB(r, g, b):
    glColor3f(r / 255.0, g / 255.0, b / 255.0)

# initialization
glutInit()                                             # initialize glut
glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
glutInitWindowSize(width, height)                      # set window size
glutInitWindowPosition(0, 0)                           # set window position
window = glutCreateWindow("Color Simulation")          # create window with title
glutKeyboardFunc(keyboard)                             # ESC to exit
glutDisplayFunc(draw)                                  # set draw function callback
glClearColor(0,0,0,0)                                  # white background, easier to see
glutIdleFunc(draw)                                     # draw all the time
glutMainLoop()