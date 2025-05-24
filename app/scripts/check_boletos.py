import os
import sys
import logging
from sqlalchemy import text
from datetime import datetime

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
            # Buscar todos os boletos com informações do usuário
            result = conn.execute(text("""
                SELECT 
                    b.id,
                    b.cpf_cnpj,
                    b.nome_empresa,
                    b.valor,
                    b.vencimento,
                    b.status,
                    b.observacao,
                    b.historico,
                    u.nome as nome_usuario,
                    u.email as email_usuario
                FROM boletos b
                JOIN usuarios u ON b.usuario_id = u.id
                ORDER BY b.id;
            """))
            
            boletos = result.fetchall()
            
            print("\nBoletos no sistema:")
            print("===================")
            for boleto in boletos:
                print(f"\nID: {boleto.id}")
                print(f"Empresa: {boleto.nome_empresa}")
                print(f"CPF/CNPJ: {boleto.cpf_cnpj}")
                print(f"Valor: R$ {boleto.valor:.2f}")
                print(f"Vencimento: {boleto.vencimento.strftime('%d/%m/%Y')}")
                print(f"Status: {boleto.status}")
                print(f"Observação: {boleto.observacao or 'Nenhuma'}")
                print(f"Histórico: {boleto.historico}")
                print(f"Usuário: {boleto.nome_usuario} ({boleto.email_usuario})")
                print("-" * 50)
            
            print(f"\nTotal de boletos: {len(boletos)}")
            
    except Exception as e:
        logger.error(f"Erro ao verificar boletos: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}")
        sys.exit(1) 