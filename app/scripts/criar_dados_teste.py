from datetime import date, timedelta
import random
from sqlalchemy.orm import Session
import sys
import os

# Adiciona o diretório pai ao path para importar os módulos da aplicação
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.models import Usuario, Boleto, Role
from app.db import SessionLocal, engine
from app.auth import hash_password

def criar_usuarios_teste(db: Session):
    usuarios = []
    for i in range(10):
        senha_hash = hash_password(f"senha{i}")
        usuario = Usuario(
            nome=f"Usuário Teste {i}",
            email=f"usuario{i}@teste.com",
            senha=senha_hash,
            cpf_cnpj=f"{random.randint(10000000000, 99999999999)}",
            role=Role.USER
        )
        db.add(usuario)
        usuarios.append(usuario)
    
    db.commit()
    return usuarios

def criar_boletos_teste(db: Session, usuarios):
    status_opcoes = ["pendente", "pago", "cancelado"]
    
    for usuario in usuarios:
        # Criar um boleto para cada usuário
        data_vencimento = date.today() + timedelta(days=random.randint(1, 30))
        boleto = Boleto(
            usuario_id=usuario.id,
            cpf_cnpj=usuario.cpf_cnpj,
            valor=random.uniform(100.0, 1000.0),
            vencimento=data_vencimento,
            status=random.choice(status_opcoes),
            historico={"criacao": "Boleto de teste"}
        )
        db.add(boleto)
    
    db.commit()

def main():
    db = SessionLocal()
    try:
        # Criar usuários de teste
        usuarios = criar_usuarios_teste(db)
        print("10 usuários de teste criados com sucesso!")
        
        # Criar boletos de teste
        criar_boletos_teste(db, usuarios)
        print("10 boletos de teste criados com sucesso!")
        
    finally:
        db.close()

if __name__ == "__main__":
    main() 