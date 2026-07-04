from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QMessageBox
)
from sqlalchemy.orm import Session
from app.models.models import Veiculo, UsuarioMilitar

class ViaturaDialog(QDialog):
    def __init__(self, db_session: Session, parent=None):
        super().__init__(parent)
        self.db = db_session
        self.setup_ui()
        self.carregar_motoristas()

    def setup_ui(self):
        self.setWindowTitle("Cadastrar Nova Viatura / Veículo")
        self.resize(400, 320)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Campos do Formulário
        layout.addWidget(QLabel("Placa do Veículo:"))
        self.txt_placa = QLineEdit()
        self.txt_placa.setPlaceholderText("Ex: EB-12345 ou ABC1D23")
        layout.addWidget(self.txt_placa)

        layout.addWidget(QLabel("Modelo / Marca:"))
        self.txt_modelo = QLineEdit()
        self.txt_modelo.setPlaceholderText("Ex: Marruá AM21 / Toyota Hilux")
        layout.addWidget(self.txt_modelo)

        layout.addWidget(QLabel("Tipo de Veículo:"))
        self.cb_tipo = QComboBox()
        self.cb_tipo.addItems(["Viatura Operacional", "Viatura Administrativa", "Particular (Militar)"])
        layout.addWidget(self.cb_tipo)

        layout.addWidget(QLabel("Proprietário / Motorista Responsável:"))
        self.cb_motorista = QComboBox()
        layout.addWidget(self.cb_motorista)

        # Botões de Ação
        layout_botoes = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")
        self.btn_salvar.clicked.connect(self.salvar_viatura)
        
        layout_botoes.addWidget(self.btn_cancelar)
        layout_botoes.addWidget(self.btn_salvar)
        layout.addLayout(layout_botoes)

    def carregar_motoristas(self):
        """Busca os militares ativos para listar no ComboBox de responsáveis."""
        try:
            militares = self.db.query(UsuarioMilitar).filter(UsuarioMilitar.esta_ativo == True).all()
            for mil in militares:
                # Exibe o nome e vincula o UUID interno do militar ao item do ComboBox
                self.cb_motorista.addItem(mil.nome_completo, mil.id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar militares: {e}")

    def salvar_viatura(self):
        placa = self.txt_placa.text().strip().upper()
        modelo = self.txt_modelo.text().strip()
        tipo = self.cb_tipo.currentText()
        proprietario_id = self.cb_motorista.currentData()

        if not placa or not modelo or not proprietario_id:
            QMessageBox.warning(self, "Aviso", "Todos os campos são obrigatórios.")
            return

        try:
            # Cria a entidade do modelo de Veiculo
            nova_viatura = Veiculo(
                placa=placa,
                modelo=modelo,
                tipo=tipo,
                proprietario_id=proprietario_id
            )
            
            self.db.add(nova_viatura)
            self.db.commit()
            
            QMessageBox.information(self, "Sucesso", "Veículo cadastrado com sucesso!")
            self.accept()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Erro", f"Falha ao salvar veículo: {e}")