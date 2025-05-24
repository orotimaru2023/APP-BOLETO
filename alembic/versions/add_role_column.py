"""add role column

Revision ID: add_role_column
Revises: 
Create Date: 2024-02-24 14:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'add_role_column'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Criar o tipo enum se não existir
    op.execute(text("""
        DO $$ 
        BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'role') THEN
                CREATE TYPE role AS ENUM ('admin', 'user');
            END IF;
        END $$;
    """))
    
    # Adicionar a coluna role
    op.execute(text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS role role;"))
    
    # Atualizar usuários existentes
    op.execute(text("UPDATE usuarios SET role = 'admin'::role WHERE is_admin = true;"))
    op.execute(text("UPDATE usuarios SET role = 'user'::role WHERE is_admin = false OR is_admin IS NULL;"))
    
    # Configurar a coluna role
    op.execute(text("ALTER TABLE usuarios ALTER COLUMN role SET NOT NULL;"))
    op.execute(text("ALTER TABLE usuarios ALTER COLUMN role SET DEFAULT 'user'::role;"))

def downgrade():
    # Remover a coluna e o tipo enum
    op.execute(text("ALTER TABLE usuarios DROP COLUMN IF EXISTS role;"))
    op.execute(text("DROP TYPE IF EXISTS role;")) 