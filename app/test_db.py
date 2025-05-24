from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import logging
from datetime import datetime, timedelta
from . import models, schemas, crud
from .db import get_db, engine

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        # Criar uma sessão de teste
        with Session(engine) as session:
            # Tenta fazer uma consulta simples
            result = session.execute(text("SELECT 1"))
            logger.info("✅ Conexão com o banco estabelecida com sucesso!")
            return True
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com o banco: {str(e)}")
        return False

def test_usuarios():
    """Testa operações na tabela de usuários"""
    try:
        with Session(engine) as session:
            # Conta usuários
            count = session.query(models.Usuario).count()
            logger.info(f"✅ Número de usuários no banco: {count}")
            
            # Lista usuários
            usuarios = session.query(models.Usuario).all()
            for user in usuarios:
                logger.info(f"  - {user.nome} ({user.email})")
            
            return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar tabela de usuários: {str(e)}")
        return False

def test_boletos():
    """Testa operações na tabela de boletos"""
    try:
        with Session(engine) as session:
            # Conta boletos
            count = session.query(models.Boleto).count()
            logger.info(f"✅ Número de boletos no banco: {count}")
            
            # Lista boletos
            boletos = session.query(models.Boleto).all()
            for boleto in boletos:
                logger.info(f"  - Boleto #{boleto.id}: R$ {boleto.valor} (Vencimento: {boleto.vencimento})")
            
            return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar tabela de boletos: {str(e)}")
        return False

def test_documentos():
    """Testa operações na tabela de documentos autorizados"""
    try:
        with Session(engine) as session:
            # Conta documentos
            count = session.query(models.DocumentoAutorizado).count()
            logger.info(f"✅ Número de documentos autorizados: {count}")
            
            # Lista documentos
            docs = session.query(models.DocumentoAutorizado).all()
            for doc in docs:
                logger.info(f"  - Documento #{doc.id}: {doc.tipo}")
            
            return True
    except Exception as e:
        logger.error(f"❌ Erro ao testar tabela de documentos: {str(e)}")
        return False

def run_all_tests():
    """Executa todos os testes"""
    logger.info("🔍 Iniciando testes do banco de dados...")
    
    tests = [
        ("Conexão com o banco", test_connection),
        ("Tabela de Usuários", test_usuarios),
        ("Tabela de Boletos", test_boletos),
        ("Tabela de Documentos", test_documentos)
    ]
    
    results = []
    for name, test_func in tests:
        logger.info(f"\n📋 Testando: {name}")
        result = test_func()
        results.append(result)
        
    # Resumo
    success = all(results)
    total = len(results)
    passed = sum(results)
    
    logger.info(f"\n📊 Resumo dos Testes:")
    logger.info(f"  ✓ Testes passaram: {passed}/{total}")
    logger.info(f"  ✗ Testes falharam: {total - passed}/{total}")
    
    return success

if __name__ == "__main__":
    run_all_tests() 