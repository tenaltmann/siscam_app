from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import RegistroAcesso, RegistroViatura, UsuarioMilitar, OrganizacaoMilitar

class PortariaService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def registrar_acesso_militar(self, militar_id: str, tipo: str, observacao: str | None = None) -> RegistroAcesso:
        """
        Registra a entrada ou saída de um militar e atualiza o contador da OM.
        tipo: 'ENTRADA' ou 'SAÍDA'
        """
        if tipo not in ['ENTRADA', 'SAÍDA']:
            raise ValueError("Tipo de acesso inválido. Use 'ENTRADA' ou 'SAÍDA'.")

        # 1. Cria o registro de histórico
        novo_registro = RegistroAcesso(
            militar_id=militar_id,
            tipo=tipo,
            data_hora=datetime.now(),
            observacao=observacao
        )
        self.db.add(novo_registro)

        # 2. Busca o militar para encontrar a sua OM
        militar = self.db.query(UsuarioMilitar).filter(UsuarioMilitar.id == militar_id).first()
        if militar and militar.organizacao_militar_id:
            om = self.db.query(OrganizacaoMilitar).filter(OrganizacaoMilitar.id == militar.organizacao_militar_id).first()
            if om:
                # 3. Atualiza o contador de militares internos na OM
                if tipo == 'ENTRADA':
                    om.qtd_militares += 1
                elif tipo == 'SAÍDA' and om.qtd_militares > 0:
                    om.qtd_militares -= 1

        self.db.commit()
        return novo_registro

    def registrar_acesso_viatura(self, viatura_placa: str, motorista_id: str, tipo: str, 
                                 chefe_viatura_id: str | None = None, odometro: int | None = None, 
                                 destino: str | None = None) -> RegistroViatura:
        """
        Registra a entrada ou saída de uma viatura e atualiza o contador da OM do motorista.
        tipo: 'ENTRADA' ou 'SAÍDA'
        """
        if tipo not in ['ENTRADA', 'SAÍDA']:
            raise ValueError("Tipo de acesso inválido. Use 'ENTRADA' ou 'SAÍDA'.")

        # 1. Cria o registro de histórico da viatura
        novo_registro = RegistroViatura(
            viatura_placa=viatura_placa.upper(),
            motorista_id=motorista_id,
            chefe_viatura_id=chefe_viatura_id,
            tipo=tipo,
            data_hora=datetime.now(),
            odometro=odometro,
            destino=destino
        )
        self.db.add(novo_registro)

        # 2. Busca a OM do motorista para atualizar os indicadores da unidade
        motorista = self.db.query(UsuarioMilitar).filter(UsuarioMilitar.id == motorista_id).first()
        if motorista and motorista.organizacao_militar_id:
            om = self.db.query(OrganizacaoMilitar).filter(OrganizacaoMilitar.id == motorista.organizacao_militar_id).first()
            if om:
                # 3. Atualiza o contador de viaturas internas na OM
                if tipo == 'ENTRADA':
                    om.qtd_viaturas += 1
                elif tipo == 'SAÍDA' and om.qtd_viaturas > 0:
                    om.qtd_viaturas -= 1

        self.db.commit()
        return novo_registro