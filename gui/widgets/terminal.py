import qt_core as qt


class TerminalWidget(qt.QWidget):
    class ClickableFiller(qt.QWidget):
        def __init__(self, input_line, parent=None):
            super().__init__(parent)
            self.setObjectName("fillerWidget")
            self.input_line = input_line
            self.setMinimumHeight(0)
            self.setSizePolicy(qt.QSizePolicy.Policy.Expanding, qt.QSizePolicy.Policy.Expanding)
            self.setAttribute(qt.Qt.WidgetAttribute.WA_StyledBackground, True)
            # self.setStyleSheet(f"background-color: #000000; padding: 0px;")

        def mousePressEvent(self, event):
            self.input_line.setFocus()
            event.accept()

    def __init__(self, theme, parent=None):
        super().__init__(parent)
        self.setObjectName("TerminalWidget")
        self.theme = theme
        self.current_prompt = "BROADCAST"

        self.command_history = []
        self.history_index = -1

        # UI Setup
        self.layout = qt.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.output_area = qt.QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.output_area.setWordWrapMode(qt.QTextOption.WrapMode.WrapAnywhere)
        self.output_area.setVerticalScrollBarPolicy(qt.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.output_area.setFocusPolicy(qt.Qt.FocusPolicy.NoFocus)
        self.output_area.setTextInteractionFlags(qt.Qt.TextInteractionFlag.TextSelectableByMouse)

        self.output_area.setMinimumHeight(0)
        self.output_area.setMaximumHeight(0)

        self.input_container = qt.QWidget(self)
        input_layout = qt.QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(5, 0, 0, 0)
        input_layout.setSpacing(0)

        self.prompt_label = qt.QLabel(f"[{self.current_prompt}]> ")
        self.input_line = qt.QLineEdit(self)
        self.input_line.returnPressed.connect(self.handle_enter)
        self.input_line.installEventFilter(self)

        input_layout.addWidget(self.prompt_label)
        input_layout.addWidget(self.input_line)

        self.filler_widget = self.ClickableFiller(self.input_line, self)
        # self.filler_widget = qt.QWidget(self)
        # self.filler_widget.setMinimumHeight(0)
        # self.filler_widget.setSizePolicy(qt.QSizePolicy.Policy.Expanding, qt.QSizePolicy.Policy.Expanding)

        self.layout.addWidget(self.output_area)
        self.layout.addWidget(self.input_container)
        self.layout.addWidget(self.filler_widget)

        # Styles
        # terminal_style = "background-color: #000000; color: #FFFFFF; font-family: 'Consolas', 'Courier New', monospace; font-size: 12px; border: none; margin: 0px;"
        # self.output_area.setStyleSheet(f"QTextEdit {{ {terminal_style} padding: 5px; line-height: 18px; }}")
        # self.input_container.setStyleSheet(f"QWidget {{ {terminal_style} padding: 0px 5px 5px 5px; }}")
        # self.input_line.setStyleSheet(
        #     f"QLineEdit {{ {terminal_style} border-left: 3px solid #000000; border-right: 3px solid #000000; border-top: none; border-bottom: none; padding: 0px; line-height: 18px; }}")
        # self.prompt_label.setStyleSheet(f"QLabel {{ {terminal_style} padding: 0px; line-height: 18px; }}")
        # self.filler_widget.setStyleSheet(f"QWidget {{ {terminal_style} padding: 0px;}}")
        # self.setStyleSheet("QWidget { background-color: #000000; border: 1px solid #333333; }")

        # Initial content
        self.add_output("DefCodex MManager [Version 2.0.0]")
        self.input_line.setFocus()

    def adjust_output_height(self):
        content_height = int(self.output_area.document().size().height() + 2)
        max_height = self.height() - self.input_line.sizeHint().height()
        final_height = max(min(content_height, max_height), 35)

        self.output_area.setVerticalScrollBarPolicy(
            qt.Qt.ScrollBarPolicy.ScrollBarAlwaysOn if content_height > max_height else
            qt.Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.output_area.setMinimumHeight(final_height)
        self.output_area.setMaximumHeight(final_height)

    def handle_enter(self):
        command = self.input_line.text()
        if command.strip() and (len(self.command_history) == 0 or command != self.command_history[-1]):
            self.command_history.append(command)
        self.history_index = -1
        text = f"{self.current_prompt}> {command}"
        self.add_output(text)
        self.input_line.clear()
        self.input_line.setFocus()

    def add_output(self, text):
        content = f"{self.output_area.toPlainText()}\n{text}" if self.output_area.toPlainText() else text
        self.output_area.setPlainText(f"{content}")
        self.adjust_output_height()
        self.output_area.moveCursor(qt.QTextCursor.MoveOperation.End)
        scrollbar = self.output_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        self.output_area.ensureCursorVisible()

    def update_prompt(self, new_prompt=None):
        if new_prompt: self.current_prompt = new_prompt
        self.prompt_label.setText(f"[{self.current_prompt}]")

    def eventFilter(self, watched, event):
        if watched == self.input_line and event.type() == qt.QEvent.Type.KeyPress and isinstance(event, qt.QKeyEvent):
            key = event.key()

            if key == qt.Qt.Key.Key_Up:
                if self.command_history and self.history_index > 0:
                    self.history_index -= 1
                    self.input_line.setText(self.command_history[self.history_index])
                elif self.command_history and self.history_index == -1:
                    self.history_index = len(self.command_history) - 1
                    self.input_line.setText(self.command_history[self.history_index])

            elif key == qt.Qt.Key.Key_Down:
                if self.command_history and len(self.command_history) - 1 > self.history_index > -1:
                    self.history_index += 1
                    self.input_line.setText(self.command_history[self.history_index])
                else:
                    self.input_line.clear()
                    self.history_index = -1

        return super().eventFilter(watched, event)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.input_line.setFocus()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_output_height()