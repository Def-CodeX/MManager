import sys
import os
import re
import keyword
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTreeView, QTabWidget, QTextEdit, QFileSystemModel,
    QMessageBox, QFileDialog, QStatusBar, QInputDialog,
    QHeaderView, QMenu, QCompleter
)
from PySide6.QtCore import Qt, QDir, Signal, QStringListModel
from PySide6.QtGui import (
    QFont, QSyntaxHighlighter, QTextCharFormat, QColor,
    QKeyEvent, QTextCursor, QAction
)
import shutil


class PythonHighlighter(QSyntaxHighlighter):
    """Destacador de sintaxe para Python"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Definir formatos
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor(0, 0, 255))
        self.keyword_format.setFontWeight(QFont.Weight.Bold)

        self.builtin_format = QTextCharFormat()
        self.builtin_format.setForeground(QColor(128, 0, 128))
        self.builtin_format.setFontWeight(QFont.Weight.Bold)

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(0, 128, 0))

        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor(128, 128, 128))
        self.comment_format.setFontItalic(True)

        self.function_format = QTextCharFormat()
        self.function_format.setForeground(QColor(255, 140, 0))

        self.class_format = QTextCharFormat()
        self.class_format.setForeground(QColor(255, 165, 0))
        self.class_format.setFontWeight(QFont.Weight.Bold)

        # Palavras-chave do Python
        self.keywords = keyword.kwlist

        # Funções built-in do Python
        self.builtins = [
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr',
            'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter',
            'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
            'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max',
            'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord',
            'pow', 'print', 'property', 'range', 'repr', 'reversed', 'round',
            'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum',
            'super', 'tuple', 'type', 'vars', 'zip', '__import__'
        ]

    def highlightBlock(self, text):
        # Destacar palavras-chave
        for word in self.keywords:
            pattern = r'\b' + re.escape(word) + r'\b'
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), len(match.group()), self.keyword_format)

        # Destacar funções built-in
        for builtin in self.builtins:
            pattern = r'\b' + re.escape(builtin) + r'\b'
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), len(match.group()), self.builtin_format)

        # Destacar strings (ordem importante: strings primeiro que comentários)
        string_patterns = [
            (r'""".*?"""', self.string_format),  # Triple quotes
            (r"'''.*?'''", self.string_format),
            (r'"[^"\\]*(?:\\.[^"\\]*)*"', self.string_format),  # Double quotes
            (r"'[^'\\]*(?:\\.[^'\\]*)*'", self.string_format)  # Single quotes
        ]

        for pattern, fmt in string_patterns:
            for match in re.finditer(pattern, text, re.DOTALL):
                self.setFormat(match.start(), len(match.group()), fmt)

        # Destacar comentários
        comment_pattern = r'#.*$'
        for match in re.finditer(comment_pattern, text, re.MULTILINE):
            self.setFormat(match.start(), len(match.group()), self.comment_format)

        # Destacar definições de função
        function_pattern = r'\bdef\s+(\w+)'
        for match in re.finditer(function_pattern, text):
            self.setFormat(match.start(1), len(match.group(1)), self.function_format)

        # Destacar definições de classe
        class_pattern = r'\bclass\s+(\w+)'
        for match in re.finditer(class_pattern, text):
            self.setFormat(match.start(1), len(match.group(1)), self.class_format)


class AutoCompleter:
    """Sistema de autocompletar para Python"""

    def __init__(self):
        self.builtin_functions = [
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr',
            'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'filter',
            'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
            'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max',
            'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord',
            'pow', 'print', 'property', 'range', 'repr', 'reversed', 'round',
            'set', 'setattr', 'slice', 'sorted', 'staticmethod', 'str', 'sum',
            'super', 'tuple', 'type', 'vars', 'zip'
        ]

        self.string_methods = [
            'capitalize', 'casefold', 'center', 'count', 'encode', 'endswith',
            'expandtabs', 'find', 'format', 'format_map', 'index', 'isalnum',
            'isalpha', 'isascii', 'isdecimal', 'isdigit', 'isidentifier',
            'islower', 'isnumeric', 'isprintable', 'isspace', 'istitle',
            'isupper', 'join', 'ljust', 'lower', 'lstrip', 'partition',
            'replace', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit',
            'rstrip', 'split', 'splitlines', 'startswith', 'strip', 'swapcase',
            'title', 'translate', 'upper', 'zfill'
        ]

        self.list_methods = [
            'append', 'clear', 'copy', 'count', 'extend', 'index', 'insert',
            'pop', 'remove', 'reverse', 'sort'
        ]

        self.dict_methods = [
            'clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 'pop',
            'popitem', 'setdefault', 'update', 'values'
        ]

    def get_suggestions(self, text, cursor_pos):
        """Obter sugestões de autocompletar baseado no contexto"""
        if cursor_pos <= 0:
            return []

        # Encontrar a palavra atual
        start = cursor_pos
        while start > 0 and (text[start - 1].isalnum() or text[start - 1] in '._'):
            start -= 1

        current_word = text[start:cursor_pos]

        if not current_word:
            return []

        suggestions = []
        all_suggestions = keyword.kwlist + self.builtin_functions

        # Analisar o contexto para métodos
        if '.' in current_word:
            parts = current_word.split('.')
            if len(parts) >= 2:
                method_part = parts[-1]
                # Adicionar métodos baseado no contexto
                all_suggestions.extend(self.string_methods + self.list_methods + self.dict_methods)
                suggestions = [s for s in all_suggestions if s.startswith(method_part)]
            else:
                suggestions = [s for s in all_suggestions if s.startswith(current_word)]
        else:
            # Extrair definições do arquivo atual
            functions = re.findall(r'def\s+(\w+)', text)
            classes = re.findall(r'class\s+(\w+)', text)
            variables = re.findall(r'^(\w+)\s*=', text, re.MULTILINE)

            all_suggestions.extend(functions + classes + variables)
            suggestions = [s for s in all_suggestions if s.startswith(current_word)]

        return sorted(list(set(suggestions)))


class CodeEditor(QTextEdit):
    """Editor de código com autocompletar"""

    def __init__(self, file_path=None):
        super().__init__()

        self.file_path = file_path

        # Configurar fonte monoespaçada
        font = QFont("Consolas", 11)
        if not font.exactMatch():
            font = QFont("Courier New", 11)
        self.setFont(font)

        # Configurar tab para 4 espaços
        metrics = self.fontMetrics()
        self.setTabStopDistance(4 * metrics.horizontalAdvance(' '))

        # Configurar destacador de sintaxe apenas para arquivos .py
        self.highlighter = None
        if file_path and file_path.endswith('.py'):
            self.highlighter = PythonHighlighter(self.document())

        # Sistema de autocompletar
        self.auto_completer_system = AutoCompleter()
        self.completer = QCompleter()
        self.completer.setModel(QStringListModel())
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)

        # Conectar eventos
        self.textChanged.connect(self.on_text_changed)

        # Pares de caracteres para auto-fechamento
        self.auto_pairs = {
            '(': ')',
            '[': ']',
            '{': '}',
            '"': '"',
            "'": "'"
        }

    def keyPressEvent(self, event: QKeyEvent):
        # Se o completer está visível, deixar ele gerenciar alguns eventos
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Escape,
                               Qt.Key.Key_Tab, Qt.Key.Key_Backtab):
                event.ignore()
                return

        # Verificar se é Ctrl+Space para ativar autocomplete
        if event.key() == Qt.Key.Key_Space and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.show_suggestions()
            return

        # Auto-completar pares de caracteres
        if event.text() in self.auto_pairs:
            self.handle_auto_pair(event.text())
            return

        # Verificar se está fechando um par automaticamente
        if event.text() in [')', ']', '}', '"', "'"]:
            if self.handle_closing_pair(event.text()):
                return

        super().keyPressEvent(event)

        # Atualizar autocomplete após digitar
        if event.text() and event.text().isalnum():
            self.update_autocomplete()

    def handle_auto_pair(self, opening):
        """Gerenciar auto-fechamento de pares"""
        cursor = self.textCursor()
        closing = self.auto_pairs[opening]

        # Casos especiais para aspas
        if opening in ['"', "'"]:
            selected_text = cursor.selectedText()
            if selected_text:
                # Envolver texto selecionado com aspas
                cursor.insertText(opening + selected_text + closing)
                return
            else:
                # Verificar se o caractere seguinte já é a aspa correspondente
                pos = cursor.position()
                text = self.toPlainText()
                if pos < len(text) and text[pos] == opening:
                    # Mover cursor para frente da aspa existente
                    cursor.setPosition(pos + 1)
                    self.setTextCursor(cursor)
                    return

        # Inserir par de caracteres
        cursor.insertText(opening + closing)
        cursor.setPosition(cursor.position() - 1)
        self.setTextCursor(cursor)

    def handle_closing_pair(self, closing):
        """Gerenciar fechamento automático de pares"""
        cursor = self.textCursor()
        pos = cursor.position()
        text = self.toPlainText()

        if pos < len(text) and text[pos] == closing:
            # Pular o caractere de fechamento se já existe
            cursor.setPosition(pos + 1)
            self.setTextCursor(cursor)
            return True
        return False

    def on_text_changed(self):
        """Chamado quando o texto muda"""
        cursor = self.textCursor()
        cursor_pos = cursor.position()
        text = self.toPlainText()

        # Verificar se deve mostrar sugestões após ponto
        if cursor_pos > 0 and cursor_pos <= len(text):
            char_before = text[cursor_pos - 1]
            if char_before == '.':
                self.show_suggestions()

    def get_current_word(self):
        """Obter a palavra atual sob o cursor"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        return cursor.selectedText()

    def get_word_start_position(self):
        """Obter posição do início da palavra atual"""
        cursor = self.textCursor()
        pos = cursor.position()
        text = self.toPlainText()

        start = pos
        while start > 0 and (text[start - 1].isalnum() or text[start - 1] in '._'):
            start -= 1

        return start

    def update_autocomplete(self):
        """Atualizar sugestões de autocomplete durante digitação"""
        cursor = self.textCursor()
        cursor_pos = cursor.position()
        text = self.toPlainText()

        if cursor_pos <= 0:
            return

        # Obter palavra atual
        start_pos = self.get_word_start_position()
        current_word = text[start_pos:cursor_pos]

        if len(current_word) >= 2:  # Mostrar sugestões após 2 caracteres
            suggestions = self.auto_completer_system.get_suggestions(text, cursor_pos)
            if suggestions:
                # Filtrar sugestões que começam com a palavra atual
                filtered_suggestions = [s for s in suggestions if s.startswith(current_word)]
                if filtered_suggestions:
                    self.completer.model().setStringList(filtered_suggestions)

                    # Posicionar o completer
                    cursor_rect = self.cursorRect()
                    cursor_rect.setWidth(self.completer.popup().sizeHintForColumn(0) +
                                         self.completer.popup().verticalScrollBar().sizeHint().width())
                    self.completer.complete(cursor_rect)
                else:
                    self.completer.popup().hide()
            else:
                self.completer.popup().hide()
        else:
            self.completer.popup().hide()

    def show_suggestions(self):
        """Mostrar lista de sugestões"""
        cursor = self.textCursor()
        cursor_pos = cursor.position()
        text = self.toPlainText()

        suggestions = self.auto_completer_system.get_suggestions(text, cursor_pos)

        if suggestions:
            self.completer.model().setStringList(suggestions)

            # Posicionar o completer
            cursor_rect = self.cursorRect()
            cursor_rect.setWidth(self.completer.popup().sizeHintForColumn(0) +
                                 self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cursor_rect)
        else:
            self.completer.popup().hide()

    def insert_completion(self, completion):
        """Inserir o texto de autocompletar"""
        cursor = self.textCursor()

        # Encontrar o início da palavra atual
        start_pos = self.get_word_start_position()
        current_pos = cursor.position()

        # Selecionar a palavra atual e substituir
        cursor.setPosition(start_pos)
        cursor.setPosition(current_pos, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(completion)

        self.setTextCursor(cursor)

    def wheelEvent(self, event):
        """Zoom com Ctrl + Scroll"""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoomIn()
            else:
                self.zoomOut()
        else:
            super().wheelEvent(event)


class FileExplorer(QTreeView):
    """Explorador de arquivos"""

    file_opened = Signal(str)

    def __init__(self):
        super().__init__()

        self.model = QFileSystemModel()
        self.current_path = QDir.currentPath()
        self.model.setRootPath(self.current_path)
        self.setModel(self.model)

        # Configurar visualização
        self.setRootIndex(self.model.index(self.current_path))
        self.hideColumn(1)  # Tamanho
        self.hideColumn(2)  # Tipo
        self.hideColumn(3)  # Data modificação

        # Configurar header
        header = self.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.update_header_title()

        # Conectar eventos
        self.doubleClicked.connect(self.on_double_click)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def update_header_title(self):
        """Atualizar título do header com o diretório atual"""
        dir_name = os.path.basename(self.current_path)
        if not dir_name:
            dir_name = self.current_path
        self.model.setHeaderData(0, Qt.Orientation.Horizontal, dir_name)

    def show_context_menu(self, position):
        """Mostrar menu de contexto"""
        index = self.indexAt(position)
        menu = QMenu(self)

        # Ações do menu
        new_file_action = menu.addAction("Novo Arquivo")
        new_folder_action = menu.addAction("Nova Pasta")

        # Se um item está selecionado, adicionar opção de excluir
        if index.isValid():
            menu.addSeparator()
            delete_action = menu.addAction("Excluir")
            delete_action.triggered.connect(lambda: self.delete_item(index))

        # Conectar ações
        new_file_action.triggered.connect(lambda: self.create_new_file(index))
        new_folder_action.triggered.connect(lambda: self.create_new_folder(index))

        # Mostrar menu
        menu.exec(self.mapToGlobal(position))

    def create_new_file(self, index=None):
        """Criar novo arquivo"""
        # Determinar diretório base
        if index and index.isValid():
            path = self.model.filePath(index)
            if self.model.isDir(index):
                base_dir = path
            else:
                base_dir = os.path.dirname(path)
        else:
            base_dir = self.current_path

        file_name, ok = QInputDialog.getText(self, 'Novo Arquivo', 'Nome do arquivo:')
        if ok and file_name.strip():
            if not file_name.endswith('.py'):
                file_name += '.py'

            file_path = os.path.join(base_dir, file_name)
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('# Novo arquivo Python\n')
                self.file_opened.emit(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível criar o arquivo:\n{str(e)}")

    def create_new_folder(self, index=None):
        """Criar nova pasta"""
        # Determinar diretório base
        if index and index.isValid():
            path = self.model.filePath(index)
            if self.model.isDir(index):
                base_dir = path
            else:
                base_dir = os.path.dirname(path)
        else:
            base_dir = self.current_path

        folder_name, ok = QInputDialog.getText(self, 'Nova Pasta', 'Nome da pasta:')
        if ok and folder_name.strip():
            folder_path = os.path.join(base_dir, folder_name)
            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível criar a pasta:\n{str(e)}")

    def delete_item(self, index):
        """Excluir arquivo ou pasta"""
        if not index.isValid():
            return

        item_path = self.model.filePath(index)
        item_name = os.path.basename(item_path)

        # Confirmar exclusão
        reply = QMessageBox.question(
            self,
            'Confirmar Exclusão',
            f'Tem certeza que deseja excluir "{item_name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.model.isDir(index):
                    # Excluir diretório
                    shutil.rmtree(item_path)
                else:
                    # Excluir arquivo
                    os.remove(item_path)

            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível excluir:\n{str(e)}")

    def on_double_click(self, index):
        """Abrir arquivo ao duplo clique"""
        file_path = self.model.filePath(index)
        if os.path.isfile(file_path):
            self.file_opened.emit(file_path)

    def set_root_path(self, path):
        """Definir diretório raiz"""
        self.current_path = path
        self.model.setRootPath(path)
        self.setRootIndex(self.model.index(path))
        self.update_header_title()


class CodeEditorMainWindow(QMainWindow):
    """Janela principal do editor de código"""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Editor de Código Python")
        self.setGeometry(100, 100, 1200, 800)

        # Dicionário para rastrear arquivos abertos
        self.open_files = {}

        # Configurar interface
        self.setup_ui()
        self.create_menu()

        # Barra de status
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Pronto")

    def setup_ui(self):
        """Configurar interface do usuário"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Explorador de arquivos (esquerda)
        self.file_explorer = FileExplorer()
        self.file_explorer.file_opened.connect(self.open_file)
        splitter.addWidget(self.file_explorer)

        # Widget direito (abas + editor)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Sistema de abas
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        right_layout.addWidget(self.tab_widget)

        splitter.addWidget(right_widget)
        splitter.setSizes([300, 900])

    def create_menu(self):
        """Criar barra de menu"""
        menubar = self.menuBar()

        # Menu Arquivo
        file_menu = menubar.addMenu('Arquivo')

        open_action = QAction('Abrir...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        save_action = QAction('Salvar', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_current_file)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        open_folder_action = QAction('Abrir Pasta...', self)
        open_folder_action.triggered.connect(self.open_folder_dialog)
        file_menu.addAction(open_folder_action)

        # Menu Editar
        edit_menu = menubar.addMenu('Editar')

        autocomplete_action = QAction('Autocompletar', self)
        autocomplete_action.setShortcut('Ctrl+Space')
        autocomplete_action.triggered.connect(self.trigger_autocomplete)
        edit_menu.addAction(autocomplete_action)

    def open_file_dialog(self):
        """Abrir diálogo para selecionar arquivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Arquivo",
            "",
            "Arquivos Python (*.py);;Todos os arquivos (*)"
        )
        if file_path:
            self.open_file(file_path)

    def open_folder_dialog(self):
        """Abrir diálogo para selecionar pasta"""
        folder_path = QFileDialog.getExistingDirectory(self, "Abrir Pasta")
        if folder_path:
            self.file_explorer.set_root_path(folder_path)

    def open_file(self, file_path):
        """Abrir arquivo em nova aba"""
        # Verificar se o arquivo já está aberto
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabToolTip(i) == file_path:
                self.tab_widget.setCurrentIndex(i)
                return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Criar novo editor
            editor = CodeEditor(file_path)
            editor.setPlainText(content)

            # Adicionar aba
            file_name = os.path.basename(file_path)
            tab_index = self.tab_widget.addTab(editor, file_name)
            self.tab_widget.setTabToolTip(tab_index, file_path)
            self.tab_widget.setCurrentIndex(tab_index)

            # Rastrear arquivo aberto
            self.open_files[tab_index] = file_path

            self.status_bar.showMessage(f"Arquivo aberto: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir o arquivo:\n{str(e)}")

    def close_tab(self, index):
        """Fechar aba"""
        if index in self.open_files:
            del self.open_files[index]

        self.tab_widget.removeTab(index)

        # Reindexar arquivos abertos
        new_open_files = {}
        for i in range(self.tab_widget.count()):
            tooltip = self.tab_widget.tabToolTip(i)
            if tooltip:
                new_open_files[i] = tooltip

        self.open_files = new_open_files

    def save_current_file(self):
        """Salvar arquivo atual"""
        current_index = self.tab_widget.currentIndex()
        if current_index == -1:
            return

        current_editor = self.tab_widget.currentWidget()
        if not isinstance(current_editor, CodeEditor):
            return

        file_path = self.tab_widget.tabToolTip(current_index)
        if not file_path:
            # Arquivo novo - pedir para salvar como
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar Como",
                "",
                "Arquivos Python (*.py);;Todos os arquivos (*)"
            )
            if not file_path:
                return

            self.tab_widget.setTabToolTip(current_index, file_path)
            self.tab_widget.setTabText(current_index, os.path.basename(file_path))
            self.open_files[current_index] = file_path

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(current_editor.toPlainText())

            self.status_bar.showMessage(f"Arquivo salvo: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar o arquivo:\n{str(e)}")

    def trigger_autocomplete(self):
        """Disparar autocompletar manualmente"""
        current_editor = self.tab_widget.currentWidget()
        if isinstance(current_editor, CodeEditor):
            current_editor.show_suggestions()


def main():
    app = QApplication(sys.argv)

    # Configurar estilo
    app.setStyle('Fusion')

    window = CodeEditorMainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()