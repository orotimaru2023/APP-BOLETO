from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import Path, HTTPException
from fastapi import UploadFile, File
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

@app.get("/boletos", response_model=List[schemas.Boleto])
def listar_boletos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    order_by: Optional[str] = Query("vencimento"),
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Boleto).filter(models.Boleto.cpf_cnpj == usuario.cpf_cnpj)

    # Ordenação básica por coluna
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
            # Converter a data de vencimento para o formato correto
            data_vencimento = datetime.datetime.strptime(linha["vencimento"], "%Y-%m-%d").date()
            
            # Criar o boleto sem especificar o ID
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
        # Tenta fazer uma consulta usando o ORM
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

    # Ordenação básica por coluna
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
