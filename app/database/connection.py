import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Define o caminho do banco de dados na raiz do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"

# O Engine é o motor que gerencia a comunicação com o arquivo .db
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # Necessário para aplicações Desktop multi-thread
)

# O SessionLocal será usado para abrir e fechar conexões com o banco nas operações
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A Base será a classe mãe de todas as tabelas (Models) do sistema
Base = declarative_base()

def get_db():
    """Função utilitária para abrir e fechar a sessão do banco com segurança"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
