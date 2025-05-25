from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum

# --- ENUMS ---

class TipoDocumento(str, Enum):
    CPF = "CPF"
    CNPJ = "CNPJ"

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"

class StatusEnum(str, Enum):
    pendente = "pendente"
    pago = "pago"
    cancelado = "cancelado"

# --- DOCUMENTOS AUTORIZADOS ---

class DocumentoAutorizadoBase(BaseModel):
    tipo: TipoDocumento
    documento: str
    nome: str
    model_config = ConfigDict(from_attributes=True)

class DocumentoAutorizadoCreate(DocumentoAutorizadoBase):
    pass

class DocumentoAutorizado(DocumentoAutorizadoBase):
    id: int
    registrado: Optional[bool] = None  # Coloque como Optional se puder ser nulo no banco
    usuario_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

# --- USUÁRIO ---

class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    cpf_cnpj: str
    role: Role = Role.USER

class UsuarioCreate(UsuarioBase):
    senha: str

class Usuario(UsuarioBase):
    id: int
    role: Role

class UsuarioResponse(UsuarioBase):
    id: int
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)

# --- TOKEN ---

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    access_token: str
    token_type: str

# --- BOLETO ---

class BoletoBase(BaseModel):
    cpf_cnpj: str
    nome_empresa: str
    valor: float = Field(gt=0)
    vencimento: date
    status: StatusEnum
    observacao: Optional[str] = None
    historico: Dict[str, Any]
    model_config = ConfigDict(from_attributes=True)

    @property
    def validar_vencimento(self) -> date:
        if self.vencimento < date.today():
            raise ValueError("A data de vencimento não pode estar no passado.")
        return self.vencimento

class BoletoCreate(BoletoBase):
    pass

class Boleto(BoletoBase):
    id: int
    usuario_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class BoletoUpdate(BaseModel):
    nome_empresa: Optional[str] = None
    valor: Optional[float] = None
    vencimento: Optional[date] = None
    status: Optional[StatusEnum] = None
    observacao: Optional[str] = None
    historico: Optional[Dict[str, Any]] = None

class BoletoPut(BoletoBase):
    pass

class VerificacaoDocumento(BaseModel):
    autorizado: bool
    mensagem: Optional[str] = None

class BoletoComUsuario(BoletoBase):
    id: int
    usuario_id: int
    usuario: UsuarioResponse

    model_config = ConfigDict(from_attributes=True)
