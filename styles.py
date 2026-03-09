# QSS - Estilos do QT for Python
# https://doc.qt.io/qtforpython/tutorials/basictutorial/widgetstyling.html

import qdarkstyle

qss = f"""
    QPushButton[css_class="special_button"] {{
        color: #fff;
        background: "#1e81b0";
        border-radius: 5px;
    }}
    QPushButton[css_class="special_button"]:hover {{
        color: #fff;
        background: "#16658a";
    }}
    QPushButton[css_class="special_button"]:pressed {{
        color: #fff;
        background: "#115270";
    }}
"""
# esses códigos em blackground são das cores, o prof colocou eles em variáveis no módulo variables e trouxe pra cá com f'string. Eu preferi deixar aí diretamente.

def setup_theme(app):
    # Aplicar o estilo escuro no qdarkstyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())

    # Sobrepor com o QSS personalizado para estilização adicional
    app.setStyleSheet(app.styleSheet() + qss)