from sqlalchemy.orm import Session
from app.models.models import OrganizacaoMilitar, UsuarioMilitar, Veiculo

class OMService:
    def __init__(self, session: Session):
        self.session = session

    def atualizar_contadores(self, om_id: str) -> None:
        """
        Regra de Negócio: Recalcula e atualiza o total de militares e 
        viaturas cadastrados para uma determinada OM específica.
        """
        om = self.session.query(OrganizacaoMilitar).filter(OrganizacaoMilitar.id == om_id).first()
        if not om:
            return

        # 1. Conta quantos militares estão cadastrados e ativos nesta OM
        total_militares = self.session.query(UsuarioMilitar).filter(
            UsuarioMilitar.organizacao_militar_id == om_id,
            UsuarioMilitar.esta_ativo == True
        ).count()

        # 2. Conta quantas viaturas/veículos estão vinculados a militares desta OM
        total_viaturas = self.session.query(Veiculo).join(UsuarioMilitar).filter(
            UsuarioMilitar.organizacao_militar_id == om_id
        ).count()

        # 3. Atualiza os campos do modelo
        om.qtd_militares = total_militares
        om.qtd_viaturas = total_viaturas

        self.session.commit()