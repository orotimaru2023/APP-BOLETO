from db import engine, Base, SessionLocal
from models import Usuario, Role
from passlib.context import CryptContext
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user(db):
    # Verifica se já existe um usuário admin
    admin = db.query(Usuario).filter(Usuario.role == Role.ADMIN).first()
    if not admin:
        # Cria o usuário admin com as credenciais do ambiente
        admin_user = Usuario(
            nome="Administrador",
            email=os.getenv("ADMIN_EMAIL", "admin@example.com"),
            senha=pwd_context.hash(os.getenv("ADMIN_PASSWORD", "admin123")),
            documento=os.getenv("ADMIN_DOCUMENTO", "00000000000"),
            role=Role.ADMIN
        )
        db.add(admin_user)
        db.commit()
        print("Usuário admin criado com sucesso!")
    else:
        print("Usuário admin já existe!")

def init_db():
    try:
        # Cria todas as tabelas
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso!")
        
        # Cria a sessão
        db = SessionLocal()
        try:
            # Cria o usuário admin
            create_admin_user(db)
        finally:
            db.close()
            
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")

if __name__ == "__main__":
    init_db() 