from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import HistoricoAcesso, Veiculo
from app.services.auth_service import AuthService

class AcessoService:
    def __init__(self, session: Session):
        """
        Recebe a sessão do banco de dados para gerenciar as operações de acesso.
        """
        self.session = session

    def obter_registro_ativo(self, veiculo_id: str) -> HistoricoAcesso | None:
        """
        Busca se existe alguma entrada ativa (sem hora de saída) para o veículo.
        Se retornar um registro, significa que o veículo está DENTRO do quartel.
        """
        return self.session.query(HistoricoAcesso).filter(
            HistoricoAcesso.veiculo_id == veiculo_id,
            HistoricoAcesso.hora_saida == None
        ).first()

    def registrar_entrada(self, placa: str) -> HistoricoAcesso:
        """
        Regra de Negócio: Verifica se o veículo existe e se já não está dentro.
        Se tudo estiver correto, registra a entrada na portaria.
        """
        # 1. Verifica se o veículo está cadastrado no sistema
        veiculo = self.session.query(Veiculo).filter(Veiculo.placa == placa).first()
        if not veiculo:
            raise ValueError(f"Veículo com placa {placa} não está cadastrado no sistema.")

        # 2. Verifica se o veículo já está dentro do quartel
        registro_ativo = self.obter_registro_ativo(veiculo.id)
        if registro_ativo:
            raise ValueError(f"Inconsistência: O veículo {placa} já se encontra dentro do quartel.")

        # 3. Obtém o operador logado no sistema para fins de auditoria
        operador = AuthService.obter_usuario_logado()
        if not operador:
            raise PermissionError("Nenhum operador logado no sistema para autorizar a entrada.")

        # 4. Cria o novo registro de histórico de acesso
        novo_acesso = HistoricoAcesso(
            veiculo_id=veiculo.id,
            operador_entrada_id=operador.id,
            hora_entrada=datetime.now()
        )

        self.session.add(novo_acesso)
        self.session.commit()
        self.session.refresh(novo_acesso)
        return novo_acesso

    def registrar_saida(self, placa: str) -> HistoricoAcesso:
        """
        Regra de Negócio: Localiza o veículo por placa, encontra a entrada ativa 
        e carimba o horário de saída.
        """
        # 1. Verifica se o veículo existe
        veiculo = self.session.query(Veiculo).filter(Veiculo.placa == placa).first()
        if not veiculo:
            raise ValueError(f"Veículo com placa {placa} não cadastrado.")

        # 2. Verifica se o veículo realmente tem uma entrada ativa para poder sair
        registro_ativo = self.obter_registro_ativo(veiculo.id)
        if not registro_ativo:
            raise ValueError(f"Inconsistência: O veículo {placa} não possui registro de entrada ativo.")

        # 3. Obtém o operador que está registrando a saída
        operador = AuthService.obter_usuario_logado()
        if not operador:
            raise PermissionError("Nenhum operador logado no sistema para autorizar a saída.")

        # 4. Atualiza o registro com a hora de saída e o operador responsável
        registro_ativo.hora_saida = datetime.now()
        registro_ativo.operador_saida_id = operador.id

        self.session.commit()
        self.session.refresh(registro_ativo)
        return registro_ativo