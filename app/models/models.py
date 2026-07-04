from datetime import date, datetime
from typing import List, Optional
import uuid
from sqlalchemy import ForeignKey, String, Integer, Boolean, Date, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.connection import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Perfil(Base):
    __tablename__ = "perfis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # Relacionamento com usuários
    usuarios: Mapped[List["UsuarioMilitar"]] = relationship(back_populates="perfil")


class OrganizacaoMilitar(Base):
    __tablename__ = "organizacoes_militares"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    nome: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    sigla: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Indicadores atualizados automaticamente pelas regras de negócio
    qtd_militares: Mapped[int] = mapped_column(Integer, default=0)
    qtd_viaturas: Mapped[int] = mapped_column(Integer, default=0)
    qtd_apresentados: Mapped[int] = mapped_column(Integer, default=0)
    qtd_transferidos: Mapped[int] = mapped_column(Integer, default=0)

    # Relacionamentos
    militares: Mapped[List["UsuarioMilitar"]] = relationship(back_populates="organizacao_militar")


class UsuarioMilitar(Base):
    __tablename__ = "usuarios_militares"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    nome_completo: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    rg: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    
    organizacao_militar_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizacoes_militares.id"), nullable=False)
    possui_veiculo: Mapped[bool] = mapped_column(Boolean, default=False)
    data_apresentacao: Mapped[date] = mapped_column(Date, nullable=False)
    data_desligamento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    esta_ativo: Mapped[bool] = mapped_column(Boolean, default=True)

    # Credenciais de acesso ao sistema desktop (Apenas se for operador/admin)
    username: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    perfil_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("perfis.id"), nullable=True)

    # Relacionamentos
    organizacao_militar: Mapped["OrganizacaoMilitar"] = relationship(back_populates="militares")
    perfil: Mapped[Optional["Perfil"]] = relationship(back_populates="usuarios")
    veiculos: Mapped[List["Veiculo"]] = relationship(back_populates="proprietario")


class Veiculo(Base):
    __tablename__ = "veiculos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)  # Ex: Carro, Moto, Viatura
    modelo: Mapped[str] = mapped_column(String(80), nullable=False)
    placa: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    
    proprietario_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios_militares.id"), nullable=False)

    # Relacionamentos
    proprietario: Mapped["UsuarioMilitar"] = relationship(back_populates="veiculos")
    historicos: Mapped[List["HistoricoAcesso"]] = relationship(back_populates="veiculo")


class HistoricoAcesso(Base):
    __tablename__ = "historico_acessos"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    veiculo_id: Mapped[str] = mapped_column(String(36), ForeignKey("veiculos.id"), nullable=False, index=True)
    data_registro: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    hora_entrada: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    hora_saida: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Rastreabilidade de quem realizou o registro na portaria
    operador_entrada_id: Mapped[str] = mapped_column(String(36), ForeignKey("usuarios_militares.id"), nullable=False)
    operador_saida_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("usuarios_militares.id"), nullable=True)

    # Relacionamentos
    veiculo: Mapped["Veiculo"] = relationship(back_populates="historicos")


class LogSistema(Base):
    __tablename__ = "logs_sistema"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    nivel: Mapped[str] = mapped_column(String(15), nullable=False)  # INFO, WARN, ERROR
    mensagem: Mapped[str] = mapped_column(Text, nullable=False)
    usuario_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("usuarios_militares.id"), nullable=True)
    exception: Mapped[Optional[str]] = mapped_column(Text, nullable=True)




class RegistroAcesso(Base):
    __tablename__ = 'registros_acesso'

    id = Column(Integer, primary_key=True, autoincrement=True)
    militar_id = Column(Integer, ForeignKey('usuarios_militares.id'), nullable=False)
    
    # Tipo de movimentação: 'ENTRADA' ou 'SAÍDA'
    tipo = Column(String(10), nullable=False)
    data_hora = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Observações (ex: "Saiu de dispensa", "Entrada para o serviço")
    observacao = Column(String(255), nullable=True)

    # Relacionamento para conseguir buscar os dados do militar facilmente depois
    militar = relationship("UsuarioMilitar")


class RegistroViatura(Base):
    __tablename__ = 'registros_viatura'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Se o sistema aceitar viaturas civis/externas no futuro, a placa pode ser String direta. 
    # Para viaturas da OM, podemos associar ou manter histórico textual.
    viatura_placa = Column(String(20), nullable=False) 
    motorista_id = Column(Integer, ForeignKey('usuarios_militares.id'), nullable=False)
    chefe_viatura_id = Column(Integer, ForeignKey('usuarios_militares.id'), nullable=True)
    
    tipo = Column(String(10), nullable=False) # 'ENTRADA' ou 'SAÍDA'
    data_hora = Column(DateTime, default=datetime.utcnow, nullable=False)
    odometro = Column(Integer, nullable=True) # Quilometragem da viatura
    destino = Column(String(150), nullable=True)

    # Relacionamentos
    motorista = relationship("UsuarioMilitar", foreign_keys=[motorista_id])
    chefe_viatura = relationship("UsuarioMilitar", foreign_keys=[chefe_viatura_id])