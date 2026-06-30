import os
from datetime import date
from app.database.connection import engine, Base, SessionLocal
from app.models.models import Perfil, OrganizacaoMilitar, UsuarioMilitar
import bcrypt

def init_database():
    print("🔄 Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

    db = SessionLocal()
    try:
        # 1. Cria os perfis básicos
        if db.query(Perfil).count() == 0:
            print("🌱 Inserindo perfis padrão (Admin/Operador)...")
            perfil_admin = Perfil(nome="Administrador", slug="admin")
            perfil_operador = Perfil(nome="Operador", slug="operador")
            db.add_all([perfil_admin, perfil_operador])
            db.commit()
            print("✅ Perfis cadastrados!")

        # 2. Cria uma Organização Militar padrão
        if db.query(OrganizacaoMilitar).count() == 0:
            print("🌱 Criando Organização Militar padrão...")
            om_padrao = OrganizacaoMilitar(nome="Quartel General", sigla="QG")
            db.add(om_padrao)
            db.commit()
            # Força o SQLAlchemy a carregar o ID gerado pelo banco para a memória
            db.refresh(om_padrao) 
            print("✅ Organização Militar padrão cadastrada!")

        # 3. Cria o usuário Administrador padrão
        if db.query(UsuarioMilitar).filter_by(username="admin").first() is None:
            print("🌱 Criando usuário administrador inicial...")
            
            # Busca garantida: pega a primeira OM disponível no banco
            om = db.query(OrganizacaoMilitar).first()
            p_admin = db.query(Perfil).filter_by(slug="admin").first()

            if not om or not p_admin:
                raise Exception("Erro crítico: OM ou Perfil Admin não foram encontrados no banco.")

            password_plana = "admin123"
            salt = bcrypt.gensalt()
            password_hashed = bcrypt.hashpw(password_plana.encode('utf-8'), salt).decode('utf-8')

            admin_user = UsuarioMilitar(
                nome_completo="Administrador do Sistema",
                rg="000000000-0",
                data_nascimento=date(1990, 1, 1),
                organizacao_militar_id=om.id, # Agora garantido!
                possui_veiculo=False,
                data_apresentacao=date.today(),
                username="admin",
                password_hash=password_hashed,
                perfil_id=p_admin.id,
                esta_ativo=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Usuário 'admin' com a senha 'admin123' criado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao inicializar os dados no banco: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    print("\n🚀 Banco de dados configurado e pronto para o uso!")
