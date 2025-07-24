import qt_core as qt
import os


class UiPushButton(qt.QPushButton):
    def __init__(
            self,
            theme,
            parent=None,
            text="",
            tooltip="",
            icon_path="",
            icon_bg="",
            icon_color="",
            icon_size=24,
            spacing=16,
            margin=16,
            width=60,
            height=60,
            gap=0,
            is_active=False
    ):
        super().__init__(parent)
        path = os.path.abspath(os.path.join(os.getcwd(), 'gui', 'icons', icon_path))

        self.icon_path = os.path.normpath(path)
        self.is_active = is_active
        self.tooltip = tooltip
        self.spacing = spacing
        self.margin = margin
        self.gap = gap
        self.icon_bg = icon_bg
        self.icon_color = icon_color
        self.theme = theme

        if text:
            self.setText("   " + text)
        if tooltip:
            self.setToolTip(f"<h2><b>{tooltip}</b></h2>")
        self.setMinimumHeight(height)
        self.setMinimumWidth(width)
        self.setCursor(qt.Qt.CursorShape.PointingHandCursor)

        self.setLayoutDirection(qt.Qt.LayoutDirection.LeftToRight)
        self.setIconSize(qt.QSize(icon_size, icon_size))

        self.set_icon()
        self.apply_style()


    def set_icon(self):
        pixmap = qt.QPixmap(self.icon_path)

        if pixmap.isNull():
            print(f"[UiPushButton] Erro: Ícone '{self.icon_path}' não encontrado.")
            return

        # Colore o ícone
        colored = qt.QPixmap(pixmap.size())
        colored.fill(qt.Qt.GlobalColor.transparent)

        painter = qt.QPainter(colored)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(qt.QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), qt.QColor(self.icon_color or self.theme['colors'].get('text_primary')))
        painter.end()

        self.setIcon(qt.QIcon(colored))

    def apply_style(self):
        base = f"""
            QPushButton {{
                color: {self.theme['colors'].get('text_primary')};
                background-color: {self.icon_bg or self.theme['colors'].get('panel')};
                border: none;
                padding: 0 {self.spacing}px;
                margin-top: {self.margin}px;
                margin-right: {self.gap}px;
                text-align: left;
            }}
            QPushButton:focus {{
                outline: none;
            }}
            QPushButton:hover {{
                color: {self.theme['colors'].get('black')};
                background-color: {self.theme['colors'].get('primary')};
            }}
            QPushButton:pressed {{
                background-color: {self.theme['colors'].get('highlight')};
            }}            
        """

        if self.tooltip:
            base += """
                QToolTip {
                    background-color: #333333;
                    color: white;
                    border: 1px solid #555555;
                    padding: 5px;
                    border-radius: 3px;
                    font-size: 12px;
                }
            """

        if self.is_active:
            base += f"""
                QPushButton {{
                    background-color: {self.theme['colors'].get('')};
                    border-right: 5px solid #282a36;
                }}
            """

        self.setStyleSheet(base)
