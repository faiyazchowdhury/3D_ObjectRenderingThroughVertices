# By Faiyaz Chowdhury, Part 2 of Neocis Coding Assessment
from tkinter import Tk, Canvas
from math import sin, cos, atan2, sqrt, pi

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

# Get Color from RGB
def RGBtoColor(rgb):
    """
    Changes RGB values to Hexadecimal String Color
    Arguments:
        rgb: RGB Values are tuple of 3 integers
    Returns:
        Color as Hexadecimal String
    """
    return "#%02x%02x%02x"%rgb

# 90 Degrees is 5F(95). 0 Degrees is FF(255)
def angleToBlueValue(angle):
    """
    Calculates the color of a face of the object
    Arguments:
        angle: angle of face pointing towards the camera
    Returns:
        An integer between 255 and 95, given an angle between 0 and pi/2
    """
    blue_value = round(255 - angle*160/(pi))
    if blue_value<0:
        return 0
    return blue_value

# Painter's algorithm sort, arranged by which triangle centroid is closest
def triangleSort(face):
    """
    Calculates the centroid of the triangle face. Used to sort farthest triangle for Painter's algorithm implementation
    Arguments:
        face: vector of 3 vertices of the triangle face
    Returns:
        Centroid coordinate
    """
    return sum([vertices[face[0]][2], vertices[face[1]][2], vertices[face[2]][2]])

def drawImage(phi, theta):
    """
    Draws the image in canvas, after performing several operations
    Arguments:
        phi: rotation about x-axis in radians
        theta: roation about y-axis in radians
    """
    for key in vertices.keys():
        vertices[key] = rotate(vertices[key], phi, theta)

    face = faces[0]
    v1 = vertices[face[0]]
    v2 = vertices[face[1]]
    v3 = vertices[face[2]]

    #Vector between points of triangular faces
    A = [v2[i] - v1[i] for i in range(3)]
    B = [v3[i] - v1[i] for i in range(3)]

    # Normal Vector of the planes
    N = [A[1] * B[2] - A[2] * B[1], A[2] * B[0] - A[0] * B[2], A[0] * B[1] - A[1] * B[0]]
    viewAngle = atan2(sqrt(N[1]**2 + N[0]**2) , -N[2])

    # Sorting makes the farther faces get displayed first, then covered up by closer faces
    sorted_faces = sorted(faces, key = triangleSort)

    for face in sorted_faces:
        v1 = vertices[face[0]]
        v2 = vertices[face[1]]
        v3 = vertices[face[2]]

        #Vector between points of triangular faces
        A = [v2[i] - v1[i] for i in range(3)]
        B = [v3[i] - v1[i] for i in range(3)]

        # Normal Vector of the planes
        N = [A[1] * B[2] - A[2] * B[1], A[2] * B[0] - A[0] * B[2], A[0] * B[1] - A[1] * B[0]]
        viewAngle = atan2(sqrt(N[1]**2 + N[0]**2) , -N[2])
        if viewAngle > pi/2:
            viewAngle = pi - viewAngle
        faceColor = RGBtoColor((0, 0, angleToBlueValue(viewAngle)))
        canvas.create_polygon([v1[0]+MIDDLE_SIZE,v1[1]+MIDDLE_SIZE,v2[0]+MIDDLE_SIZE,v2[1]+MIDDLE_SIZE,v3[0]+MIDDLE_SIZE,v3[1]+MIDDLE_SIZE], outline='blue', fill=faceColor, width=2)
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
    window.title("3D Shaded Object Part 2")
    canvas = Canvas(window, height=WINDOW_SIZE, width=WINDOW_SIZE)

    # Initial Drawing
    drawImage(0,0)
    canvas.bind('<Button-1>', pressButton)
    canvas.bind('<B1-Motion>', dragMouse)

    canvas.pack()
    window.mainloop()