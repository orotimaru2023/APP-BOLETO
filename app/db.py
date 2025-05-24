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
    # URL do Railway Production (usando endereço interno para a aplicação)
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:iQALhTglaVrojkoUdagaqVimiGoCsIpX@postgres.railway.internal:5432/railway"
    )
    logger.info("Conectando ao banco de dados de produção (Railway)")
else:
    # URL para desenvolvimento local (usando endereço público do Railway)
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:iQALhTglaVrojkoUdagaqVimiGoCsIpX@caboose.proxy.rlwy.net:21021/railway"
    logger.info("Conectando ao banco de dados de desenvolvimento (Railway)")

try:
    if ENVIRONMENT == "production":
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            echo=True
        )
    else:
        engine = create_engine(
            SQLALCHEMY_DATABASE_URL,
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
