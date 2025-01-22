from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGraphicsView,
                               QGraphicsScene, QGraphicsItem, QTextEdit, QListWidget, QListWidgetItem, QInputDialog, QMenu)
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPen
import sys
import io
from contextlib import redirect_stdout
import traceback

COLORS = {
    "bg_primary": "#1a1b26",
    "bg_secondary": "#24283b",
    "bg_tertiary": "#2f334d",
    "accent": "#7aa2f7",
    "text_primary": "#c0caf5",
    "text_secondary": "#a9b1d6",
    "error": "#f7768e",
    "success": "#9ece6a",
    "block_colors": {
        "Print": QColor("#bb9af7"),
        "Variable": QColor("#7dcfff"),
        "Loop": QColor("#ff9e64"),
        "Condition": QColor("#9ece6a"),
    }
}

class Block(QGraphicsItem):
    COLOR_MAP = COLORS["block_colors"]
    VERTICAL_SPACING = 60
    VERTICAL_TOLERANCE = 20
    INDENT_THRESHOLD = 20

    def __init__(self, block_type="Block", parent=None):
        super().__init__(parent)
        self.block_type = block_type
        self.text = self.get_initial_text()
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.rect = QRectF(0, 0, 160, 45)
        self.nested_blocks = []
        self.parent_block = None

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            menu = QMenu()
            delete_action = menu.addAction("Delete Block")

            scene_pos = event.scenePos()
            view = self.scene().views()[0]
            screen_pos = view.mapToGlobal(view.mapFromScene(scene_pos))

            action = menu.exec(screen_pos)
            if action == delete_action:
                for nested in self.nested_blocks:
                    nested.scene().removeItem(nested)
                if self.parent_block:
                    self.parent_block.nested_blocks.remove(self)
                self.scene().removeItem(self)
        else:
            super().mousePressEvent(event)

    def get_initial_text(self):
        if self.block_type == "Print":
            return "Print: 'Hello World'"
        elif self.block_type == "Variable":
            return "Variable: x = 10"
        elif self.block_type == "Loop":
            return "Loop: range(5)"
        elif self.block_type == "Condition":
            return "Condition: x > 5"
        return self.block_type

    def boundingRect(self) -> QRectF:
        return self.rect.adjusted(-5, -5, 5, 5)

    def paint(self, painter, option, widget=None):
        color = self.COLOR_MAP.get(self.block_type, QColor(211, 211, 211))
        painter.setBrush(color)
        painter.setPen(QPen(Qt.black, 0))
        painter.drawRoundedRect(self.rect, 10, 10)

        painter.setPen(QPen(QColor("#1a1b26")))
        font = painter.font()
        font.setPointSize(10)
        font.setFamily("Segoe UI")
        painter.setFont(font)
        painter.drawText(self.rect, Qt.AlignCenter, self.text)

    def edit_block(self):
        if self.block_type == "Print":
            new_text, ok = QInputDialog.getText(None, "Edit Print Block", "Enter text to print:", text="Hello World")
            if ok:
                self.text = f"Print: '{new_text}'"
        elif self.block_type == "Variable":
            new_var, ok = QInputDialog.getText(None, "Edit Variable Block", "Enter variable and value (e.g., x = 10):", text="x = 10")
            if ok:
                self.text = f"Variable: {new_var}"
        elif self.block_type == "Loop":
            new_range, ok = QInputDialog.getText(None, "Edit Loop Block", "Enter range (e.g., 5):", text="5")
            if ok:
                self.text = f"Loop: range({new_range})"
        elif self.block_type == "Condition":
            new_condition, ok = QInputDialog.getText(None, "Edit Condition Block", "Enter condition (e.g., x > 5):", text="x > 5")
            if ok:
                self.text = f"Condition: {new_condition}"
        self.update()

class Terminal(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11pt;
            }}
        """)
        self.clear_terminal()

    def clear_terminal(self):
        self.clear()
        self.append("=== Terminal Output ===\n")

    def append_output(self, text, error=False):
        color = COLORS["error"] if error else COLORS["text_primary"]
        self.append(f'<span style="color: {color};">{text}</span>')

class VisualLang(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisualLang IDE")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['bg_primary']};
            }}
            QWidget {{
                background-color: {COLORS['bg_primary']};
                color: {COLORS['text_primary']};
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_primary']};
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['text_primary']};
            }}
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 11pt;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            QListWidget {{
                background-color: {COLORS['bg_secondary']};
                border: none;
                border-radius: 8px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                margin: 2px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['accent']};
                color: {COLORS['bg_primary']};
            }}
            QGraphicsView {{
                background-color: {COLORS['bg_secondary']};
                border: none;
                border-radius: 8px;
                margin: 5px;
            }}
        """)
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_widget.setLayout(main_layout)

        sidebar_layout = QVBoxLayout()
        block_list = QListWidget()
        for block_name in ["Print", "Variable", "Loop", "Condition"]:
            item = QListWidgetItem(block_name)
            block_list.addItem(item)
        block_list.itemDoubleClicked.connect(self.create_block)
        
        sidebar_label = QLabel("Blocks")
        sidebar_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(sidebar_label)
        sidebar_layout.addWidget(block_list)
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setFixedWidth(200)
        main_layout.addWidget(sidebar_widget)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene(0, 0, 2000, 1500)
        self.scene.setBackgroundBrush(QColor(COLORS['bg_secondary']))
        self.graphics_view.setScene(self.scene)
        right_layout.addWidget(self.graphics_view)

        bottom_panel = QHBoxLayout()
        bottom_panel.setSpacing(10)

        code_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        buttons = [
            ("Generate Python Code", self.generate_code),
            ("Run Code", self.gen_run_code),
            ("Clear Terminal", self.clear_terminal)
        ]
        
        for text, handler in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            button_layout.addWidget(btn)
        
        code_layout.addLayout(button_layout)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11pt;
            }}
        """)
        
        code_label = QLabel("Generated Code")
        code_label.setAlignment(Qt.AlignLeft)
        code_layout.addWidget(code_label)
        code_layout.addWidget(self.output_text)

        terminal_layout = QVBoxLayout()
        terminal_label = QLabel("Terminal Output")
        terminal_label.setAlignment(Qt.AlignLeft)
        terminal_layout.addWidget(terminal_label)
        self.terminal = Terminal()
        terminal_layout.addWidget(self.terminal)

        bottom_panel.addLayout(code_layout)
        bottom_panel.addLayout(terminal_layout)
        
        right_layout.addLayout(bottom_panel)
        main_layout.addLayout(right_layout)

    def clear_terminal(self):
        self.terminal.clear_terminal()

    def gen_run_code(self):
        self.generate_code()
        self.run_code()

    def run_code(self):
        code = self.output_text.toPlainText()
        if not code.strip():
            self.terminal.append_output("No code to run!", error=True)
            return

        stdout = io.StringIO()
        try:
            with redirect_stdout(stdout):
                exec(code)
            output = stdout.getvalue()
            if output:
                self.terminal.append_output(output)
            else:
                self.terminal.append_output("Code executed successfully with no output.")
        except Exception as e:
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            self.terminal.append_output(error_msg, error=True)
        finally:
            stdout.close()

    def create_block(self, item):
        block_type = item.text()
        block = Block(block_type)
        block.setFlag(QGraphicsItem.ItemIsFocusable)
        block.setAcceptedMouseButtons(Qt.LeftButton)
        self.scene.addItem(block)
        block.setPos(50, 50)
        block.mouseDoubleClickEvent = lambda event: block.edit_block()

    def block_rel(self):
        blocks = [item for item in self.scene.items() if isinstance(item, Block)]

        for block in blocks:
            block.nested_blocks = []
            block.parent_block = None

        vertical_groups = {}
        for block in blocks:
            y_pos = block.pos().y()
            found_group = False
            for group_y in vertical_groups.keys():
                if abs(y_pos - group_y) <= Block.VERTICAL_TOLERANCE:
                    vertical_groups[group_y].append(block)
                    found_group = True
                    break
            if not found_group:
                vertical_groups[y_pos] = [block]

        sorted_groups = sorted(vertical_groups.items(), key=lambda x: x[0])

        for i, (y_pos, group) in enumerate(sorted_groups):
            group.sort(key=lambda b: b.pos().x())

            if i > 0:
                prev_group = sorted_groups[i-1][1]
                if prev_group:
                    leftmost = min(group, key=lambda b: b.pos().x())
                    if abs(leftmost.pos().x() - prev_group[0].pos().x()) < Block.INDENT_THRESHOLD:
                        continue

            for j, block in enumerate(group):
                if j > 0:
                    prev_block = group[j-1]
                    if (block.pos().x() > prev_block.pos().x() + Block.INDENT_THRESHOLD and
                        prev_block.block_type in ["Loop", "Condition"]):
                        block.parent_block = prev_block
                        prev_block.nested_blocks.append(block)

        return blocks

    def generate_code(self):
        blocks = self.block_rel()

        root_blocks = [block for block in blocks if block.parent_block is None]
        root_blocks.sort(key=lambda b: b.pos().y())
        
        code = []
        for block in root_blocks:
            code.append(self.generate_block_code(block, 0))
            
        self.output_text.setText("\n".join(filter(None, code)))

    def generate_block_code(self, block, indent_level):
        indent = "    " * indent_level
        code = []

        if block.block_type == "Print":
            content = block.text.split(": ")[-1]
            code.append(f"{indent}print({content})")
        elif block.block_type == "Variable":
            code.append(f"{indent}{block.text.split(': ')[-1]}")
        elif block.block_type in ["Loop", "Condition"]:
            header = (f"{indent}for i in {block.text.split(': ')[-1]}:"
                     if block.block_type == "Loop"
                     else f"{indent}if {block.text.split(': ')[-1]}:")
            code.append(header)

            nested_blocks = sorted(block.nested_blocks, key=lambda b: b.pos().y())
            if nested_blocks:
                for nested in nested_blocks:
                    code.append(self.generate_block_code(nested, indent_level + 1))
            else:
                code.append(f"{indent}    pass")

        next_vertical = next((b for b in self.scene.items()
                            if isinstance(b, Block) and 
                            abs(b.pos().y() - (block.pos().y() + Block.VERTICAL_SPACING)) < Block.VERTICAL_TOLERANCE and
                            abs(b.pos().x() - block.pos().x()) < Block.INDENT_THRESHOLD and 
                            b.parent_block is None), None)
        
        if next_vertical:
            code.append(self.generate_block_code(next_vertical, indent_level))

        return "\n".join(filter(None, code))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VisualLang()
    window.show()
    sys.exit(app.exec())