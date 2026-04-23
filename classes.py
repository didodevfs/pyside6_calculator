from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLineEdit, QLabel, QGridLayout, QPushButton, QMessageBox
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QKeyEvent
from styles import TEXT_MARGIN, MAIN_FONT_SIZE, MINIMUN_WIDTH
from tools import reseting_win_attributes

class Display(QLineEdit):
    equal_signal = Signal()
    delete_signal = Signal()
    reset_signal = Signal()
    operator_signal = Signal(str)
    numbers_signal = Signal(str)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_style()

        # self.setReadOnly(True) # não permitirá que o usuário digite algo no display (eu também precisaria excluir o método keyPressEvent)


    def set_style(self):
        margins = [TEXT_MARGIN for _ in range(4)] # porque é necessário passar 4 parâmetros: left, top, right, bottom. Então essa list comprehension passa o TEXT_MARGIN para os 4
        self.setStyleSheet(f'font-size: {MAIN_FONT_SIZE}px;')
        # self.setMinimumHeight(MAIN_FONT_SIZE * 2) # Comentei porque aparentemente é desnecessário - provavelmente por já possui margem superior e inferior através do setTextMargins
        self.setMinimumWidth(MINIMUN_WIDTH)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setTextMargins(*margins)


    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        text = event.text()

        enter = key in [Qt.Key.Key_Enter, Qt.Key.Key_Return]
        delete = key in [Qt.Key.Key_Backspace, Qt.Key.Key_Delete]
        esc = key in [Qt.Key.Key_Escape, Qt.Key.Key_C]
        operator = key in [Qt.Key.Key_Plus, Qt.Key.Key_Minus, Qt.Key.Key_Asterisk, Qt.Key.Key_Slash]
        number = text in '.0123456789'

        if enter:
            self.equal_signal.emit()
            return event.ignore()
        
        if delete:
            self.delete_signal.emit()
            return event.ignore()
        
        if esc:
            self.reset_signal.emit()
            return event.ignore()

        if operator:
            # print('pressionou um operador')
            self.operator_signal.emit(text)
            return event.ignore()

        if number:
            self.numbers_signal.emit(text)
            return event.ignore()
            # return super().keyPressEvent(event)



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


    def error_msg_box(self, text):
        msg_box = QMessageBox(QMessageBox.Icon.Critical, 'Erro', text)       
        msg_box.exec()


    def wtf_msg_box(self, text, button):
        msg_box = QMessageBox(QMessageBox.Icon.Critical, 'Erro', text)

        msg_box.setInformativeText('O botão "Ok 👍" fará você continuar mesmo assim')
        msg_box.setStandardButtons(msg_box.StandardButton.Cancel | msg_box.StandardButton.Ok)
      
        msg_box.button(msg_box.StandardButton.Cancel).setText('Limpar e Continuar')
        msg_box.button(msg_box.StandardButton.Ok).setText('Ok 👍')

        selected_button = msg_box.exec()

        if selected_button == msg_box.StandardButton.Cancel:
            button.get_reset()



class Button(QPushButton):   
    def __init__(self, grid, window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = self.font()
        font.setPixelSize(MAIN_FONT_SIZE)
        self.setFont(font)
        self.setMinimumSize(75, 75)
        
        self.grid = grid
        self.win = window
        self.special_type = None
       

    def set_special_button(self, button_text):
        self.setProperty('css_class', 'special_button')

        if button_text in '+-/*^':
            self.special_type = 'operator'
        elif button_text == '◀':
            self.special_type = 'del'
        elif button_text == 'C':
            self.special_type = 'reset'
        elif button_text == '=':
            self.special_type = 'equal'

        return self.special_type


    def connect_button_clicked(self, special_type):
        if not special_type:
            slot_method = self.get_number
        if special_type == 'operator':
            slot_method = self.get_operator
        if special_type == 'equal':
            slot_method = self.get_equal
        if special_type == 'reset':
            slot_method = self.get_reset
        if special_type == 'del':
            slot_method = self.get_delete
        
        return self.clicked.connect(slot_method)


    @Slot()
    def get_number(self, *args):
        if not args and self.text() == '🐍':
            self._didodev()

        if self.win.result or self.win.result == 0.0:
            self._result_to_first_number()
        
        if not self.win.operator:
            try:
                if args:
                    button_text, = args
                else:
                    button_text = self.text()
                input = self.win.display.text() + button_text
                self.win.first_number = float(input)
                self.win.display.insert(button_text)
                self.win.equation = f'{self.win.first_number}'
            except Exception as error:
                print(error)
                if self.text() != '🐍':
                    self.win.error_msg_box('Digite um número antes do ponto')
        
        else:
            try:
                if args:
                    button_text, = args
                else:
                    button_text = self.text()
                input_test = self.win.display.text() + button_text
                self.win.second_number = float(input_test)
                self.win.display.insert(button_text)
                self.win.equation = f'{self.win.first_number} {self.win.operator} {self.win.second_number}'
            except Exception as error:
                print(error)
                self.win.error_msg_box('Digite um número antes do ponto')


    @Slot()
    def get_operator(self, *args):
        if self.win.result or self.win.result == 0.0:
            self._result_to_first_number()

        if self.win.first_number or self.win.first_number == 0.0: # and not self.win.operator
            if self.win.second_number or self.win.second_number == 0.0:
                self.win.error_msg_box('Você não pode adicionar outro operador neste momento')
            else:
                if args:
                    button_text, = args
                else:
                    button_text = self.text()
                self.win.display.clear()
                self.win.operator = button_text
                self.win.equation = f'{self.win.first_number} {self.win.operator} '
        else: # self.win.first_number
            if args:
                button_text, = args
            else:
                button_text = self.text()

            if button_text == '-':
                # self.win.display.clear()
                self.win.display.insert(button_text)
            else:
                self.win.error_msg_box('Digite um número primeiro')


    @Slot()
    def get_equal(self):
        if (self.win.second_number or self.win.second_number == 0.0) and '=' not in self.win.equation:
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

            except ZeroDivisionError:
                self.win.error_msg_box('Não dá pra dividir por zero')

            except OverflowError:
                self.win.error_msg_box('Essa conta é muito grande e não pode ser realizada!')
            
            except Exception as error:
                self.win.wtf_msg_box('Que danado de conta é essa?!', self)
                print(error)
    

    @Slot()
    def get_reset(self):
        self.win.display.clear()
        reseting_win_attributes(self.win)


    @Slot()
    def get_delete(self):
        self.win.display.backspace()
        if self.win.result or self.win.result == 0.0:
            self.win.result = self.win.display.text()
            self._result_to_first_number()
        if self.win.second_number or self.win.second_number == 0.0:
            self.win.second_number = self.win.display.text()
            self.win.equation = f'{self.win.first_number} {self.win.operator} {self.win.second_number}'
        if not self.win.second_number:
            if self.win.operator:
                self.win.error_msg_box('Não há nada no display para apagar')
            else:
                self.win.first_number = self.win.display.text()
                self.win.equation = f'{self.win.first_number}'

    
    def _result_to_first_number(self):
        first_number = self.win.result
        reseting_win_attributes(self.win)
        self.win.first_number = first_number


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

                button.connect_button_clicked(button.special_type)

        self.window.display.numbers_signal.connect(button.get_number)
        self.window.display.operator_signal.connect(button.get_operator)
        self.window.display.equal_signal.connect(button.get_equal)
        self.window.display.reset_signal.connect(button.get_reset)
        self.window.display.delete_signal.connect(button.get_delete)