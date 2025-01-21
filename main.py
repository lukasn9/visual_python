from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGraphicsView, 
                               QGraphicsScene, QGraphicsItem, QFileDialog, QTextEdit, QListWidget, QListWidgetItem, QLineEdit, QInputDialog)
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainterPath, QColor
import sys

class Block(QGraphicsItem):
    COLOR_MAP = {
        "Print": QColor(173, 216, 230),
        "Variable": QColor(144, 238, 144),
        "Loop": QColor(255, 228, 181),
        "Condition": QColor(250, 128, 114),
    }

    def __init__(self, block_type="Block", parent=None):
        super().__init__(parent)
        self.block_type = block_type
        self.text = self.get_initial_text()
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        self.rect = QRectF(0, 0, 150, 50)

    def get_initial_text(self):
        if self.block_type == "Print":
            return "Print: 'Hello'"
        elif self.block_type == "Variable":
            return "Variable: x = 10"
        elif self.block_type == "Loop":
            return "Loop: range(5)"
        elif self.block_type == "Condition":
            return "Condition: x > 5"
        return self.block_type

    def boundingRect(self) -> QRectF:
        return self.rect

    def paint(self, painter, option, widget=None):
        color = self.COLOR_MAP.get(self.block_type, QColor(211, 211, 211))
        painter.setBrush(color)
        painter.drawRoundedRect(self.rect, 5, 5)
        painter.drawText(self.rect, Qt.AlignCenter, self.text)

    def edit_block(self):
        if self.block_type == "Print":
            new_text, ok = QInputDialog.getText(None, "Edit Print Block", "Enter text to print:", text="Hello")
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

class VisualLang(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisualLang IDE")
        self.setGeometry(100, 100, 1200, 800)
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        sidebar_layout = QVBoxLayout()
        block_list = QListWidget()
        for block_name in ["Print", "Variable", "Loop", "Condition"]:
            item = QListWidgetItem(block_name)
            block_list.addItem(item)
        block_list.itemDoubleClicked.connect(self.create_block_from_sidebar)
        sidebar_layout.addWidget(QLabel("Blocks"))
        sidebar_layout.addWidget(block_list)

        main_layout.addLayout(sidebar_layout)

        canvas_layout = QVBoxLayout()
        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene(0, 0, 2000, 1500)
        self.graphics_view.setScene(self.scene)
        canvas_layout.addWidget(self.graphics_view)

        generate_code_button = QPushButton("Generate Python Code")
        generate_code_button.clicked.connect(self.generate_code)
        canvas_layout.addWidget(generate_code_button)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        canvas_layout.addWidget(self.output_text)

        main_layout.addLayout(canvas_layout)

    def create_block_from_sidebar(self, item):
        block_type = item.text()
        block = Block(block_type)
        block.setFlag(QGraphicsItem.ItemIsFocusable)
        block.setAcceptedMouseButtons(Qt.LeftButton)
        self.scene.addItem(block)
        block.setPos(50, 50)
        block.mouseDoubleClickEvent = lambda event: block.edit_block()

    def generate_code(self):
        blocks = sorted(self.scene.items(), key=lambda b: b.pos().y())
        code = []
        for block in blocks:
            if isinstance(block, Block):
                if block.block_type == "Print":
                    content = block.text.split(": ")[-1]
                    code.append(f"print({content})")
                elif block.block_type == "Variable":
                    content = block.text.split(": ")[-1]
                    code.append(content)
                elif block.block_type == "Loop":
                    content = block.text.split(": ")[-1]
                    code.append(f"for i in {content}:\n    print(i)")
                elif block.block_type == "Condition":
                    content = block.text.split(": ")[-1]
                    code.append(f"if {content}:\n    print('Condition met')")
        self.output_text.setText("\n".join(code))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VisualLang()
    window.show()
    sys.exit(app.exec())
