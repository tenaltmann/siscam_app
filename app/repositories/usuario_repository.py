from sqlalchemy.orm import Session
from app.models.models import UsuarioMilitar
from app.core.security import gerar_hash_senha
from app.services.om_service import OMService

class UsuarioRepository:
    def __init__(self, session: Session):
        """
        Recebe a sessão do SQLAlchemy via injeção de dependência.
        """
        self.session = session
        # Inicializa o serviço de OM internamente para atualizar os contadores
        self.om_service = OMService(session)

    def salvar(self, usuario: UsuarioMilitar) -> UsuarioMilitar:
        """
        Salva um novo militar/usuário ou atualiza um existente.
        Garante que a senha seja criptografada e atualiza os contadores da OM.
        """
        # 1. Criptografia de senha com bcrypt se necessário
        if usuario.password_hash and not usuario.password_hash.startswith("$2b$"):
            usuario.password_hash = gerar_hash_senha(usuario.password_hash)
            
        # 2. Salva o militar no banco de dados
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)

        # 3. AUTOMAÇÃO (Passo 3.3): Atualiza os contadores da OM à qual este militar pertence
        if usuario.organizacao_militar_id:
            self.om_service.atualizar_contadores(usuario.organizacao_militar_id)

        return usuario

    def buscar_por_id(self, usuario_id: str) -> UsuarioMilitar | None:
        """Busca um militar pelo seu ID único (UUID string)."""
        return self.session.query(UsuarioMilitar).filter(UsuarioMilitar.id == usuario_id).first()

    def buscar_por_username(self, username: str) -> UsuarioMilitar | None:
        """Busca o usuário pelo username de acesso ao sistema desktop."""
        return self.session.query(UsuarioMilitar).filter(UsuarioMilitar.username == username).first()

    def buscar_por_rg(self, rg: str) -> UsuarioMilitar | None:
        """Busca um militar pelo número de RG."""
        return self.session.query(UsuarioMilitar).filter(UsuarioMilitar.rg == rg).first()

    def listar_todos(self) -> list[UsuarioMilitar]:
        """Retorna a lista de todos os militares cadastrados."""
        return self.session.query(UsuarioMilitar).all()

    def deletar(self, usuario: UsuarioMilitar) -> None:
        """Remove o registro do banco de dados e atualiza os contadores da OM."""
        om_id = usuario.organizacao_militar_id
        
        self.session.delete(usuario)
        self.session.commit()

        # Atualiza os contadores após a remoção
        if om_id:
            self.om_service.atualizar_contadores(om_id)