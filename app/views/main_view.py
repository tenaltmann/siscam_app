from app.views.management_view import ManagementView
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QPushButton, QFrame, QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from app.services.om_service import OMService
from app.services.auth_service import AuthService
from app.services.portaria_service import PortariaService 

class MainView(QMainWindow):
    def __init__(self, auth_service: AuthService, om_service: OMService, portaria_service: PortariaService):
        super().__init__()
        self.auth_service = auth_service
        self.om_service = om_service
        self.portaria_service = portaria_service
        
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

        self.aba_gerenciamento = ManagementView(self.om_service)
        
        # Adicionando as abas ao componente principal
        self.abas.addTab(self.aba_dashboard, "📊 Dashboard")
        self.abas.addTab(self.aba_portaria, "🚗 Controle de Portaria")
        
        self.abas.addTab(self.aba_gerenciamento, "⚙️ Gerenciamento")
        
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
        """Estrutura o formulário de controle de acesso para Militares e Viaturas."""
        layout_principal = QHBoxLayout(self.aba_portaria)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(20)

        # --- PAINEL ESQUERDO: CONTROLE DE MILITARES ---
        painel_militar = QFrame()
        painel_militar.setStyleSheet("QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; }")
        layout_mil = QVBoxLayout(painel_militar)
        
        lbl_tit_mil = QLabel("👥 Movimentação de Militar")
        lbl_tit_mil.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50; border: none;")
        layout_mil.addWidget(lbl_tit_mil)

        layout_mil.addWidget(QLabel("ID do Militar:"))
        self.txt_militar_id = QLineEdit()
        self.txt_militar_id.setPlaceholderText("Cole o UUID do militar aqui...")
        layout_mil.addWidget(self.txt_militar_id)

        layout_mil.addWidget(QLabel("Tipo de Acesso:"))
        self.cb_tipo_militar = QComboBox()
        self.cb_tipo_militar.addItems(["ENTRADA", "SAÍDA"])
        layout_mil.addWidget(self.cb_tipo_militar)

        layout_mil.addWidget(QLabel("Observação / Motivo:"))
        self.txt_obs_militar = QLineEdit()
        layout_mil.addWidget(self.txt_obs_militar)

        self.btn_salvar_militar = QPushButton("Registrar Acesso Militar")
        self.btn_salvar_militar.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 8px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #2ecc71; }"
        )
        self.btn_salvar_militar.clicked.connect(self.processar_acesso_militar)
        layout_mil.addWidget(self.btn_salvar_militar)
        layout_mil.addStretch()

        # --- PAINEL DIREITO: CONTROLE DE VIATURAS ---
        painel_viatura = QFrame()
        painel_viatura.setStyleSheet("QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 8px; }")
        layout_via = QVBoxLayout(painel_viatura)

        lbl_tit_via = QLabel("🚗 Movimentação de Viatura")
        lbl_tit_via.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50; border: none;")
        layout_via.addWidget(lbl_tit_via)

        layout_via.addWidget(QLabel("Placa da Viatura:"))
        self.txt_via_placa = QLineEdit()
        layout_via.addWidget(self.txt_via_placa)

        layout_via.addWidget(QLabel("ID do Motorista (Militar):"))
        self.txt_via_motorista = QLineEdit()
        layout_via.addWidget(self.txt_via_motorista)

        layout_via.addWidget(QLabel("Tipo de Acesso:"))
        self.cb_tipo_viatura = QComboBox()
        self.cb_tipo_viatura.addItems(["ENTRADA", "SAÍDA"])
        layout_via.addWidget(self.cb_tipo_viatura)

        layout_via.addWidget(QLabel("Destino / Missão:"))
        self.txt_via_destino = QLineEdit()
        layout_via.addWidget(self.txt_via_destino)

        self.btn_salvar_viatura = QPushButton("Registrar Acesso Viatura")
        self.btn_salvar_viatura.setStyleSheet(
            "QPushButton { background-color: #2980b9; color: white; font-weight: bold; padding: 8px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #3498db; }"
        )
        self.btn_salvar_viatura.clicked.connect(self.processar_acesso_viatura)
        layout_via.addWidget(self.btn_salvar_viatura)
        layout_via.addStretch()

        # Adiciona os painéis ao layout principal horizontal da aba
        layout_principal.addWidget(painel_militar)
        layout_principal.addWidget(painel_viatura)

    def processar_acesso_militar(self):
        militar_id = self.txt_militar_id.text().strip()
        tipo = self.cb_tipo_militar.currentText()
        obs = self.txt_obs_militar.text().strip() or None

        if not militar_id:
            QMessageBox.warning(self, "Aviso", "O ID do militar é obrigatório.")
            return

        try:
            self.portaria_service.registrar_acesso_militar(militar_id, tipo, obs)
            QMessageBox.information(self, "Sucesso", f"Movimentação de {tipo} registrada!")
            self.txt_militar_id.clear()
            self.txt_obs_militar.clear()
            self.atualizar_dashboard() # Força o dashboard a atualizar os cards na hora
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao registrar: {e}") 
  
    def processar_acesso_viatura(self):
        placa = self.txt_via_placa.text().strip()
        motorista_id = self.txt_via_motorista.text().strip()
        tipo = self.cb_tipo_viatura.currentText()
        destino = self.txt_via_destino.text().strip() or None

        if not placa or not motorista_id:
            QMessageBox.warning(self, "Aviso", "Placa e ID do motorista são obrigatórios.")
            return

        try:
            self.portaria_service.registrar_acesso_viatura(
                viatura_placa=placa, motorista_id=motorista_id, tipo=tipo, destino=destino
            )
            QMessageBox.information(self, "Sucesso", f"Movimentação da Viatura registrada!")
            self.txt_via_placa.clear()
            self.txt_via_motorista.clear()
            self.txt_via_destino.clear()
            self.atualizar_dashboard() # Atualiza os contadores na hora
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao registrar: {e}")

    def atualizar_dashboard(self):
        """Busca os contadores atualizados da OM via repositório/sessão e atualiza a tela."""
        from app.models.models import OrganizacaoMilitar
        
        # Busca a primeira OM cadastrada no sistema
        om = self.om_service.session.query(OrganizacaoMilitar).first()
        
        if om:
            self.lbl_efetivo_num.setText(str(om.qtd_militares)) # Corrigido para qtd_militares
            self.lbl_viaturas_num.setText(str(om.qtd_viaturas)) # Corrigido para qtd_viaturas
        else:
            self.lbl_efetivo_num.setText("0")
            self.lbl_viaturas_num.setText("0")