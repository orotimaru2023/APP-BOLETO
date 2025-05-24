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
            # Adicionar coluna nome_empresa
            logger.info("Adicionando coluna 'nome_empresa'...")
            conn.execute(text("""
                ALTER TABLE boletos
                ADD COLUMN IF NOT EXISTS nome_empresa VARCHAR(255);
            """))
            
            # Adicionar índice para nome_empresa
            logger.info("Criando índice para 'nome_empresa'...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_boletos_nome_empresa
                ON boletos (nome_empresa);
            """))
            
            # Adicionar coluna observacao
            logger.info("Adicionando coluna 'observacao'...")
            conn.execute(text("""
                ALTER TABLE boletos
                ADD COLUMN IF NOT EXISTS observacao TEXT;
            """))
            
            # Atualizar registros existentes com nome da empresa baseado no CPF/CNPJ
            logger.info("Atualizando registros existentes...")
            conn.execute(text("""
                UPDATE boletos
                SET nome_empresa = 'Empresa ' || cpf_cnpj
                WHERE nome_empresa IS NULL;
            """))
            
            conn.commit()
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