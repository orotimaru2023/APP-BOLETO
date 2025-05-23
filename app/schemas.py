from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from enum import Enum
from datetime import date
from pydantic import validator

# --- USUÁRIO ---

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    cpf_cnpj: str

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioOut(UsuarioBase):
    id: int
    is_admin: bool

    class Config:
        orm_mode = True

# --- AUTENTICAÇÃO ---

class LoginData(BaseModel):
    email: EmailStr
    senha: str

class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- BOLETO ---

class BoletoBase(BaseModel):
    cpf_cnpj: str
    valor: float
    vencimento: date
    status: str
    historico: Optional[dict] = {}

class BoletoCreate(BoletoBase):
    pass

class BoletoOut(BoletoBase):
    id: int

    class Config:
        orm_mode = True

class BoletoUpdate(BaseModel):
    valor: Optional[float] = None
    vencimento: Optional[date] = None
    status: Optional[str] = None
    historico: Optional[dict] = None

    # schemas.py
from pydantic import BaseModel
from datetime import date

class BoletoPut(BaseModel):
    cpf_cnpj: str
    valor: float
    vencimento: date
    status: str
    historico: dict

class StatusEnum(str, Enum):
    pendente = "pendente"
    pago = "pago"
    cancelado = "cancelado"

status: StatusEnum

class BoletoBase(BaseModel):
    cpf_cnpj: str
    valor: float
    vencimento: date
    status: StatusEnum
    historico: Optional[dict] = {}

    @validator("vencimento")
    def validar_vencimento(cls, v):
        if v < date.today():
            raise ValueError("A data de vencimento não pode estar no passado.")
        return v