from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from sqlalchemy.orm import Session
from app.models.models import UsuarioMilitar, OrganizacaoMilitar
from datetime import date

class MilitarDialog(QDialog):
    def __init__(self, db_session: Session, parent=None):
        super().__init__(parent)
        self.db = db_session
        self.setup_ui()
        self.carregar_oms()

    def setup_ui(self):
        self.setWindowTitle("Cadastrar Novo Militar")
        self.resize(400, 350)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Campos do Formulário
        layout.addWidget(QLabel("Nome Completo:"))
        self.txt_nome = QLineEdit()
        layout.addWidget(self.txt_nome)

        layout.addWidget(QLabel("Identidade (RG):"))
        self.txt_rg = QLineEdit()
        layout.addWidget(self.txt_rg)

        layout.addWidget(QLabel("Organização Militar:"))
        self.cb_om = QComboBox()
        layout.addWidget(self.cb_om)

        layout.addWidget(QLabel("Possui Veículo Particular?"))
        self.cb_veiculo = QComboBox()
        self.cb_veiculo.addItems(["Não", "Sim"])
        layout.addWidget(self.cb_veiculo)

        # Botões de Ação
        layout_botoes = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_salvar = QPushButton("Salvar")
        self.btn_salvar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_salvar.clicked.connect(self.salvar_militar)
        
        layout_botoes.addWidget(self.btn_cancelar)
        layout_botoes.addWidget(self.btn_salvar)
        layout.addLayout(layout_botoes)

    def carregar_oms(self):
        """Busca as OMs cadastradas no banco para preencher o ComboBox."""
        try:
            oms = self.db.query(OrganizacaoMilitar).all()
            for om in oms:
                # Armazena o nome visível e vincula o ID real da OM internamente
                self.cb_om.addItem(f"{om.sigla} - {om.nome}", om.id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar OMs: {e}")

    def salvar_militar(self):
        nome = self.txt_nome.text().strip()
        rg = self.txt_rg.text().strip()
        om_id = self.cb_om.currentData() # Pega o ID da OM selecionada
        possui_veiculo = self.cb_veiculo.currentText() == "Sim"

        if not nome or not rg or not om_id:
            QMessageBox.warning(self, "Aviso", "Todos os campos são obrigatórios.")
            return

        try:
            # Cria a entidade do modelo
            novo_militar = UsuarioMilitar(
                nome_completo=nome,
                rg=rg,
                organizacao_militar_id=om_id,
                possui_veiculo=possui_veiculo,
                data_nascimento=date(1995, 1, 1), # Padrão temporário para não complicar o form
                data_apresentacao=date.today(),
                esta_ativo=True
            )
            
            self.db.add(novo_militar)
            self.db.commit()
            
            QMessageBox.information(self, "Sucesso", "Militar cadastrado com sucesso!")
            self.accept() # Fecha o modal retornando sucesso
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Erro", f"Falha ao salvar no banco: {e}")