from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt
from app.services.om_service import OMService
from app.services.auth_service import AuthService

class MainView(QMainWindow):
    def __init__(self, auth_service: AuthService, om_service: OMService):
        super().__init__()
        self.auth_service = auth_service
        self.om_service = om_service
        
        self.setup_ui()
        self.atualizar_dashboard()

    def setup_ui(self):
        """Estrutura os componentes visuais da janela principal."""
        self.setWindowTitle("SisCAM - Sistema de Controle de Acesso Militar")
        self.resize(900, 600)

        # Widget Central e Layout Principal
        widget_central = QWidget()
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(15, 15, 15, 15)
        layout_principal.setSpacing(10)

        # --- BARRA SUPERIOR (Info do Operador) ---
        barra_superior = QHBoxLayout()
        
        operador = self.auth_service.obter_usuario_logado()
        nome_operador = operador.nome_completo if operador else "Operador"
        
        self.label_usuario = QLabel(f"<b>Operador:</b> {nome_operador}")
        self.label_usuario.setStyleSheet("font-size: 13px; color: #34495e;")
        
        self.btn_logout = QPushButton("Sair / Logoff")
        self.btn_logout.setStyleSheet(
            "QPushButton { background-color: #c0392b; color: white; border-radius: 4px; padding: 5px 15px; font-weight: bold; }"
            "QPushButton:hover { background-color: #e74c3c; }"
        )
        self.btn_logout.clicked.connect(self.close) # Temporário para fechar a tela
        
        barra_superior.addWidget(self.label_usuario)
        barra_superior.addStretch()
        barra_superior.addWidget(self.btn_logout)
        layout_principal.addLayout(barra_superior)

        # --- SISTEMA DE ABAS (Navegação) ---
        self.abas = QTabWidget()
        self.abas.setStyleSheet("QTabBar::tab { font-size: 13px; padding: 8px 20px; font-weight: bold; }")
        
        # Criando os containers das abas
        self.aba_dashboard = QWidget()
        self.aba_portaria = QWidget()
        
        # Inicializando os layouts de cada aba
        self.setup_aba_dashboard()
        self.setup_aba_portaria()
        
        # Adicionando as abas ao componente principal
        self.abas.addTab(self.aba_dashboard, "📊 Dashboard")
        self.abas.addTab(self.aba_portaria, "🚗 Controle de Portaria")
        
        layout_principal.addWidget(self.abas)
        self.setCentralWidget(widget_central)

    def setup_aba_dashboard(self):
        """Estrutura a aba do Dashboard com os cards de contadores."""
        layout = QVBoxLayout(self.aba_dashboard)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Título da Seção
        titulo = QLabel("Visão Geral da Organização Militar")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(titulo)

        # Layout Horizontal para os Cards de Contadores
        layout_cards = QHBoxLayout()
        layout_cards.setSpacing(20)

        # Card 1: Efetivo Presente
        self.card_efetivo = QFrame()
        self.card_efetivo.setStyleSheet("QFrame { background-color: #ebf5fb; border: 1px solid #a9dfbf; border-radius: 8px; }")
        layout_efetivo = QVBoxLayout(self.card_efetivo)
        
        lbl_efetivo_txt = QLabel("Militar(es) Interno(s)")
        lbl_efetivo_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_efetivo_txt.setStyleSheet("font-size: 14px; color: #2e4053; border: none;")
        
        self.lbl_efetivo_num = QLabel("0")
        self.lbl_efetivo_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_efetivo_num.setStyleSheet("font-size: 36px; font-weight: bold; color: #2980b9; border: none;")
        
        layout_efetivo.addWidget(lbl_efetivo_txt)
        layout_efetivo.addWidget(self.lbl_efetivo_num)

        # Card 2: Viaturas Internas
        self.card_viaturas = QFrame()
        self.card_viaturas.setStyleSheet("QFrame { background-color: #fef9e7; border: 1px solid #f9e79f; border-radius: 8px; }")
        layout_viaturas = QVBoxLayout(self.card_viaturas)
        
        lbl_viaturas_txt = QLabel("Viatura(s) na OM")
        lbl_viaturas_txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_viaturas_txt.setStyleSheet("font-size: 14px; color: #2e4053; border: none;")
        
        self.lbl_viaturas_num = QLabel("0")
        self.lbl_viaturas_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_viaturas_num.setStyleSheet("font-size: 36px; font-weight: bold; color: #d35400; border: none;")
        
        layout_viaturas.addWidget(lbl_viaturas_txt)
        layout_viaturas.addWidget(self.lbl_viaturas_num)

        # Adiciona os cards ao layout horizontal
        layout_cards.addWidget(self.card_efetivo)
        layout_cards.addWidget(self.card_viaturas)
        
        layout.addLayout(layout_cards)
        layout.addStretch() # Empurra tudo para cima

    def setup_aba_portaria(self):
        """Estrutura provisória para a aba de portaria (será detalhada na Etapa 5)."""
        layout = QVBoxLayout(self.aba_portaria)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        placeholder = QLabel("🚧 Área de Registro de Entradas e Saídas (Próxima Etapa) 🚧")
        placeholder.setStyleSheet("font-size: 14px; color: #7f8c8d; font-style: italic;")
        layout.addWidget(placeholder)

    def atualizar_dashboard(self):
        """Busca os contadores atualizados da OM via repositório/sessão e atualiza a tela."""
        from app.models.models import OrganizacaoMilitar
        
        # Como o OMService tem acesso à sessão do banco, usamos ela para buscar a OM ID 1
        om = self.om_service.session.query(OrganizacaoMilitar).filter(OrganizacaoMilitar.id == 1).first()
        
        if om:
            self.lbl_efetivo_num.setText(str(om.total_militares_internos))
            self.lbl_viaturas_num.setText(str(om.total_viaturas_internas))
        else:
            self.lbl_efetivo_num.setText("0")
            self.lbl_viaturas_num.setText("0")