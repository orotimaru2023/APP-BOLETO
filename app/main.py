from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import Path, UploadFile, File
import csv
from io import StringIO
import json
import datetime
from . import db
from . import models
from . import schemas
from . import crud
from . import auth
from .db import Base, engine
from sqlalchemy import func

# Criar as tabelas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-app-boleto.vercel.app",
        "https://app-boleto-production.up.railway.app",
        "https://frontend-app-boleto-git-main-aldos-projects-e8f51764.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

# --------------------------
# DOCUMENTOS AUTORIZADOS
# --------------------------

@app.get("/documentos-autorizados", response_model=List[schemas.DocumentoAutorizado])
def listar_documentos_autorizados(
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if usuario.role == "admin":
        return db.query(models.DocumentoAutorizado).all()
    return db.query(models.DocumentoAutorizado).filter(
        models.DocumentoAutorizado.usuario_id == usuario.id
    ).all()


@app.post("/documentos-autorizados", response_model=schemas.DocumentoAutorizado)
def criar_documento_autorizado(
    doc: schemas.DocumentoAutorizadoCreate,
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Impede duplicidade para o mesmo usuário
    doc_existente = db.query(models.DocumentoAutorizado).filter_by(
        documento=doc.documento,
        usuario_id=usuario.id
    ).first()
    if doc_existente:
        raise HTTPException(status_code=400, detail="Documento já cadastrado.")

    novo_doc = models.DocumentoAutorizado(**doc.dict(), usuario_id=usuario.id)
    db.add(novo_doc)
    db.commit()
    db.refresh(novo_doc)
    return novo_doc

# --------------------------
# USUÁRIO & AUTENTICAÇÃO
# --------------------------

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": str(datetime.datetime.now())}

@app.get("/usuarios/me", response_model=schemas.UsuarioResponse)
def get_current_user(usuario=Depends(auth.get_current_user)):
    return usuario

@app.get("/")
def home():
    return {"status": "healthy", "message": "API de boletos funcionando com FastAPI!"}

@app.post("/register", response_model=schemas.UsuarioResponse)
def register(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.criar_usuario(db, usuario)

@app.post("/login", response_model=schemas.TokenData)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = auth.authenticate_user(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    access_token = auth.create_access_token(data={"sub": usuario.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --------------------------
# BOLETOS
# --------------------------

@app.get("/boletos", response_model=List[schemas.Boleto])
def listar_boletos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    order_by: Optional[str] = Query("vencimento"),
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Boleto).filter(models.Boleto.cpf_cnpj == usuario.cpf_cnpj)

    if order_by == "valor":
        query = query.order_by(models.Boleto.valor)
    elif order_by == "status":
        query = query.order_by(models.Boleto.status)
    else:
        query = query.order_by(models.Boleto.vencimento)

    boletos = query.offset(skip).limit(limit).all()
    return boletos

@app.post("/boletos", response_model=schemas.Boleto)
def criar_boleto(
    boleto: schemas.BoletoCreate,
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar boletos.")
    
    boleto_data = boleto.dict()
    boleto_data["usuario_id"] = usuario.id

    return crud.criar_boleto(db, boleto_data)

@app.put("/boletos/{boleto_id}", response_model=schemas.Boleto)
def atualizar_boleto_put(
    boleto_id: int = Path(..., description="ID do boleto a ser atualizado"),
    boleto_data: schemas.BoletoPut = ...,
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return crud.atualizar_boleto_put(db, usuario, boleto_id, boleto_data)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar boleto: {str(e)}")

@app.patch("/boletos/{boleto_id}", response_model=schemas.Boleto)
def atualizar_boleto_patch(
    boleto_id: int,
    dados_patch: schemas.BoletoUpdate,
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return crud.atualizar_boleto_patch(db, usuario, boleto_id, dados_patch)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao atualizar boleto: {str(e)}")

@app.delete("/boletos/{boleto_id}")
def deletar_boleto(
    boleto_id: int,
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return crud.deletar_boleto(db, usuario, boleto_id)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao deletar boleto: {str(e)}")

@app.get("/boletos/{boleto_id}", response_model=schemas.Boleto)
def obter_boleto_por_id(
    boleto_id: int,
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        return crud.obter_boleto_por_id(db, usuario, boleto_id)
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao obter boleto: {str(e)}")

@app.post("/importar-boletos-csv")
def importar_boletos_csv(
    arquivo: UploadFile = File(...),
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem importar boletos.")

    try:
        conteudo = arquivo.file.read().decode("utf-8")
        leitor = csv.DictReader(StringIO(conteudo))

        boletos = []
        for linha in leitor:
            data_vencimento = datetime.datetime.strptime(linha["vencimento"], "%Y-%m-%d").date()
            boleto = models.Boleto(
                usuario_id=usuario.id,
                cpf_cnpj=linha["cpf_cnpj"],
                valor=float(linha["valor"]),
                vencimento=data_vencimento,
                status=linha["status"],
                historico=json.loads(linha["historico"])
            )
            db.add(boleto)
            boletos.append(boleto)

        db.commit()
        return {"mensagem": f"{len(boletos)} boletos importados com sucesso."}
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar o arquivo: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao importar boletos: {str(e)}"
        )

@app.post("/importar-boletos-txt")
def importar_boletos_txt(
    arquivo: UploadFile = File(...),
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem importar boletos.")

    conteudo = arquivo.file.read().decode("utf-8")
    leitor = csv.DictReader(StringIO(conteudo), delimiter=",")

    boletos = []
    for linha in leitor:
        boleto = models.Boleto(
            usuario_id=usuario.id,
            cpf_cnpj=linha["cpf_cnpj"],
            valor=float(linha["valor"]),
            vencimento=linha["vencimento"],
            status=linha["status"],
            historico={"info": linha["historico"]}
        )
        db.add(boleto)
        boletos.append(boleto)

    db.commit()
    return {"mensagem": f"{len(boletos)} boletos importados com sucesso."}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        from .models import Usuario
        count = db.query(func.count(Usuario.id)).scalar()
        return {
            "message": "Conexão com o banco de dados estabelecida com sucesso!",
            "usuarios_cadastrados": count
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao conectar com o banco de dados: {str(e)}"
        )

@app.get("/admin/boletos", response_model=List[schemas.BoletoComUsuario])
def listar_todos_boletos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    order_by: Optional[str] = Query("vencimento"),
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if usuario.role != models.Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem acessar esta rota"
        )

    query = db.query(models.Boleto).join(models.Usuario)

    if order_by == "valor":
        query = query.order_by(models.Boleto.valor)
    elif order_by == "status":
        query = query.order_by(models.Boleto.status)
    elif order_by == "cpf_cnpj":
        query = query.order_by(models.Boleto.cpf_cnpj)
    else:
        query = query.order_by(models.Boleto.vencimento)

    total = query.count()
    boletos = query.offset(skip).limit(limit).all()
    
    return boletos
