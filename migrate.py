import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Configuração da conexão
conn = psycopg2.connect(
    "postgresql://postgres:iQALhTglaVrojkoUdagaqVimiGoCsIpX@caboose.proxy.rlwy.net:21021/railway"
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# Criar cursor
cur = conn.cursor()

try:
    # Remover a coluna role se existir
    cur.execute("""
        ALTER TABLE usuarios DROP COLUMN IF EXISTS role;
    """)
    print("Coluna 'role' removida!")
    
    # Remover o tipo enum se existir
    cur.execute("""
        DROP TYPE IF EXISTS role;
    """)
    print("Tipo enum 'role' removido!")
    
    # Criar tipo enum
    cur.execute("""
        CREATE TYPE role AS ENUM ('ADMIN', 'USER');
    """)
    print("Tipo enum 'role' criado com sucesso!")
    
    # Adicionar coluna role
    cur.execute("""
        ALTER TABLE usuarios ADD COLUMN role role DEFAULT 'USER'::role;
    """)
    print("Coluna 'role' adicionada com sucesso!")
    
    # Verificar valores atuais
    cur.execute("SELECT id, nome, is_admin FROM usuarios")
    rows = cur.fetchall()
    print("\nValores atuais:")
    for row in rows:
        print(row)
    
    # Atualizar usuários existentes
    cur.execute("UPDATE usuarios SET role = 'ADMIN'::role WHERE is_admin = true")
    cur.execute("UPDATE usuarios SET role = 'USER'::role WHERE is_admin = false OR is_admin IS NULL")
    print("\nUsuários atualizados com sucesso!")
    
    # Verificar valores após atualização
    cur.execute("SELECT id, nome, is_admin, role FROM usuarios")
    rows = cur.fetchall()
    print("\nValores após atualização:")
    for row in rows:
        print(row)
    
    # Configurar a coluna role
    cur.execute("ALTER TABLE usuarios ALTER COLUMN role SET NOT NULL")
    print("\nMigração concluída com sucesso!")

except Exception as e:
    print(f"\nErro durante a migração: {str(e)}")
    conn.rollback()

finally:
    cur.close()
    conn.close() 