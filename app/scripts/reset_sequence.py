import os
import sys
import logging
from sqlalchemy import text

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adiciona o diretório pai ao path para importar os módulos da aplicação
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db import engine

def main():
    try:
        # Criar conexão
        with engine.connect() as conn:
            # Verificar o último ID usado
            result = conn.execute(text("""
                SELECT COALESCE(MAX(id), 0) + 1 as next_id
                FROM boletos;
            """))
            next_id = result.scalar()
            
            # Reiniciar a sequência
            logger.info(f"Reiniciando a sequência para começar em {next_id}...")
            conn.execute(text("""
                ALTER SEQUENCE boletos_id_seq RESTART WITH :next_id;
            """), {"next_id": next_id})
            
            conn.commit()
            logger.info("Sequência reiniciada com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro ao reiniciar a sequência: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        sys.exit(1) 