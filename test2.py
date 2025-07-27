import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QLabel, QLineEdit,
                               QFileDialog, QTextEdit, QMessageBox, QProgressBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os


class FileUploadForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Formulário de Envio de Arquivos")
        self.setGeometry(100, 100, 600, 500)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        layout = QVBoxLayout(central_widget)

        # Título
        title = QLabel("Upload de Arquivos")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Seção de seleção de arquivo único
        single_file_layout = QHBoxLayout()
        self.single_file_label = QLabel("Nenhum arquivo selecionado")
        self.single_file_label.setStyleSheet("border: 1px solid #ccc; padding: 5px; background: #f9f9f9;")
        single_file_btn = QPushButton("Selecionar Arquivo")
        single_file_btn.clicked.connect(self.select_single_file)

        single_file_layout.addWidget(QLabel("Arquivo único:"))
        single_file_layout.addWidget(self.single_file_label, 1)
        single_file_layout.addWidget(single_file_btn)
        layout.addLayout(single_file_layout)

        # Seção de seleção de múltiplos arquivos
        multi_file_layout = QHBoxLayout()
        self.multi_files_display = QTextEdit()
        self.multi_files_display.setMaximumHeight(100)
        self.multi_files_display.setPlaceholderText("Nenhum arquivo selecionado...")
        multi_file_btn = QPushButton("Selecionar Múltiplos")
        multi_file_btn.clicked.connect(self.select_multiple_files)

        multi_file_layout.addWidget(QLabel("Múltiplos arquivos:"))
        multi_file_layout.addWidget(self.multi_files_display, 1)
        multi_file_layout.addWidget(multi_file_btn)
        layout.addLayout(multi_file_layout)

        # Seção de seleção de pasta
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("Nenhuma pasta selecionada")
        self.folder_label.setStyleSheet("border: 1px solid #ccc; padding: 5px; background: #f9f9f9;")
        folder_btn = QPushButton("Selecionar Pasta")
        folder_btn.clicked.connect(self.select_folder)

        folder_layout.addWidget(QLabel("Pasta:"))
        folder_layout.addWidget(self.folder_label, 1)
        folder_layout.addWidget(folder_btn)
        layout.addLayout(folder_layout)

        # Seção de filtros específicos (imagens)
        image_layout = QHBoxLayout()
        self.image_label = QLabel("Nenhuma imagem selecionada")
        self.image_label.setStyleSheet("border: 1px solid #ccc; padding: 5px; background: #f9f9f9;")
        image_btn = QPushButton("Selecionar Imagem")
        image_btn.clicked.connect(self.select_image)

        image_layout.addWidget(QLabel("Imagem:"))
        image_layout.addWidget(self.image_label, 1)
        image_layout.addWidget(image_btn)
        layout.addLayout(image_layout)

        # Preview da imagem (pequeno)
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(150, 150)
        self.image_preview.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0;")
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setText("Preview")
        layout.addWidget(self.image_preview)

        # Campo de descrição
        layout.addWidget(QLabel("Descrição:"))
        self.description_field = QTextEdit()
        self.description_field.setMaximumHeight(80)
        self.description_field.setPlaceholderText("Digite uma descrição para os arquivos...")
        layout.addWidget(self.description_field)

        # Barra de progresso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Botões de ação
        button_layout = QHBoxLayout()
        clear_btn = QPushButton("Limpar Tudo")
        clear_btn.clicked.connect(self.clear_all)
        upload_btn = QPushButton("Enviar Arquivos")
        upload_btn.clicked.connect(self.upload_files)
        upload_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(upload_btn)
        layout.addLayout(button_layout)

    def select_single_file(self):
        """Seleciona um único arquivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo",
            "",
            "Todos os Arquivos (*);;Documentos (*.pdf *.doc *.docx);;Imagens (*.png *.jpg *.jpeg)"
        )

        if file_path:
            file_name = os.path.basename(file_path)
            self.single_file_label.setText(file_name)
            self.single_file_label.setToolTip(file_path)  # Mostra caminho completo no tooltip

    def select_multiple_files(self):
        """Seleciona múltiplos arquivos"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar Múltiplos Arquivos",
            "",
            "Todos os Arquivos (*);;Documentos (*.pdf *.doc *.docx);;Imagens (*.png *.jpg *.jpeg)"
        )

        if file_paths:
            self.selected_files = file_paths
            file_names = [os.path.basename(path) for path in file_paths]
            self.multi_files_display.setText("\n".join(file_names))

    def select_folder(self):
        """Seleciona uma pasta"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta",
            ""
        )

        if folder_path:
            folder_name = os.path.basename(folder_path)
            self.folder_label.setText(folder_name)
            self.folder_label.setToolTip(folder_path)

    def select_image(self):
        """Seleciona uma imagem com preview"""
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Imagem",
            "",
            "Imagens (*.png *.jpg *.jpeg *.gif *.bmp);;Todos os Arquivos (*)"
        )

        if image_path:
            image_name = os.path.basename(image_path)
            self.image_label.setText(image_name)
            self.image_label.setToolTip(image_path)

            # Mostrar preview da imagem
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.image_preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled_pixmap)

    def clear_all(self):
        """Limpa todos os campos"""
        self.single_file_label.setText("Nenhum arquivo selecionado")
        self.single_file_label.setToolTip("")
        self.multi_files_display.clear()
        self.folder_label.setText("Nenhuma pasta selecionada")
        self.folder_label.setToolTip("")
        self.image_label.setText("Nenhuma imagem selecionada")
        self.image_label.setToolTip("")
        self.image_preview.clear()
        self.image_preview.setText("Preview")
        self.description_field.clear()
        self.selected_files = []
        self.progress_bar.setVisible(False)

    def upload_files(self):
        """Simula o envio dos arquivos"""
        # Coleta todos os arquivos selecionados
        files_to_upload = []

        # Arquivo único
        if self.single_file_label.toolTip():
            files_to_upload.append(self.single_file_label.toolTip())

        # Múltiplos arquivos
        files_to_upload.extend(self.selected_files)

        # Pasta
        if self.folder_label.toolTip():
            files_to_upload.append(f"Pasta: {self.folder_label.toolTip()}")

        # Imagem
        if self.image_label.toolTip():
            files_to_upload.append(self.image_label.toolTip())

        if not files_to_upload:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um arquivo!")
            return

        # Simula progresso de upload
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(files_to_upload))

        # Aqui você implementaria a lógica real de upload
        for i, file_path in enumerate(files_to_upload):
            self.progress_bar.setValue(i + 1)
            # Simular processamento
            QApplication.processEvents()

        # Mensagem de sucesso
        description = self.description_field.toPlainText()
        msg = f"Arquivos enviados com sucesso!\n\n"
        msg += f"Total de arquivos: {len(files_to_upload)}\n"
        if description:
            msg += f"Descrição: {description}\n"
        msg += "\nArquivos:\n" + "\n".join([os.path.basename(f) for f in files_to_upload])

        QMessageBox.information(self, "Sucesso", msg)

        # Opcionalmente, limpar após o envio
        # self.clear_all()


def main():
    app = QApplication(sys.argv)
    window = FileUploadForm()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()