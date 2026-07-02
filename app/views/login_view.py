from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from app.services.auth_service import AuthService

class LoginView(QWidget):
    # Sinal que avisa a janela principal que o login foi feito com sucesso
    login_sucesso = Signal()

    def __init__(self, auth_service: AuthService):
        super().__init__()
        self.auth_service = auth_service
        self.setup_ui()

    def setup_ui(self):
        """Estrutura os componentes visuais da tela de login."""
        self.setWindowTitle("SisCAM - Controle de Acesso (Login)")
        self.setFixedSize(380, 250)

        # Layout Principal Centralizado
        layout_principal = QVBoxLayout()
        layout_principal.setSpacing(15)
        layout_principal.setContentsMargins(30, 30, 30, 30)

        # Título da Tela
        self.label_titulo = QLabel("Acesso ao Sistema")
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout_principal.addWidget(self.label_titulo)

        # Campo: Usuário
        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Digite seu usuário (Ex: sargento.silva)")
        self.input_usuario.setStyleSheet("padding: 8px; font-size: 13px;")
        layout_principal.addWidget(self.input_usuario)

        # Campo: Senha
        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Digite sua senha")
        self.input_senha.setEchoMode(QLineEdit.EchoMode.Password)  # Oculta os caracteres
        self.input_senha.setStyleSheet("padding: 8px; font-size: 13px;")
        # Permite fazer login apertando 'Enter' dentro do campo de senha
        self.input_senha.returnPressed.connect(self.handle_login)
        layout_principal.addWidget(self.input_senha)

        # Botão de Entrar
        self.btn_entrar = QPushButton("Entrar no Sistema")
        self.btn_entrar.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 10px; border-radius: 4px; font-size: 13px; }"
            "QPushButton:hover { background-color: #219653; }"
        )
        self.btn_entrar.clicked.connect(self.handle_login)
        layout_principal.addWidget(self.btn_entrar)

        self.setLayout(layout_principal)

    def handle_login(self):
        """Coleta os dados da tela e valida com a regra de negócio."""
        username = self.input_usuario.text().strip()
        senha = self.input_senha.text()

        if not username or not len(senha):
            QMessageBox.warning(self, "Aviso", "Preencha todos os campos para prosseguir.")
            return

        # Desabilita o botão temporariamente para evitar cliques duplos
        self.btn_entrar.setEnabled(False)

        # Dispara a verificação real usando o nosso AuthService + Bcrypt
        sucesso = self.auth_service.realizar_login(username, senha)

        if sucesso:
            # Emite o sinal de que o login deu certo para a aplicação abrir a janela principal
            self.login_sucesso.emit()
            self.close()
        else:
            QMessageBox.critical(self, "Erro de Acesso", "Usuário ou senha incorretos, ou operador inativo.")
            self.input_senha.clear()
            self.btn_entrar.setEnabled(True)