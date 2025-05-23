from sqlalchemy.orm import Session
from fastapi import HTTPException
import models, schemas, auth
from typing import Optional

def criar_usuario(db: Session, usuario: schemas.UsuarioCreate):
    usuario_existente = db.query(models.Usuario).filter(
        (models.Usuario.email == usuario.email) |
        (models.Usuario.cpf_cnpj == usuario.cpf_cnpj)
    ).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Usuário já existe.")
    hashed = auth.hash_password(usuario.senha)
    novo_usuario = models.Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=hashed,
        cpf_cnpj=usuario.cpf_cnpj
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario

def listar_boletos_por_cpf_cnpj(db: Session, cpf_cnpj: str, local_kw: Optional[str] = None):
    query = db.query(models.Boleto).filter(models.Boleto.cpf_cnpj == cpf_cnpj)
    if local_kw:
        query = query.filter(models.Boleto.status.ilike(f"%{local_kw}%"))
    return query.all()

def criar_boleto(db: Session, boleto_data: dict):
    existe = db.query(models.Boleto).filter_by(
        cpf_cnpj=boleto_data["cpf_cnpj"],
        valor=boleto_data["valor"],
        vencimento=boleto_data["vencimento"],
        status=boleto_data["status"]
    ).first()
    if existe:
        raise HTTPException(status_code=400, detail="Boleto duplicado.")
    novo_boleto = models.Boleto(**boleto_data)
    db.add(novo_boleto)
    db.commit()
    db.refresh(novo_boleto)
    return novo_boleto

def atualizar_boleto_put(db: Session, usuario, boleto_id: int, boleto_data: schemas.BoletoPut):
    if not usuario.is_admin:
        raise PermissionError("Apenas administradores podem atualizar boletos.")
    boleto = db.query(models.Boleto).filter_by(id=boleto_id).first()
    if not boleto:
        raise ValueError("Boleto não encontrado.")
    boleto.cpf_cnpj = boleto_data.cpf_cnpj
    boleto.valor = boleto_data.valor
    boleto.vencimento = boleto_data.vencimento
    boleto.status = boleto_data.status
    boleto.historico = boleto_data.historico
    db.commit()
    db.refresh(boleto)
    return boleto

def atualizar_boleto_patch(db: Session, usuario, boleto_id: int, dados_patch: schemas.BoletoUpdate):
    if not usuario.is_admin:
        raise PermissionError("Apenas administradores podem editar boletos.")
    boleto = db.query(models.Boleto).filter_by(id=boleto_id).first()
    if not boleto:
        raise ValueError("Boleto não encontrado.")
    if dados_patch.valor is not None:
        boleto.valor = dados_patch.valor
    if dados_patch.vencimento is not None:
        boleto.vencimento = dados_patch.vencimento
    if dados_patch.status is not None:
        boleto.status = dados_patch.status
    if dados_patch.historico is not None:
        boleto.historico = dados_patch.historico
    db.commit()
    db.refresh(boleto)
    return boleto

def deletar_boleto(db: Session, usuario, boleto_id: int):
    if not usuario.is_admin:
        raise PermissionError("Apenas administradores podem excluir boletos.")
    boleto = db.query(models.Boleto).filter_by(id=boleto_id).first()
    if not boleto:
        raise ValueError("Boleto não encontrado.")
    db.delete(boleto)
    db.commit()
    return {"mensagem": f"Boleto {boleto_id} deletado com sucesso."}

def obter_boleto_por_id(db: Session, usuario, boleto_id: int):
    boleto = db.query(models.Boleto).filter_by(id=boleto_id).first()
    if not boleto:
        raise ValueError("Boleto não encontrado.")
    if not usuario.is_admin and boleto.cpf_cnpj != usuario.cpf_cnpj:
        raise PermissionError("Você não tem permissão para acessar este boleto.")
    return boleto
