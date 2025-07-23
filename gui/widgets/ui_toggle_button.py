import qt_core as qt


class UiToggleButton(qt.QCheckBox):
    def __init__(
            self,
            theme,
            parent = None,
            width: int = 60,
            height: int = 28,
            bg_color = "#777",
            circle_color = "#ddd",
            active_color = "#f59e0b",
    ):
        super().__init__(parent)
        self.theme = theme
        self._bg_color = bg_color
        self._circle_color = circle_color
        self._active_color = active_color

        self.setFixedSize(width, height)
        self.setCursor(qt.Qt.CursorShape.PointingHandCursor)

        self._circle_position = 3
        self.animation = qt.QPropertyAnimation(self, b'circle_position', self)
        self.animation.setEasingCurve(qt.QEasingCurve.Type.OutCirc)
        self.animation.setDuration(500)

        self.stateChanged.connect(self.start_animation)

    @qt.Property(float)
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, value):
        self._circle_position = value
        self.update()

    def start_animation(self, value):
        self.animation.stop()
        if value:
            self.animation.setEndValue(self.width() - 26)
        else:
            self.animation.setEndValue(3)

        self.animation.start()

    def hitButton(self, pos, /):
        return self.contentsRect().contains(pos)

    def paintEvent(self, event):
        painter = qt.QPainter()
        painter.begin(self)

        painter.setRenderHint(qt.QPainter.RenderHint.Antialiasing)
        painter.setPen(qt.Qt.PenStyle.NoPen)
        rect = qt.QRect(0, 0, self.width(), self.height())

        if not self.isChecked():
            painter.setBrush(qt.QBrush(self._bg_color))
        else:
            painter.setBrush(qt.QBrush(self._active_color))

        painter.drawRoundedRect(0, 0, rect.width(), self.height(), self.height() / 2, self.height() / 2)

        painter.setBrush(qt.QColor(self._circle_color))
        painter.drawEllipse(self._circle_position, 3, 22, 22)

        painter.end()
