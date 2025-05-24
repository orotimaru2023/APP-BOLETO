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
            # Verificar a estrutura da tabela
            logger.info("Verificando a estrutura da tabela boletos...")
            result = conn.execute(text("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = 'boletos'
                ORDER BY ordinal_position;
            """))
            
            print("\nEstrutura da tabela boletos:")
            print("-----------------------------")
            for row in result:
                print(f"Coluna: {row[0]}")
                print(f"Tipo: {row[1]}")
                if row[2]:
                    print(f"Tamanho máximo: {row[2]}")
                print("-----------------------------")
            
    except Exception as e:
        logger.error(f"Erro ao verificar a tabela: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        sys.exit(1) 