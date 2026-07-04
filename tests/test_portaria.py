import pytest
from app.services.portaria_service import PortariaService
from app.models.models import OrganizacaoMilitar, RegistroAcesso

def test_registrar_entrada_militar_incrementa_contador(db_session):
    # Instancia o serviço usando o banco em memória
    service = PortariaService(db_session)
    
    # Executa a entrada do militar padrão criado no conftest
    registro = service.registrar_acesso_militar(militar_id="militar-123", tipo="ENTRADA")
    
    # Validações (Asserts)
    assert registro.id is not None
    assert registro.tipo == "ENTRADA"
    
    # Verifica se a quantidade de militares na OM subiu para 1
    om = db_session.query(OrganizacaoMilitar).filter(OrganizacaoMilitar.id == 1).first()
    assert om.qtd_militares == 1

def test_registrar_saida_militar_decrementa_contador(db_session):
    service = PortariaService(db_session)
    
    # Força o contador a começar em 1 para simular que ele já estava dentro
    om = db_session.query(OrganizacaoMilitar).filter(OrganizacaoMilitar.id == 1).first()
    om.qtd_militares = 1
    db_session.commit()
    
    # Executa a saída
    service.registrar_acesso_militar(militar_id="militar-123", tipo="SAÍDA")
    
    # Verifica se a quantidade de militares na OM voltou para 0
    assert om.qtd_militares == 0

def test_tipo_de_acesso_invalido_retorna_erro(db_session):
    service = PortariaService(db_session)
    
    # Garante que passar um tipo inválido levanta um ValueError
    with pytest.raises(ValueError):
        service.registrar_acesso_militar(militar_id="militar-123", tipo="INVALIDO")