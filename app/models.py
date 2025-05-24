from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, JSON, Boolean, Enum
from sqlalchemy.orm import relationship
from .db import Base
import enum

class TipoDocumento(str, enum.Enum):
    CPF = "CPF"
    CNPJ = "CNPJ"

class Role(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class DocumentoAutorizado(Base):
    __tablename__ = 'documentos_autorizados'
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoDocumento), nullable=False)
    documento = Column(String, unique=True, nullable=False)
    nome = Column(String, nullable=False)
    registrado = Column(Boolean, default=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    usuario = relationship("Usuario", back_populates="documento_autorizado")

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    cpf_cnpj = Column(String, unique=True, nullable=False)
    role = Column(Enum(Role), default=Role.USER, nullable=False)
    boletos = relationship("Boleto", back_populates="usuario")
    documento_autorizado = relationship("DocumentoAutorizado", back_populates="usuario", uselist=False)

class Boleto(Base):
    __tablename__ = 'boletos'
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    cpf_cnpj = Column(String, nullable=False)
    valor = Column(Numeric(10, 2))
    vencimento = Column(Date)
    status = Column(String)
    descricao = Column(String, nullable=True)
    historico = Column(JSON, nullable=True)
    usuario = relationship("Usuario", back_populates="boletos")
