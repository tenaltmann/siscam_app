from app.repositories.usuario_repository import UsuarioRepository
from app.core.security import verificar_senha
from app.models.models import UsuarioMilitar

class AuthService:
    # Atributo de classe para manter o operador logado na sessão do sistema Desktop
    _usuario_logado: UsuarioMilitar | None = None

    def __init__(self, usuario_repo: UsuarioRepository):
        """
        Recebe o repositório de usuários por injeção de dependência.
        """
        self.usuario_repo = usuario_repo

    def realizar_login(self, username: str, senha_plana: str) -> bool:
        """
        Valida as credenciais do usuário. 
        Se estiverem corretas, inicia a sessão do sistema guardando o usuário ativo.
        """
        # 1. Busca o usuário pelo username no banco de dados
        usuario = self.usuario_repo.buscar_por_username(username)
        if not usuario:
            return False  # Usuário não encontrado

        # 2. Se o usuário existir, mas não estiver ativo (ex: transferido), barra o login
        if not usuario.esta_ativo:
            return False

        # 3. GARANTIA DE TIPO: Se o usuário não tiver hash de senha cadastrado, barra o acesso
        if usuario.password_hash is None:
            return False

        # 4. Agora o Python sabe que usuario.password_hash é 100% str (não é mais str | None)
        if verificar_senha(senha_plana, usuario.password_hash):
            AuthService._usuario_logado = usuario  # Define a sessão ativa
            return True
        
        return False  # Senha incorreta

    @classmethod
    def obter_usuario_logado(cls) -> UsuarioMilitar | None:
        """
        Retorna o usuário que está logado atualmente no sistema.
        Útil para auditoria (logs) e checagem de permissões de perfil.
        """
        return cls._usuario_logado

    @classmethod
    def realizar_logout(cls) -> None:
        """
        Encerra a sessão atual do operador no sistema desktop.
        """
        cls._usuario_logado = None