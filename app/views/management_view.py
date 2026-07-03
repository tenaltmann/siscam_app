from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
    QHeaderView, QAbstractItemView, QComboBox
)
from PySide6.QtCore import Qt
from app.services.om_service import OMService

class ManagementView(QWidget):
    def __init__(self, om_service: OMService):
        super().__init__()
        self.om_service = om_service
        self.setup_ui()

    def setup_ui(self):
        """Estrutura a interface de gerenciamento de militares e viaturas."""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(10, 10, 10, 10)
        layout_principal.setSpacing(15)

        # Título da Seção
        titulo = QLabel("Administração de Pessoal e Material")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        layout_principal.addWidget(titulo)

        # --- SEÇÃO DE MILITARES ---
        sub_titulo_militares = QLabel("👥 Militares Cadastrados")
        sub_titulo_militares.setStyleSheet("font-size: 13px; font-weight: bold; color: #34495e;")
        layout_principal.addWidget(sub_titulo_militares)

        # Barra de Ações para Militares (Busca / Novo)
        barra_militares = QHBoxLayout()
        self.txt_busca_militar = QLineEdit()
        self.txt_busca_militar.setPlaceholderText("Buscar militar por nome ou identidade...")
        
        self.btn_novo_militar = QPushButton("+ Cadastrar Militar")
        self.btn_novo_militar.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 5px 10px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #2ecc71; }"
        )
        
        barra_militares.addWidget(self.txt_busca_militar)
        barra_militares.addWidget(self.btn_novo_militar)
        layout_principal.addLayout(barra_militares)

        # Tabela de Militares
        self.tabela_militares = QTableWidget()
        self.tabela_militares.setColumnCount(4)
        self.tabela_militares.setHorizontalHeaderLabels(["Identidade", "Posto/Grad", "Nome Completo", "Status"])
        self.tabela_militares.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_militares.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_militares.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout_principal.addWidget(self.tabela_militares)

        # --- SEÇÃO DE VIATURAS ---
        sub_titulo_viaturas = QLabel("🚗 Viaturas Cadastradas")
        sub_titulo_viaturas.setStyleSheet("font-size: 13px; font-weight: bold; color: #34495e; margin-top: 10px;")
        layout_principal.addWidget(sub_titulo_viaturas)

        # Barra de Ações para Viaturas
        barra_viaturas = QHBoxLayout()
        self.txt_busca_viatura = QLineEdit()
        self.txt_busca_viatura.setPlaceholderText("Buscar viatura por placa ou modelo...")
        
        self.btn_nova_viatura = QPushButton("+ Cadastrar Viatura")
        self.btn_nova_viatura.setStyleSheet(
            "QPushButton { background-color: #2980b9; color: white; font-weight: bold; padding: 5px 10px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #3498db; }"
        )
        
        barra_viaturas.addWidget(self.txt_busca_viatura)
        barra_viaturas.addWidget(self.btn_nova_viatura)
        layout_principal.addLayout(barra_viaturas)

        # Tabela de Viaturas
        self.tabela_viaturas = QTableWidget()
        self.tabela_viaturas.setColumnCount(4)
        self.tabela_viaturas.setHorizontalHeaderLabels(["Placa", "Modelo", "Tipo", "Localização"])
        self.tabela_viaturas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_viaturas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_viaturas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout_principal.addWidget(self.tabela_viaturas)

        # Inicializa as tabelas com placeholders visuais
        self.carregar_dados_mock()

    def carregar_dados_mock(self):
        """Insere linhas temporárias para validação visual do layout."""
        # Mock Militares
        self.tabela_militares.setRowCount(1)
        self.tabela_militares.setItem(0, 0, QTableWidgetItem("123456789-0"))
        self.tabela_militares.setItem(0, 1, QTableWidgetItem("Capitão"))
        self.tabela_militares.setItem(0, 2, QTableWidgetItem("Caxias da Silva"))
        self.tabela_militares.setItem(0, 3, QTableWidgetItem("Interno"))

        # Mock Viaturas
        self.tabela_viaturas.setRowCount(1)
        self.tabela_viaturas.setItem(0, 0, QTableWidgetItem("EB-12345"))
        self.tabela_viaturas.setItem(0, 1, QTableWidgetItem("Marruá AM21"))
        self.tabela_viaturas.setItem(0, 2, QTableWidgetItem("Operacional"))
        self.tabela_viaturas.setItem(0, 3, QTableWidgetItem("Na OM"))