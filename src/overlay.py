#!/usr/bin/env python3.9
import sys
import numpy as np
from scipy.spatial.transform import Rotation
from geometry import Vector2, Vector3, TransformMatrix

from mumble_link import MumbleLink
from gw2_api import GW2API

from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication

import time

link = MumbleLink()
api = GW2API()

print(link)

# Pos 1 =               (-57.73, 24.00, 158.40)
# Moving to the east =  (-42.92, 24.00, 158.43)
# Moving to the west  = (-70.71, 24.00, 158.37)
# X Axis = West -> East
# Y Axis = Down -> Up
# Z Axis = South -> North
# Pos 2 =               (-57.73, 24.00, 158.40)
# Moving to the north = (-57.76, 24.00, 170.93)
# Moving to the south = (-57.70, 23.99, 147.88)

"""

void CMatrix4x4::SetLookAtLH( const CVector3 &Eye, const CVector3 &Target, const CVector3 &Up )
{
  CVector3 &Z = Target - Eye;
  Z.Normalize();
  CVector3 &X = Up%Z;
  CVector3 &Y = Z%X;
  Y.Normalize();
  X.Normalize();

  _11 = X.x; _12 = Y.x; _13 = Z.x; _14 = 0.0f;
  _21 = X.y; _22 = Y.y; _23 = Z.y; _24 = 0.0f;
  _31 = X.z; _32 = Y.z; _33 = Z.z; _34 = 0.0f;
  _41 = -X*Eye; _42 = -Y*Eye; _43 = -Z*Eye; _44 = 1.0f;
}

CMatrix4x4 cam;
cam.SetLookAtLH( camPosition, camPosition + camFront, CVector3( 0, 1, 0 ) );

void CMatrix4x4::SetPerspectiveFovLH(float fovy, float aspect, float zn, float zf)
{
  SetIdentity();
  _11 = 1.0f / ( aspect*tanf( fovy / 2.0f ) );
  _22 = 1.0f / tanf( fovy / 2.0f );
  _33 = zf / ( zf - zn );
  _34 = 1.0f;
  _43 = ( zf*zn ) / ( zn - zf );
  _44 = 0.0f;
}
float asp = drawrect.Width() / drawrect.Height();
persp.SetPerspectiveFovLH( mumbleLink.fov, asp, 0.01f, 150.0f );

VSOUT vsmain(VSIN x) {
    VSOUT k;
    k.p = k.Position = mul(camera,(x.Position-x.Pos2)*width+x.Pos2);
    k.p/=k.p.w;

    float4 p2 = mul(camera,x.Pos2);
    p2/=p2.w;
    k.Position=mul(persp,(k.Position-p2)*width2d+p2);
    k.UV=float2(x.UV.x,x.UV.y*uvScale);
    k.Color=x.Color;
    k.p/=k.p.w;
    return k;
}

--------

bool computePixelCoordinates(
    const Vec3f &pWorld,
    const Matrix44f &cameraToWorld,
    const float &canvasWidth,
    const float &canvasHeight,
    const int &imageWidth,
    const int &imageHeight,
    Vec2i &pRaster)
{
    // First transform the 3D point from world space to camera space.
    // It is of course inefficient to compute the inverse of the cameraToWorld
    // matrix in this function. It should be done outside the function, only once
    // and the worldToCamera should be passed to the function instead.
    // We are only compute the inverse of this matrix in this function ...
     Vec3f pCamera;
     Matrix44f worldToCamera = cameraToWorld.inverse();
     worldToCamera.multVecMatrix(pWorld, pCamera);
     // Coordinates of the point on the canvas. Use perspective projection.
     Vec2f pScreen;
     pScreen.x = pCamera.x / -pCamera.z;
     pScreen.y = pCamera.y / -pCamera.z;
     // If the x- or y-coordinate absolute value is greater than the canvas width
     // or height respectively, the point is not visible
     if (std::abs(pScreen.x) > canvasWidth || std::abs(pScreen.y) > canvasHeight)
         return false;
     // Normalize. Coordinates will be in the range [0,1]
     Vec2f pNDC;
     pNDC.x = (pScreen.x + canvasWidth / 2) / canvasWidth;
     pNDC.y = (pScreen.y + canvasHeight / 2) / canvasHeight;
     // Finally convert to pixel coordinates. Don't forget to invert the y coordinate
     pRaster.x = std::floor(pNDC.x * imageWidth);
     pRaster.y = std::floor((1 - pNDC.y) * imageHeight);

     return true;
}

int main(...)
{
    ...
    Matrix44f cameraToWorld(...);
    Vec3f pWorld(...);
    float canvasWidth = 2, canvasHeight = 2;
    uint32_t imageWidth = 512, imageHeight = 512;
    // The 2D pixel coordinates of pWorld in the image if the point is visible
    Vec2i pRaster;
    if (computePixelCoordinates(pWorld, cameraToWorld, canvasWidth, canvasHeight, imageWidth, imageHeight, pRaster)) {
       std::cerr << "Pixel coordinates " << pRaster << std::endl;
    }
    else {
       std::cert << Pworld << " is not visible" << std::endl;
    }
    ...

    return 0;
}

"""

class Camera:
    def __init__(self, location: Vector3, focus: Vector3, screenShape: Vector2, fov: float):
        """
        @param location an (x, y, z) tuple where x is west <-> east, y is down <-> up, and z is south <-> north
        @param rotation euler angle rotation
        """
        # Width and height of the screen
        self.screenShape = screenShape

        # Create transform matrices (TACO method)
        focus = focus.normalize()
        x_axis = Vector3.up().cross(focus).normalize()
        y_axis = focus.cross(x_axis).normalize()
        self.camera_to_world = TransformMatrix.identity()
        self.camera_to_world[:3, 0] = x_axis._np_arr
        self.camera_to_world[:3, 1] = y_axis._np_arr
        self.camera_to_world[:3, 2] = focus._np_arr
        self.camera_to_world[3, :3] = location._np_arr
        # ???
        self.camera_to_world = self.camera_to_world.transpose()
        print("CameraToWorld transform:", self.camera_to_world, sep='\n')

        self.world_to_camera = self.camera_to_world.inverse()
        print("WorldToCamera transform:", self.world_to_camera, sep='\n')

        aspect = self.screenShape.x / self.screenShape.y
        print("Aspect:", aspect)
        print("FOV:", link.identity.fov)
        zn = 0.01
        zf = 150.0
        self.perspective_transform = TransformMatrix.identity()
        self.perspective_transform[0,0] = 1 / (aspect * np.tan(fov / 2))
        self.perspective_transform[1,1] = 1 / np.tan(fov / 2)
        self.perspective_transform[2,2] = zf / (zf - zn)
        self.perspective_transform[2,3] = 1
        self.perspective_transform[3,2] = (zf * zn) / (zn - zf)
        self.perspective_transform[3,3] = 0
        # ???
        self.perspective_transform = self.perspective_transform.transpose()
        #self.perspective_transform = self.perspective_transform.inverse()
        print("Taco Persp Transform:", self.perspective_transform, sep='\n')

    def worldToScreenPoint(self, point: Vector3) -> Vector2:
        width = self.screenShape.x
        height = self.screenShape.y
        width_percent = width / (width + height)
        height_percent = height / (width + height)
        # ???
        magic = 5
        canvas_width = width_percent * magic
        canvas_height = height_percent * magic

        # Convert from world to camera space
        cameraPoint = point
        # ???
        #cameraPoint = self.perspective_transform.apply(cameraPoint)
        cameraPoint = self.world_to_camera.apply(cameraPoint)
        cameraPoint = self.perspective_transform.apply(cameraPoint)

        # Convert from camera space to screen coordinates
        screenPoint = Vector2()
        # ???
        #screenPoint.x = (cameraPoint.x / -cameraPoint.z)
        #screenPoint.y = (cameraPoint.y / -cameraPoint.z)
        screenPoint.x = (cameraPoint.x / cameraPoint.z)
        screenPoint.y = (cameraPoint.y / cameraPoint.z)

        print("ScreenPoint Pre-normal:", screenPoint)

        # Check if the point is visible
        if abs(screenPoint.x) > canvas_width or abs(screenPoint.y) > canvas_height:
            return None

        # Normalize
        normalizedPoint = Vector2()
        normalizedPoint.x = (screenPoint.x + (canvas_width / 2)) / canvas_width
        normalizedPoint.y = (screenPoint.y + (canvas_height / 2)) / canvas_height

        print("Normalized ScreenPoint:", normalizedPoint)

        # Convert to pixel coordinates
        result = Vector2(dtype=int)
        result.x = np.floor(normalizedPoint.x * self.screenShape.x)
        result.y = np.floor((1 - normalizedPoint.y) * self.screenShape.y)
        return result

    def screenToWorldPoint(self, position: Vector2, z: float) -> Vector3:
        pass


def vertices_around(point: Vector3):
    bottom = np.array(point._np_arr)
    top = np.array(point._np_arr)
    top[1] += 2

    bottom_northwest = Vector3(np.array(bottom))
    bottom_northwest[2] += 2
    bottom_northwest[0] -= 2

    bottom_northeast = Vector3(np.array(bottom))
    bottom_northeast[2] += 2
    bottom_northeast[0] += 2

    bottom_southeast = Vector3(np.array(bottom))
    bottom_southeast[2] -= 2
    bottom_southeast[0] += 2

    bottom_southwest = Vector3(np.array(bottom))
    bottom_southwest[2] -= 2
    bottom_southwest[0] -= 2

    top_northwest = Vector3(np.array(top))
    top_northwest[2] += 2
    top_northwest[0] -= 2

    top_northeast = Vector3(np.array(top))
    top_northeast[2] += 2
    top_northeast[0] += 2

    top_southeast = Vector3(np.array(top))
    top_southeast[2] -= 2
    top_southeast[0] += 2

    top_southwest = Vector3(np.array(top))
    top_southwest[2] -= 2
    top_southwest[0] -= 2

    return {
        '+SW': top_southwest,
        '+NW': top_northwest,
        '+SE': top_southeast,
        '+NE': top_northeast,
        '-SW': bottom_southwest,
        '-NW': bottom_northwest,
        '-SE': bottom_southeast,
        '-NE': bottom_northeast,
    }


def wireframe_around(point: Vector3):
    bottom = np.array(point._np_arr)
    top = np.array(point._np_arr)
    top[1] += 2

    bottom_northwest = Vector3(np.array(bottom))
    bottom_northwest[2] += 2
    bottom_northwest[0] -= 2

    bottom_northeast = Vector3(np.array(bottom))
    bottom_northeast[2] += 2
    bottom_northeast[0] += 2

    bottom_southeast = Vector3(np.array(bottom))
    bottom_southeast[2] -= 2
    bottom_southeast[0] += 2

    bottom_southwest = Vector3(np.array(bottom))
    bottom_southwest[2] -= 2
    bottom_southwest[0] -= 2

    top_northwest = Vector3(np.array(top))
    top_northwest[2] += 2
    top_northwest[0] -= 2

    top_northeast = Vector3(np.array(top))
    top_northeast[2] += 2
    top_northeast[0] += 2

    top_southeast = Vector3(np.array(top))
    top_southeast[2] -= 2
    top_southeast[0] += 2

    top_southwest = Vector3(np.array(top))
    top_southwest[2] -= 2
    top_southwest[0] -= 2

    return (
        (top_southwest, top_northwest),
        (top_northwest, top_northeast),
        (top_northeast, top_southeast),
        (top_southeast, top_southwest),

        (bottom_southwest, bottom_northwest),
        (bottom_northwest, bottom_northeast),
        (bottom_northeast, bottom_southeast),
        (bottom_southeast, bottom_southwest),

        (top_southwest, bottom_southwest),
        (top_northwest, bottom_northwest),
        (top_northeast, bottom_northeast),
        (top_southeast, bottom_southeast),
    )


class MainWindow(QMainWindow):
    def __init__(self):
        screenShape = QtWidgets.qApp.desktop().availableGeometry()

        QMainWindow.__init__(self)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint |
            QtCore.Qt.WindowTransparentForInput
        )
        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter,
                QtCore.QSize(screenShape.width(), screenShape.height()),
                screenShape
        ))
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.paint_timer = QtCore.QTimer(self)
        self.paint_timer.setInterval(50)
        self.paint_timer.timeout.connect(self.update)
        self.paint_timer.start()

    def paintEvent(self, event=None):
        link.update()
        screenShape = QtWidgets.qApp.desktop().availableGeometry()
        painter = QtGui.QPainter(self)

        # Paint rectangle
        painter.setOpacity(0.1)
        painter.setBrush(QtCore.Qt.white)
        painter.setPen(QtGui.QPen(QtCore.Qt.white))
        painter.drawRect(self.rect())

        # Paint text
        painter.setFont(QtGui.QFont("Ubuntu Sans", 12, QtGui.QFont.Bold))
        painter.setOpacity(0.7)
        painter.setPen(QtGui.QPen(QtCore.Qt.black))

        camera = Camera(
            Vector3(link.camera_position),
            Vector3(link.camera_front),
            Vector2(np.array([screenShape.width(), screenShape.height()], dtype=int)),
            link.identity.fov
        )

        stairs_position = Vector3(np.array((133.38336181640625, 30.58201789855957, -166.88389587402344)))
        for start, stop in wireframe_around(stairs_position):
            start = camera.worldToScreenPoint(start)
            stop = camera.worldToScreenPoint(stop)
            if start and stop:
                painter.drawLine(QtCore.QPoint(start.x, start.y), QtCore.QPoint(stop.x, stop.y))

        for label, point in vertices_around(Vector3(link.avatar_position)).items():
            point = camera.worldToScreenPoint(point)
            if point:
                painter.drawText(QtCore.QPoint(point.x, point.y), label)

        painter.drawText(QtCore.QPoint(int(screenShape.width()/2), int(screenShape.height()/2)), "O")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()
