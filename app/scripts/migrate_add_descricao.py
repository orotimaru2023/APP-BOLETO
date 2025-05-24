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
            # Verificar se a coluna já existe
            logger.info("Verificando se a coluna 'descricao' existe...")
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'boletos' AND column_name = 'descricao';
            """))
            
            if not result.fetchone():
                # Adicionar a coluna descricao
                logger.info("Adicionando coluna 'descricao' à tabela boletos...")
                conn.execute(text("""
                    ALTER TABLE boletos
                    ADD COLUMN IF NOT EXISTS descricao VARCHAR(255);
                """))
                conn.commit()
                logger.info("Coluna 'descricao' adicionada com sucesso!")
            else:
                logger.info("A coluna 'descricao' já existe na tabela boletos.")
            
            logger.info("Migração concluída com sucesso!")
            
    except Exception as e:
        logger.error(f"Erro ao executar a migração: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        sys.exit(1) 