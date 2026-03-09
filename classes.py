from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QLabel, QGridLayout, QPushButton
from PySide6.QtCore import Qt, Slot
from variables import TEXT_MARGIN, MAIN_FONT_SIZE, MINIMUN_WIDTH

class Display(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_style()


    def set_style(self):
        margins = [TEXT_MARGIN for _ in range(4)] # porque é necessário passar 4 parâmetros: left, top, right, bottom. Então essa list comprehension passa o TEXT_MARGIN para os 4
        self.setStyleSheet(f'font-size: {MAIN_FONT_SIZE}px;')
        # self.setMinimumHeight(MAIN_FONT_SIZE * 2) # Comentei porque aparentemente é desnecessário - provavelmente por já possui margem superior e inferior através do setTextMargins
        self.setMinimumWidth(MINIMUN_WIDTH)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setTextMargins(*margins)



class History(QLabel):
    def __init__(self, text): # Olhar definitions para ver parâmetros direitinho. colocar *args e **kwargs no lugar text seria mais seguro
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignRight) # fiz direto sem usar um metodo, como o config_style usado no Display
        self.setStyleSheet('font-size: 15px;')



class Window(QMainWindow):
    def __init__(self, display: Display, history: History, parent: QWidget | None = None, *args, **kwargs) -> None:
        super().__init__(parent, *args, **kwargs)

        # Configurando o layout básico:
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)

        # Título da janela
        self.setWindowTitle('Calculadora')

        self.display = display
        self.history = history

        self.first_number = None
        self.second_number = None
        self.result = None
        self.operator = None
        self._equation = ''


    def adjust_fixed_size(self):
        # Última coisa a ser feita
        self.adjustSize() # para que a janela se ajuste ao tamanho necessário de acordo com o que tem nela. Não era necessário, já estava indo automaticamente
        self.setFixedSize(self.width(), self.height()) # Para que o usuário não consiga alterar as dimensões da janela ou maximizá-la


    def add_widget_to_main_layout(self, widget: QWidget):
        self.main_layout.addWidget(widget)

    
    @property
    def equation(self):
        return self._equation
    

    @equation.setter
    def equation(self, equation):
        self._equation = equation
        self.history.setText(equation)



class Button(QPushButton):
    def __init__(self, grid, window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = self.font()
        font.setPixelSize(MAIN_FONT_SIZE)
        self.setFont(font)
        self.setMinimumSize(75, 75)
        
        self.grid = grid
        self.win = window
        self._special_type = None
       

    def set_special_button(self, button_text):
        self.setProperty('css_class', 'special_button')

        if button_text in '+-/*^':
            self._special_type = 'operator'
        elif button_text in '◀':
            self._special_type = 'del'
        elif button_text in 'C':
            self._special_type = 'reset'
        elif button_text in '=':
            self._special_type = 'equal'
        else:
            print('PEGAR ERRO')


    def connect_button_clicked(self):
        if not self._special_type:
            slot_method = self.get_number
            self.clicked.connect(slot_method)
        if self._special_type == 'operator':
            slot_method = self.get_operator
            self.clicked.connect(slot_method)
        if self._special_type == 'op_pow':
            slot_method = self.get_operator
            self.clicked.connect(slot_method)
        if self._special_type == 'equal':
            slot_method = self.get_equal
            self.clicked.connect(slot_method)
        if self._special_type == 'reset':
            slot_method = self.get_reset
            self.clicked.connect(slot_method)
        if self._special_type == 'del':
            slot_method = self.get_delete
            self.clicked.connect(slot_method)
    

    def get_number(self):
        if self.text() == '🐍':
            self._didodev()

        if self.win.result:
            self._result_to_first_number()
        
        if not self.win.operator:
            try:
                button_text = self.text()
                input = self.win.display.text() + button_text
                self.win.first_number = float(input)
                self.win.display.insert(button_text)
                self.win.equation = f'{self.win.first_number}'
            except Exception as error:
                print(error)
        
        else:
            try:
                button_text = self.text()
                input_test = self.win.display.text() + button_text
                self.win.second_number = float(input_test)
                self.win.display.insert(button_text)
                self.win.equation = f'{self.win.first_number} {self.win.operator} {self.win.second_number}'
            except Exception as error:
                print(error)


    def get_operator(self):
        if self.win.result:
            self._result_to_first_number()

        if self.win.first_number and not self.win.operator:
            button_text = self.text()
            self.win.display.clear()
            self.win.operator = button_text
            self.win.equation = f'{self.win.first_number} {self.win.operator} '

    
    def get_equal(self):
        if self.win.second_number and '=' not in self.win.equation:
            try:
                if self.win.operator == '^':
                    self.win.operator = '**'
                    self.win.equation = f'{self.win.first_number} {self.win.operator} {self.win.second_number}'
                result = eval(self.grid.window.equation)
                if self.win.operator == '**':
                    self.win.operator = '^'
                    self.win.equation = f'{self.win.first_number} {self.win.operator} {self.win.second_number}'
                self.win.result = (result)
                self.win.equation += f' = {self.win.result}'
                self.win.display.setText(str(self.win.result))

            except Exception as error:
                self.win.display.setText('CONTA INVÁLIDA')
                print(error)
    

    def get_reset(self):
        self.win.display.clear()
        self.win.equation = ''
        self.win.first_number = None
        self.win.second_number = None
        self.win.operator = None


    def get_delete(self): # DÁ ERRO QUANDO APERTA APÓS UM OPERATOR, AJUSTAR
        self.win.display.backspace()
        if self.win.result:
            self.win.result = self.win.display.text()
            self._result_to_first_number()
        if self.win.second_number:
            self.win.second_number = self.win.display.text()
            self.win.equation = f'{self.win.first_number} {self.win.operator} {self.win.second_number}'
        if not self.win.second_number:
            self.win.first_number = self.win.display.text()
            self.win.equation = f'{self.win.first_number}'

    
    def _result_to_first_number(self):
        self.win.first_number = self.win.result
        self.win.second_number = None
        self.win.operator = None
        self.win.equation = ''
        self.win.result = None

    def _didodev(self):
        self.get_reset()
        self.win.display.setText('🐍 DidoDevFS 🐍')


class ButtonsGrid(QGridLayout):
    def __init__(self, window, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.window = window

        self._grid_mask = [
            ['*', '/', '◀','C'],
            ['7', '8', '9','^'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['🐍', '0', '.', '='],
        ]
        self._add_mask_to_grid()

    def _add_mask_to_grid(self): # Prof usou expressão regular (aula 357)
        window = self.window
        for i, mask_list in enumerate(self._grid_mask):
            for j, button_text in enumerate(mask_list):
                button = Button(self, window, button_text)
                self.addWidget(button, i, j)
                if button_text in '*/-+^=C◀':
                    button.set_special_button(button_text)

                button.connect_button_clicked()