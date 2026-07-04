from app.utils.exception_handler import GlobalExceptionHandler

import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from app.database.connection import engine, Base, SessionLocal

from app.repositories.usuario_repository import UsuarioRepository

from app.services.auth_service import AuthService
from app.services.om_service import OMService
from app.services.portaria_service import PortariaService

from app.views.login_view import LoginView
from app.views.main_view import MainView

def inicializar_banco():
    """Garante a criação das tabelas no banco de dados SQLite."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        sys.exit(1)

def inicializar_dados_om_padrao(session, om_service):
    """Garante que exista pelo menos uma OM cadastrada para o Dashboard funcionar."""
    from app.models.models import OrganizacaoMilitar
    om_existente = session.query(OrganizacaoMilitar).filter(OrganizacaoMilitar.id == 1).first()
    if not om_existente:
        # Cria uma OM padrão fictícia para testes locais se não existir nenhuma
        nova_om = OrganizacaoMilitar(
            id=1,
            nome_om="OM de Teste",
            total_militares_internos=0,
            total_viaturas_internas=0
        )
        session.add(nova_om)
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