from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGraphicsView,
                               QGraphicsScene, QGraphicsItem, QTextEdit, QListWidget, QListWidgetItem, QInputDialog, QMenu, QTabWidget)
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
        "WhileLoop": QColor("#f7768e"),
        "Addition": QColor("#73daca"),
        "Subtraction": QColor("#ff7a93"),
        "Multiplication": QColor("#b4f9f0"),
        "Division": QColor("#ffa656"),
        "Rounding": QColor("#c0caf5"),
        "Modulo": QColor("#ff9e64"),
        "Exponentiation": QColor("#73daca"),
        "SquareRoot": QColor("#7dcfff"),
        "AbsoluteValue": QColor("#9ece6a"),
        "MinMax": QColor("#ff9e64"),
        "Function": QColor("#bb9af7"),
        "Return": QColor("#f7768e"),
        "Break": QColor("#ff7a93"),
        "Continue": QColor("#ffa656"),
        "ListCreate": QColor("#b4f9f0"),
        "StringConvert": QColor("#73daca"),
        "IntConvert": QColor("#7dcfff"),
        "FloatConvert": QColor("#9ece6a"),
        "TypeCheck": QColor("#ff7a93"),
        "StringConcat": QColor("#bb9af7"),
        "StringSplit": QColor("#b4f9f0"),
        "StringFormat": QColor("#7aa2f7")
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
        initial_texts = {
            "Print": "Print: 'Hello World'",
            "Variable": "Variable: x = 10",
            "Loop": "Loop: range(5)",
            "Condition": "Condition: x > 5",
            "WhileLoop": "WhileLoop: x < 10",
            "Addition": "Addition: x, y",
            "Subtraction": "Subtraction: x, y",
            "Multiplication": "Multiplication: x, y",
            "Division": "Division: x, y",
            "Rounding": "Rounding: x, 2",
            "Modulo": "Modulo: x, y",
            "Exponentiation": "Exponentiation: result, x, y",
            "SquareRoot": "SquareRoot: result, x",
            "AbsoluteValue": "AbsoluteValue: result, x",
            "MinMax": "MinMax: result, x, y",
            "Function": "Function: my_function(param1, param2)",
            "Return": "Return: value",
            "Break": "Break: in_loop",
            "Continue": "Continue: in_loop",
            "ListCreate": "ListCreate: my_list, [1, 2, 3]",
            "DictCreate": "DictCreate: my_dict, {'key': 'value'}",
            "ListAppend": "ListAppend: my_list, new_item",
            "Comprehension": "Comprehension: result, [x for x in range(10)]",
            "StringConvert": "StringConvert: result, x",
            "IntConvert": "IntConvert: result, x",
            "FloatConvert": "FloatConvert: result, x",
            "TypeCheck": "TypeCheck: result, x",
            "StringConcat": "StringConcat: result, str1, str2",
            "StringSplit": "StringSplit: result, string, delimiter",
            "StringFormat": "StringFormat: result, template, values",
            "StringLength": "StringLength: result, string"
        }
        return initial_texts.get(self.block_type, self.block_type)

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
        edit_prompts = {
            "Print": ("Edit Print Block", "Enter text to print:", "Hello World", False),
            "Variable": ("Edit Variable Block", "Enter variable and value (e.g., x = 10):", "x = 10", False),
            "Loop": ("Edit Loop Block", "Enter range (e.g., 5):", "5", False),
            "Condition": ("Edit Condition Block", "Enter condition (e.g., x > 5):", "x > 5", False),
            "WhileLoop": ("Edit While Loop Block", "Enter while condition (e.g., x < 10):", "x < 10", False),
            "Addition": ("Edit Addition Block", "Enter first value/variable:", "x", True),
            "Subtraction": ("Edit Subtraction Block", "Enter first value/variable:", "x", True),
            "Multiplication": ("Edit Multiplication Block", "Enter first value/variable:", "x", True),
            "Division": ("Edit Division Block", "Enter first value/variable:", "x", True),
            "Rounding": ("Edit Rounding Block", "Enter variable to round:", "x", True),
            "Modulo": ("Edit Modulo Block", "Enter first value/variable:", "x", True),
            "Exponentiation": ("Edit Exponentiation Block", "Enter first value/variable:", "x", True),
            "Square Root": ("Edit Square Root Block", "Enter variable to square root:", "x", True),
            "Absolute Value": ("Edit Absolute Value Block", "Enter variable:", "x", True),
            "Min/Max": ("Edit Min/Max Block", "Enter first value/variable:", "x", True),
            "Function": ("Edit Function Block", "Enter function definition:", "def my_function(param1, param2):", False),
            "Return": ("Edit Return Block", "Enter return value:", "result", False),
            "Break": ("Edit Break Block", "Enter context:", "", False),
            "Continue": ("Edit Continue Block", "Enter context:", "", False),
            "ListCreate": ("Edit List Creation Block", "Enter list values:", "[1, 2, 3]", True),
            "StringConvert": ("Edit String Conversion Block", "Enter variable to convert:", "x", True),
            "IntConvert": ("Edit Integer Conversion Block", "Enter variable to convert:", "x", True),
            "FloatConvert": ("Edit Float Conversion Block", "Enter variable to convert:", "x", True),
            "TypeCheck": ("Edit Type Check Block", "Enter variable to check:", "x", True),
            "StringConcat": ("Edit String Concatenation Block", "Enter first string:", "str1", True),
            "StringSplit": ("Edit String Split Block", "Enter string to split:", "string", True),
            "StringFormat": ("Edit String Format Block", "Enter format template:", "'{} {}'", True)
        }

        title, prompt1, default1, needs_var = edit_prompts.get(self.block_type, ("Edit Block", "Enter first value:", "", False))
        
        if needs_var:
            var_title = f"Edit {self.block_type} Result Variable"
            var_prompt = "Enter the variable to save result:"
            var_default = "result"
            var_name, var_ok = QInputDialog.getText(None, var_title, var_prompt, text=var_default)
            
            if not var_ok:
                return

            first_title = title
            first_prompt = prompt1
            first_value, first_ok = QInputDialog.getText(None, first_title, first_prompt, text=default1)
            
            if not first_ok:
                return

            second_prompt = "Enter second value/variable:" if self.block_type != "Rounding" else "Enter decimal places:"
            second_default = "y" if self.block_type != "Rounding" else "2"
            second_value, second_ok = QInputDialog.getText(None, title, second_prompt, text=second_default)
            
            if second_ok:
                self.text = f"{self.block_type}: {var_name}, {first_value}, {second_value}"
        else:
            new_text, ok = QInputDialog.getText(None, title, prompt1, text=default1)
            
            if ok:
                self.text = f"{self.block_type}: {new_text}"
        
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
        block_tabs = QTabWidget()
        block_categories = {
            "Basic": [
                "Print", "Variable", "Loop",
                "Condition", "While Loop"
            ],
            "Arithmetic": [
                "Addition", "Subtraction",
                "Multiplication", "Division",
                "Rounding", "Modulo"
            ],
            "Computational": [
                "Exponentiation", "Square Root",
                "Absolute Value", "Min/Max"
            ],
            "Control Flow": [
                "Function", "Return",
                "Break", "Continue"
            ],
            "Data Structures": [
                "List Create"
            ],
            "Type Conversion": [
                "String Convert", "Int Convert",
                "Float Convert", "Type Check"
            ],
            "String Manipulation": [
                "String Concat", "String Split",
                "String Format"
            ]
        }
        for category, blocks in block_categories.items():
            block_list = QListWidget()
            for block_name in blocks:
                item = QListWidgetItem(block_name)
                block_list.addItem(item)
            block_list.itemDoubleClicked.connect(self.create_block)
            block_tabs.addTab(block_list, category)
    
        sidebar_layout.addWidget(block_tabs)
        
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

        def safe_split(text):
            parts = text.split(': ')
            return parts[-1].split(',') if len(parts) > 1 else []

        parts = safe_split(block.text)
        var_name = parts[0].strip() if len(parts) > 0 else ""
        first_val = parts[1].strip() if len(parts) > 1 else ""
        second_val = parts[2].strip() if len(parts) > 2 else ""

        block_type_mapping = {
            "Print": f"{indent}print({block.text.split(': ')[-1]})",
            "Variable": f"{indent}{block.text.split(': ')[-1]}",
            "Loop": f"{indent}for i in {block.text.split(': ')[-1]}:",
            "Condition": f"{indent}if {block.text.split(': ')[-1]}:",
            "WhileLoop": f"{indent}while {block.text.split(': ')[-1]}:",
            "Exponentiation": f"{indent}{var_name} = {first_val} ** {second_val}",
            "SquareRoot": f"{indent}{var_name} = {first_val} ** 0.5",
            "AbsoluteValue": f"{indent}{var_name} = abs({first_val})",
            "MinMax": f"{indent}{var_name} = max({first_val}, {second_val})",
            "Function": f"{indent}{block.text.split(': ')[-1]}:",
            "Return": f"{indent}return {block.text.split(': ')[-1]}",
            "Break": f"{indent}break",
            "Continue": f"{indent}continue",
            "ListCreate": f"{indent}{var_name} = {first_val}",
            "DictCreate": f"{indent}{var_name} = {first_val}",
            "ListAppend": f"{indent}{first_val}.append({second_val})",
            "Comprehension": f"{indent}{var_name} = {first_val}",
            "StringConvert": f"{indent}{var_name} = str({first_val})",
            "IntConvert": f"{indent}{var_name} = int({first_val})",
            "FloatConvert": f"{indent}{var_name} = float({first_val})",
            "TypeCheck": f"{indent}{var_name} = type({first_val})",
            "StringConcat": f"{indent}{var_name} = {first_val} + {second_val}",
            "StringSplit": f"{indent}{var_name} = {first_val}.split({second_val})",
            "StringFormat": f"{indent}{var_name} = {first_val}.format({second_val})",
            "StringLength": f"{indent}{var_name} = len({first_val})"
        }

        two_input_ops = {
            "Addition": " + ",
            "Subtraction": " - ",
            "Multiplication": " * ",
            "Division": " / ",
            "Modulo": " % "
        }

        if block.block_type in two_input_ops:
            op_line = f"{indent}{var_name} = {first_val}{two_input_ops[block.block_type]}{second_val}"
            block_type_mapping[block.block_type] = op_line

        if block.block_type == "Rounding":
            block_type_mapping["Rounding"] = f"{indent}{var_name} = round({first_val}, {second_val})"

        code.append(block_type_mapping.get(block.block_type, ""))

        if block.block_type in ["Loop", "Condition", "WhileLoop"]:
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