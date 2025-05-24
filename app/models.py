from sqlalchemy import Column, Integer, String, Float, Date, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .db import Base
from enum import Enum as PyEnum

class TipoDocumento(str, PyEnum):
    CPF = "CPF"
    CNPJ = "CNPJ"

class Role(PyEnum):
    ADMIN = "admin"
    USER = "user"

class DocumentoAutorizado(Base):
    __tablename__ = 'documentos_autorizados'
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String)
    documento = Column(String)
    nome = Column(String)
    registrado = Column(Date)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    usuario = relationship("Usuario", back_populates="documento_autorizado")

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha = Column(String)
    cpf_cnpj = Column(String, unique=True, index=True)
    is_admin = Column(Boolean, default=False)
    role = Column(Enum(Role), default=Role.USER)
    boletos = relationship("Boleto", back_populates="usuario")
    documento_autorizado = relationship("DocumentoAutorizado", back_populates="usuario", uselist=False)

class Boleto(Base):
    __tablename__ = 'boletos'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    cpf_cnpj = Column(String, index=True)
    nome_empresa = Column(String, index=True)
    valor = Column(Float)
    vencimento = Column(Date)
    status = Column(String)
    observacao = Column(String, nullable=True)
    historico = Column(JSON)
    usuario = relationship("Usuario", back_populates="boletos")
