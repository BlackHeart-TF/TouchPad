import sys
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QPainter, QColor, QBrush, QPen
from PySide2.QtCore import Qt, QRectF,QSize,QPointF,QTimer
from vgamepad import VX360Gamepad
import pyWinhook as pyHook
import pythoncom

class TouchToggleWindow(QWidget):
    ShownColor = QColor(0, 0, 0, 5)
    HiddenColor = QColor(0, 0, 0, 0)
    def __init__(self):
        super().__init__()
        self.start_point,self.current_point = None,None
        self.initUI()
        self.toggle_rect = QRectF(70, 70, 60, 60)  # Circle area
        self.stick_size = QSize(300, 300)  # Circle area
        self.interactive = False  # Flag to toggle interactivity
        self.gamepad = VX360Gamepad()
        self.initMouseHook()


    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(QApplication.desktop().screenGeometry())

    def paintEvent(self, event):
        painter = QPainter(self)
        print("repainted")
        painter.setCompositionMode(QPainter.CompositionMode_Source)
       
        #painter.fillRect(self.rect(), TouchToggleWindow.ShownColor if self.interactive else TouchToggleWindow.HiddenColor)  # Fully transparent

        painter.setBrush(QBrush(QColor(255, 0, 0, 64)))  # Semi-transparent red
        painter.setPen(QPen(Qt.NoPen))
        painter.drawRoundedRect(self.toggle_rect,5,5)

        if self.interactive and self.start_point:
            # Draw the stationary circle
            pen = QPen(QColor(60, 60, 60, 128))
            pen.setWidth(5)
            painter.setPen(pen)
            painter.setBrush(QBrush(QColor(128, 128, 128, 64)))  # Semi-transparent green
            painter.drawRoundedRect(self.rounded_rect,20,20)  # Larger circle

            if self.current_point:
                # Draw the moving circle
                painter.setBrush(QBrush(QColor(90, 90, 90, 178)))  # Semi-transparent red
                painter.drawEllipse(self.current_point, 20, 20)  # Smaller circle

    def onmousePressEvent(self, event):
        position = QPointF(event.Position[0],event.Position[1])
        if self.toggle_rect.contains(position):
            self.interactive = not self.interactive
            if not self.interactive:
                self.start_point,self.current_point = None,None
                
            print(f"Interactive mode: {self.interactive}")
        elif self.interactive:
            self.start_point = position
            self.current_point = position
            rect_top_left = QPointF(
                self.start_point.x() - self.stick_size.width() / 2,
                self.start_point.y() - self.stick_size.height() / 2
            )
            self.rounded_rect = QRectF(rect_top_left, self.stick_size)
            print(f"Touch start: {self.start_point}")
            
        
        self.update()
        return not self.interactive

    def onmouseMoveEvent(self, event):
        if self.interactive and self.start_point:
            new_point = event.Position
            inner_rect = self.rounded_rect.adjusted(10, 10, -10, -10)

            # Constrain the new point within the inner rectangle
            constrained_x = min(max(new_point[0], inner_rect.left()), inner_rect.right())
            constrained_y = min(max(new_point[1], inner_rect.top()), inner_rect.bottom())
            self.current_point = QPointF(constrained_x, constrained_y)

            # Calculate relative position within the original rectangle
            relative_x = ((constrained_x - inner_rect.left()) / inner_rect.width()) * 2 - 1
            relative_y = 1- (((constrained_y - inner_rect.top()) / inner_rect.height()) * 2)
            self.axis_values = QPointF(relative_x, relative_y)
            self.set_left_stick(self.axis_values)
            print(f"{relative_x} {relative_y}")
            self.update()
        return True

    def onmouseReleaseEvent(self, event):
        # position = QPointF(event.Position[0],event.Position[1])
        # if not self.toggle_rect.contains(position):
            self.start_point = None
            self.current_point = None
            self.set_left_stick(QPointF(0,0))
            self.update()
            return True

        # Implement other event handlers if needed
    def set_left_stick(self, axis_values):
        """
        Set the position of the left stick on a virtual Xbox controller.

        :param gamepad: A vgamepad virtual gamepad object.
        :param axis_values: A QPointF with x and y values between -1.0 and 1.0.
        """
        # Normalize values to the range expected by vgamepad (0 to 32767)
        lx = int((axis_values.x() * 32767))
        ly = int((axis_values.y() * 32767))

        # Set the left stick position
        self.gamepad.left_joystick(lx,ly)
        print(f"{lx} {ly}")
        self.gamepad.update()

    def onMouseEvent(self,event):
        # Mouse press
        if event.MessageName == 'mouse left down':
            x, y = event.Position
            print(f"Mouse pressed at ({x}, {y})")
            # Send start position to your overlay application
            return self.onmousePressEvent(event)

        # Mouse move
        elif self.interactive and  event.MessageName == 'mouse move':
            x, y = event.Position
            # Send move position to your overlay application
            return self.onmouseMoveEvent(event)
            
        # Mouse release
        elif event.MessageName == 'mouse left up':
            x, y = event.Position
            print(f"Mouse released at ({x}, {y})")
            # Send end position to your overlay application
            return self.onmouseReleaseEvent(event)

        return True

    def initMouseHook(self):
        # Create a hook manager
        hm = pyHook.HookManager()
        # Set the mouse hook
        hm.SubscribeMouseLeftDown(self.onMouseEvent)
        hm.SubscribeMouseLeftUp(self.onMouseEvent)
        hm.SubscribeMouseMove(self.onMouseEvent)
        # Start the hook
        hm.HookMouse()
        # Enter into a perpetual loop
        # pythoncom.PumpMessages()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.processWinMessages)
        self.timer.start(100)  # Adjust the interval as needed

    def processWinMessages(self):
        pythoncom.PumpWaitingMessages()

app = QApplication(sys.argv)
window = TouchToggleWindow()
window.show()
sys.exit(app.exec_())
