import qt_core as qt


class FormInput(qt.QFrame):
    def __init__(self, theme, inputs_form: list[qt.QWidget], parent=None, text=''):
        super().__init__(parent)
        self.theme = theme
        self.text = text

        self.setStyleSheet("border: none; border-radius: 0px")
        self.layout = qt.QHBoxLayout(self)
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.layout.setSpacing(20)

        self.label = qt.QLabel(self, text=self.text)

        self.spacer = qt.QSpacerItem(0, 0, qt.QSizePolicy.Policy.Expanding, qt.QSizePolicy.Policy.Minimum)

        # Add layout
        if self.text:
            self.layout.addWidget(self.label)

        for input_item in inputs_form:
            self.layout.addWidget(input_item)

        self.layout.addSpacerItem(self.spacer)
