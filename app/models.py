from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from db import Base

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    cpf_cnpj = Column(String, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    boletos = relationship("Boleto", back_populates="usuario")

class Boleto(Base):
    __tablename__ = 'boletos'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    cpf_cnpj = Column(String, index=True)
    valor = Column(Numeric(10, 2))
    vencimento = Column(Date)
    status = Column(String)
    historico = Column(JSON)
    usuario = relationship("Usuario", back_populates="boletos")
