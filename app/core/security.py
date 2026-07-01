import bcrypt

def gerar_hash_senha(senha_plana: str) -> str:
    """
    Recebe uma senha em texto claro, gera um salt aleatório e
    retorna o hash seguro como uma string codificada em UTF-8.
    """
    if not senha_plana:
        raise ValueError("A senha não pode estar vazia.")

    # Converte a senha de string para bytes
    senha_bytes = senha_plana.encode('utf-8')
    
    # Gera o salt e o hash (o bcrypt faz ambos juntos)
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(senha_bytes, salt)
    
    # Retorna o hash como string para ser salvo no banco de dados
    return hash_bytes.decode('utf-8')


def verificar_senha(senha_plana: str, senha_hash_armazenado: str) -> bool:
    """
    Compara uma senha digitada (texto claro) com o hash salvo no banco.
    Retorna True se as senhas forem iguais, e False caso contrário.
    """
    try:
        # Converte as strings para os formatos de bytes exigidos pelo bcrypt
        senha_bytes = senha_plana.encode('utf-8')
        hash_bytes = senha_hash_armazenado.encode('utf-8')
        
        # O bcrypt extrai o salt automaticamente do hash armazenado e compara
        return bcrypt.checkpw(senha_bytes, hash_bytes)
    except Exception:
        # Caso ocorra algum erro de formatação no hash do banco
        return False