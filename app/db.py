import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import Engine

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do banco de dados
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # URL do Railway Production
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:iQALhTglaVrojkoUdagaqVimiGoCsIpX@monorail.proxy.rlwy.net:47938/railway"
    )
    logger.info("Conectando ao banco de dados de produção (Railway)")
else:
    # SQLite para desenvolvimento
    DATABASE_URL = "sqlite:///./test.db"
    logger.info("Conectando ao banco de dados de desenvolvimento (SQLite)")

try:
    if ENVIRONMENT == "production":
        engine = create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=True
        )
    else:
        engine = create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
            echo=True
        )
    
    # Testar conexão
    with engine.connect() as conn:
        logger.info("Conexão com o banco de dados estabelecida com sucesso!")
except Exception as e:
    logger.error(f"Erro ao conectar ao banco de dados: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para criar todas as tabelas
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {str(e)}")
        raise

# Adicionar listener para logs de conexão
@event.listens_for(Engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    logger.info("Nova conexão estabelecida com o banco de dados")
