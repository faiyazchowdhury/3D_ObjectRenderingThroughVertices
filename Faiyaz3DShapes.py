# By Faiyaz Chowdhury, Part 1 of Neocis Coding Assessment
from tkinter import Tk, Canvas
from math import sin, cos

WINDOW_SIZE = 800
POINT_SIZE = WINDOW_SIZE/200
MIDDLE_SIZE = WINDOW_SIZE/2
# NOTE GUI Buttons also have global values

#------Transformation Math-----------
def shiftToOriginAndScale(vertices, window_size):
    """
    Moves the vertices median point to the origin.
    Scales the objedt to be viable in canvas
    Arguments:
        vertices: A map of vertex ID keys and 3D coordinate values
        window_size: Number of pixels in the square canvas
    """
    points = list(zip(*vertices.values()))
    x_points = points[0]
    y_points = points[1]
    z_points = points[2]
    x_min = min(x_points)
    x_max = max(x_points)
    x_mid = (x_max+x_min)/2
    x_dis = x_max-x_mid
    y_min = min(y_points)
    y_max = max(y_points)
    y_mid = (y_max+y_min)/2
    y_dis = y_max-y_mid
    z_min = min(z_points)
    z_max = max(z_points)
    z_mid = (z_max+z_min)/2
    z_dis = z_max-z_mid
    scale = window_size/max(x_dis, y_dis, z_dis)/4
    x_offset = - x_mid
    y_offset = - y_mid
    z_offset = - z_mid
    for key in vertices.keys():
        x,y,z = vertices[key]
        vertices[key] = [(x+x_offset)*scale, (y+y_offset)*scale, (z+z_offset)*scale]

def rotate(point, phi, theta):
    """
    3D Matrix Rotation about x and y axis
    Arguments:
        point: [x,y,z] coordinate as list
        phi: rotation about x-axis in radians
        theta: roation about y-axis in radians
    Returns:
        Rotated [x,y,z] coordinate as list
    """
    x, y, z = point
    y, z = [y*cos(theta)+z*sin(theta),   -y*sin(theta)+z*cos(theta)] # rotate about x
    x, z = [x*cos(phi)  +z*sin(phi),     -x*sin(phi)  +z*cos(phi)] # rotate about y
    return [x,y,z]

def cameraTransform(point, focal_length, z_offset):
    """
    Projection of 3D point to Camera matrix
    CAMERA TRANSFORMATION NOT NEEDED: Infinite Distance: x' = x, y' = y
    Arguments:
        point: [x,y,z] coordinate as list
        focal_length: point at which z-distance becomes 0
        z_offset: minimun z value of points to prevent object being behind the camera or focal length.
    Returns:
        Camera point [x,y,z] coordinate as list
    """
    x,y,z = point
    z = z + z_offset
    return [focal_length*(x/z), focal_length*(y/z), z] # Finite Distance

def drawImage(phi, theta):
    """
    Draws the image in canvas, after performing several operations
    Arguments:
        phi: rotation about x-axis in radians
        theta: roation about y-axis in radians
    """
    for key in vertices.keys():
        vertices[key] = rotate(vertices[key], phi, theta)
    visited_edges = {}
    for face in faces:
        edges = [(min(a, b), max(a,b)) for idx, a in enumerate(face) for b in face[idx + 1:]]
        for edge in edges:
            if edge not in visited_edges:
                visited_edges[edge] = True;
                canvas.create_line(vertices[edge[0]][0]+MIDDLE_SIZE, vertices[edge[0]][1]+MIDDLE_SIZE, vertices[edge[1]][0]+MIDDLE_SIZE, vertices[edge[1]][1]+MIDDLE_SIZE, fill = "blue")
    [canvas.create_oval(x+MIDDLE_SIZE+POINT_SIZE, y+MIDDLE_SIZE+POINT_SIZE, x+MIDDLE_SIZE-POINT_SIZE, y+MIDDLE_SIZE-POINT_SIZE, fill="blue") for x,y,_ in vertices.values()]

#---------GUI Buttons-------------
def pressButton(event):
    """
    Sets the mouse coordinates upon clicking
    Arguments:
        event: Canvas.bind event
    """
    global press_x
    global press_y
    press_x = event.x
    press_y = event.y
    try:
        past_x = event.x
        past_y = event.y
        press_x = event.x
        press_y = event.y
    except NameError:
        press_x = event.x
        press_y = event.y

def dragMouse(event):
    """
    Sets the mouse coordinate changes after clicking to update image
    Arguments:
        event: Canvas.bind event
    """
    global past_x
    global past_y
    try:
        delta_x = event.x - past_x
        delta_y = event.y - past_y
        if (-10<delta_x and delta_x<10 and delta_y<10 and -10<delta_y): #Prevent Erratic motion
            canvas.delete('all')
            drawImage(delta_x/MIDDLE_SIZE, delta_y/MIDDLE_SIZE)
        past_x = event.x
        past_y = event.y
    except NameError:
        past_x = press_x
        past_y = press_y


if __name__ == '__main__':

    # Read File
    with open('object.txt') as file:
        lines = file.readlines()
    file.close()

    # Extracting Data
    numV, numF = list(map(int,(lines[0].rstrip('\n').split(","))))
    vertices = {}
    for line in range(1, numV+1):
        key, x,y,z = lines[line].rstrip('\n').split(",")
        vertices[int(key)] = [float(x),float(y),float(z)]
    faces = [list(map(int,lines[line].rstrip('\n').split(","))) for line in range(numV+1, numV+numF+1)] #Vertices indexed at 1

    # Shifting data to origin. Making everything fit in window
    shiftToOriginAndScale(vertices, WINDOW_SIZE)

    # Drawing Setup
    window = Tk()
    window.title("3D Object Part 1")
    canvas = Canvas(window, height=WINDOW_SIZE, width=WINDOW_SIZE)

    # Initial Drawing
    drawImage(0,0)
    canvas.bind('<Button-1>', pressButton)
    canvas.bind('<B1-Motion>', dragMouse)

    canvas.pack()
    window.mainloop()