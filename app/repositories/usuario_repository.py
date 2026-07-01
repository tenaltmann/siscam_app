from sqlalchemy.orm import Session
from app.models.models import UsuarioMilitar
from app.core.security import gerar_hash_senha

class UsuarioRepository:
    def __init__(self, session: Session):
        """
        Recebe a sessão do SQLAlchemy via injeção de dependência.
        """
        self.session = session

    def salvar(self, usuario: UsuarioMilitar) -> UsuarioMilitar:
        """
        Salva um novo militar/usuário ou atualiza um existente.
        Garante que a senha (se fornecida) seja criptografada com o bcrypt antes de ir para o banco.
        """
        # Verifica se o password_hash foi preenchido com uma senha em texto claro
        # O bcrypt gera hashes que começam com '$2b$' ou '$2a$', se não começar, precisamos criptografar
        if usuario.password_hash and not usuario.password_hash.startswith("$2b$"):
            usuario.password_hash = gerar_hash_senha(usuario.password_hash)
            
        self.session.add(usuario)
        self.session.commit()
        self.session.refresh(usuario)
        return usuario

    def buscar_por_id(self, usuario_id: str) -> UsuarioMilitar | None:
        """Busca um militar pelo seu ID único (UUID string)."""
        return self.session.query(UsuarioMilitar).filter(UsuarioMilitar.id == usuario_id).first()

    def buscar_por_username(self, username: str) -> UsuarioMilitar | None:
        """
        Busca o usuário pelo username de acesso ao sistema desktop.
        Crucial para a etapa de autenticação (Login).
        """
        return self.session.query(UsuarioMilitar).filter(UsuarioMilitar.username == username).first()

    def buscar_por_rg(self, rg: str) -> UsuarioMilitar | None:
        """
        Busca um militar pelo número de RG.
        Útil para cadastros e buscas operacionais.
        """
        return self.session.query(UsuarioMilitar).filter(UsuarioMilitar.rg == rg).first()

    def listar_todos(self) -> list[UsuarioMilitar]:
        """Retorna a lista de todos os militares cadastrados."""
        return self.session.query(UsuarioMilitar).all()

    def deletar(self, usuario: UsuarioMilitar) -> None:
        """Remove o registro do banco de dados."""
        self.session.delete(usuario)
        self.session.commit()