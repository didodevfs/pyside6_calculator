import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from classes import Window, Display, History, ButtonsGrid
from tools import ICON_PATH
from styles import setup_theme


if __name__ == '__main__':
    # Cria a Aplicação
    app = QApplication(sys.argv)
    setup_theme(app)
    # window = Window()

    # Define o ícone
    icon = QIcon(ICON_PATH)
    # window.setWindowIcon(icon)
    app.setWindowIcon(icon) # Tanto em app. como em window. funciona. Não precisa setar nos dois. Tentar entender a diferença. Acredito que ele quis colocar para o símbolo aparecer na barra lá embaixo além de na janela. Não funcionou para mim (na barra, na janela sim). Tentar consertar.

    # Histórico da conta
    history = History('') # Não é preciso colocar as aspas. Deixei apenas pra saber que eu posso passar um texto pro QLabel
    # window.add_widget_to_main_layout(history)

    # Display
    display = Display() # inicialmente eu tinha colocado logo abaixo de onde crio window # Posso colocar algo dentro dos parênteses que irá aparecer no display quando abrir o app
    # Com o display.setPlaceholderText('Mensagem aqui') o 'Mensagem aqui' aparece "transpartente" no display enquanto algo nao é digitado
    # window.add_widget_to_main_layout(display)
   
    window = Window(display, history)
    window.setWindowIcon(icon)
    window.add_widget_to_main_layout(history)
    window.add_widget_to_main_layout(display)
    # Teclado
    virtual_keyboard = ButtonsGrid(window)
    window.main_layout.addLayout(virtual_keyboard)

    # Executa tudo
    window.adjust_fixed_size()
    window.show()
    app.exec()