from app.utils.exception_handler import GlobalExceptionHandler

import sys
import os
from PySide6.QtWidgets import QApplication, QMessageBox
from datetime import date
from dotenv import load_dotenv

from app.database.connection import engine, Base, SessionLocal

from app.repositories.usuario_repository import UsuarioRepository

from app.core.security import gerar_hash_senha

from app.services.auth_service import AuthService
from app.services.om_service import OMService
from app.services.portaria_service import PortariaService

from app.views.login_view import LoginView
from app.views.main_view import MainView

from tests.conftest import db_session

from app.models.models import UsuarioMilitar, OrganizacaoMilitar

load_dotenv()

def inicializar_banco():
    """Garante a criação das tabelas no banco de dados SQLite."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        sys.exit(1)

def inicializar_dados_om_padrao(session, om_service):
    """Garante que exista pelo menos uma OM cadastrada para o Dashboard funcionar."""
    om_existente = session.query(OrganizacaoMilitar).filter(OrganizacaoMilitar.id == 1).first()
    if not om_existente:
        # Cria uma OM padrão fictícia para testes locais se não existir nenhuma
        nova_om = OrganizacaoMilitar(
            id=1,
            nome="OM de Teste",
            sigla="OM TST",
            qtd_militares=0,
            qtd_viaturas=0
        )
        session.add(nova_om)
        session.commit()

# Recupera apenas as credenciais de ACESSO do .env
    env_username = os.getenv("ADMIN_USERNAME")
    env_password = os.getenv("ADMIN_PASSWORD")

    # Validação rigorosa de segurança: garante que são strings e interrompe se forem None
    if env_username is None or env_password is None:
        raise ValueError(
            "ERRO CRÍTICO: As variáveis 'ADMIN_USERNAME' ou 'ADMIN_PASSWORD' "
            "não foram encontradas no arquivo .env do sistema."
        )

    # Verifica se já existe um operador com esse username cadastrado
    usuario_existente = session.query(UsuarioMilitar).filter(UsuarioMilitar.username == env_username).first()
    if not usuario_existente:
        novo_usuario = UsuarioMilitar(
            id="admin-master-id",
            nome_completo="Administrador do Sistema",
            
            # --- DADOS CADASTRAIS (Exigidos pelo banco, colocamos valores padrão) ---
            rg="00000000-0",                    # Apenas preenchendo o documento obrigatório
            data_nascimento=date(1990, 1, 1),
            data_apresentacao=date(2026, 1, 1),
            organizacao_militar_id="1",
            possui_veiculo=False,
            esta_ativo=True,
            
            # --- CREDENCIAIS DE LOGIN (O que a tela de login vai validar) ---
            username=env_username,              # Seu 'admin' vindo do .env
            password_hash=gerar_hash_senha(env_password), # Sua senha vinda do .env
            perfil_id=None                      
        )
        session.add(novo_usuario)
        session.commit()


    

def main():
    # 1. Inicializa a infraestrutura de dados
    inicializar_banco()
    db_session = SessionLocal()

    # 2. Inicializa os Repositórios e Serviços
    usuario_repo = UsuarioRepository(db_session)
    auth_service = AuthService(usuario_repo)
    om_service = OMService(db_session)
    portaria_service = PortariaService(db_session)
    exception_handler = GlobalExceptionHandler(db_session)

    # Configura o manipulador global de exceções para capturar erros não tratados
    sys.excepthook = exception_handler.handle_exception

    # Garante a existência da OM ID 1
    inicializar_dados_om_padrao(db_session, om_service)

    # 3. Inicializa a aplicação gráfica Qt
    app = QApplication(sys.argv)

    # Instancia as janelas da interface
    login_window = LoginView(auth_service)
    main_window = MainView(auth_service, om_service, portaria_service)

    # 4. ORQUESTRACAO DO FLUXO: Conecta o sucesso do login à abertura da janela principal
    def login_sucesso():
        login_window.close()       # Fecha a tela de login
        main_window.atualizar_dashboard() # Garante dados frescos na tela
        main_window.show()         # Abre a janela principal

    # Conecta o sinal que criamos no Passo 4.1 à função de transição
    login_window.login_sucesso.connect(login_sucesso)

    # Exibe a tela inicial (Login)
    login_window.show()

    # Executa o loop principal da aplicação gráfica
    sys.exit(app.exec())

if __name__ == "__main__":
    main()