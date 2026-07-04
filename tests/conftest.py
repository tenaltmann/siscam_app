import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, OrganizacaoMilitar, UsuarioMilitar
from datetime import date

@pytest.fixture(scope="function")
def db_session():
    """Cria um banco de dados em memória isolado para cada função de teste."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Cria uma Organização Militar padrão para os testes
    om_teste = OrganizacaoMilitar(
        id=1,
        nome="Batalhão de Testes",
        sigla="Btl Tst",
        qtd_militares=0,
        qtd_viaturas=0
    )
    session.add(om_teste)
    
    # Cria um Militar padrão para os testes
    militar_teste = UsuarioMilitar(
        id="militar-123",
        nome_completo=f"Soldado de Teste",
        rg="111222333",
        organizacao_militar_id=1,
        possui_veiculo=False,
        data_nascimento=date(2000, 1, 1),
        data_apresentacao=date.today(),
        esta_ativo=True
    )
    session.add(militar_teste)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(engine)