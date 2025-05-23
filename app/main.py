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
import db, models, schemas, crud, auth
from db import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-app-boleto.vercel.app",
        "https://app-boleto-production.up.railway.app",
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

@app.get("/")
def home():
    return {"mensagem": "API de boletos funcionando com FastAPI!"}

@app.post("/register", response_model=schemas.UsuarioOut)
def register(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.criar_usuario(db, usuario)

@app.post("/login", response_model=schemas.TokenData)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = auth.authenticate_user(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    access_token = auth.create_access_token(data={"sub": usuario.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/boletos", response_model=List[schemas.BoletoOut])
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

@app.post("/boletos", response_model=schemas.BoletoOut)
def criar_boleto(
    boleto: schemas.BoletoCreate,
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem criar boletos.")
    
    boleto_data = boleto.dict()
    boleto_data["usuario_id"] = usuario.id  # <-- Adiciona o campo!

    return crud.criar_boleto(db, boleto_data)

@app.put("/boletos/{boleto_id}", response_model=schemas.BoletoOut)
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
    

@app.post("/importar-boletos-csv")
def importar_boletos_csv(
    arquivo: UploadFile = File(...),
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem importar boletos.")

    conteudo = arquivo.file.read().decode("utf-8")
    leitor = csv.DictReader(StringIO(conteudo))

    boletos = []
    for linha in leitor:
        boleto = models.Boleto(
            usuario_id=usuario.id,
            cpf_cnpj=linha["cpf_cnpj"],
            valor=float(linha["valor"]),
            vencimento=linha["vencimento"],
            status=linha["status"],
            historico=json.loads(linha["historico"])
        )
        db.add(boleto)
        boletos.append(boleto)

    db.commit()
    return {"mensagem": f"{len(boletos)} boletos importados com sucesso."}


@app.post("/importar-boletos-txt")
def importar_boletos_txt(
    arquivo: UploadFile = File(...),
    usuario=Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if not usuario.is_admin:
        raise HTTPException(status_code=403, detail="Apenas administradores podem importar boletos.")

    conteudo = arquivo.file.read().decode("utf-8")
    leitor = csv.DictReader(StringIO(conteudo), delimiter=",")  # Altere o delimitador se necessário

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

@app.patch("/boletos/{boleto_id}", response_model=schemas.BoletoOut)
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

@app.get("/boletos/{boleto_id}", response_model=schemas.BoletoOut)
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
