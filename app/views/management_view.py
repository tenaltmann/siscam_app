from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit, 
    QHeaderView, QAbstractItemView, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from app.services.om_service import OMService

# Importação dos novos modais que criamos
from app.views.militar_dialog import MilitarDialog
from app.views.viatura_dialog import ViaturaDialog

# Importação dos modelos para consulta
from app.models.models import UsuarioMilitar, Veiculo

class ManagementView(QWidget):
    def __init__(self, om_service: OMService):
        super().__init__()
        self.om_service = om_service
        self.db = om_service.session  # Reaproveita a sessão de banco do serviço
        self.setup_ui()
        self.carregar_dados_reais()   # Agora carregamos os dados do banco

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
        self.txt_busca_militar.textChanged.connect(self.carregar_dados_reais) # Busca em tempo real
        
        self.btn_novo_militar = QPushButton("+ Cadastrar Militar")
        self.btn_novo_militar.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 5px 10px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #2ecc71; }"
        )
        self.btn_novo_militar.clicked.connect(self.abrir_cadastro_militar) # Conecta o botão
        
        barra_militares.addWidget(self.txt_busca_militar)
        barra_militares.addWidget(self.btn_novo_militar)
        layout_principal.addLayout(barra_militares)

        # Tabela de Militares
        self.tabela_militares = QTableWidget()
        self.tabela_militares.setColumnCount(4)
        self.tabela_militares.setHorizontalHeaderLabels(["Identidade", "Nome Completo", "Possui Veículo", "Status"])
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
        self.txt_busca_viatura.textChanged.connect(self.carregar_dados_reais) # Busca em tempo real
        
        self.btn_nova_viatura = QPushButton("+ Cadastrar Viatura")
        self.btn_nova_viatura.setStyleSheet(
            "QPushButton { background-color: #2980b9; color: white; font-weight: bold; padding: 5px 10px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #3498db; }"
        )
        self.btn_nova_viatura.clicked.connect(self.abrir_cadastro_viatura) # Conecta o botão
        
        barra_viaturas.addWidget(self.txt_busca_viatura)
        barra_viaturas.addWidget(self.btn_nova_viatura)
        layout_principal.addLayout(barra_viaturas)

        # Tabela de Viaturas
        self.tabela_viaturas = QTableWidget()
        self.tabela_viaturas.setColumnCount(4)
        self.tabela_viaturas.setHorizontalHeaderLabels(["Placa", "Modelo", "Tipo", "ID Proprietário"])
        self.tabela_viaturas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_viaturas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_viaturas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout_principal.addWidget(self.tabela_viaturas)

    def carregar_dados_reais(self):
        """Busca os dados do banco SQLite filtrando por termos digitados na busca."""
        try:
            # 1. Carregar Militares
            busca_mil = self.txt_busca_militar.text().strip()
            query_mil = self.db.query(UsuarioMilitar)
            if busca_mil:
                query_mil = query_mil.filter(
                    (UsuarioMilitar.nome_completo.like(f"%{busca_mil}%")) | 
                    (UsuarioMilitar.rg.like(f"%{busca_mil}%"))
                )
            militares = query_mil.all()
            
            self.tabela_militares.setRowCount(len(militares))
            for i, mil in enumerate(militares):
                self.tabela_militares.setItem(i, 0, QTableWidgetItem(mil.rg))
                self.tabela_militares.setItem(i, 1, QTableWidgetItem(mil.nome_completo))
                self.tabela_militares.setItem(i, 2, QTableWidgetItem("Sim" if mil.possui_veiculo else "Não"))
                self.tabela_militares.setItem(i, 3, QTableWidgetItem("Ativo" if mil.esta_ativo else "Inativo"))

            # 2. Carregar Viaturas / Veículos
            busca_via = self.txt_busca_viatura.text().strip()
            query_via = self.db.query(Veiculo)
            if busca_via:
                query_via = query_via.filter(
                    (Veiculo.placa.like(f"%{busca_via}%")) | 
                    (Veiculo.modelo.like(f"%{busca_via}%"))
                )
            viaturas = query_via.all()

            self.tabela_viaturas.setRowCount(len(viaturas))
            for i, via in enumerate(viaturas):
                self.tabela_viaturas.setItem(i, 0, QTableWidgetItem(via.placa))
                self.tabela_viaturas.setItem(i, 1, QTableWidgetItem(via.modelo))
                self.tabela_viaturas.setItem(i, 2, QTableWidgetItem(via.tipo))
                self.tabela_viaturas.setItem(i, 3, QTableWidgetItem(str(via.proprietario_id)[:8] + "..."))

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar tabelas: {e}")

    def abrir_cadastro_militar(self):
        """Abre o modal flutuante e recarrega a tabela se o usuário salvou os dados."""
        dialog = MilitarDialog(self.db, self)
        if dialog.exec() == MilitarDialog.DialogCode.Accepted:
            self.carregar_dados_reais()

    def abrir_cadastro_viatura(self):
        """Abre o modal flutuante e recarrega a tabela se o usuário salvou os dados."""
        dialog = ViaturaDialog(self.db, self)
        if dialog.exec() == ViaturaDialog.DialogCode.Accepted:
            self.carregar_dados_reais()