from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import sqlite3
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def inicializar_bd():
    conn = sqlite3.connect("agendazap.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dados TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM configuracoes")
    if cursor.fetchone()[0] == 0:
        dados_iniciais = {
            "nomeBarbearia": "Barbearia Yukio",
            "logoBarbearia": "",
            "whatsYukio": "",
            "instagramYukio": "",
            "telegramYukio": "",
            "senhaYukio": "1234",
            "servicos": [
                {"id": "corte", "nome": "Corte de Cabelo", "preco": 3000, "duracao": 50},
                {"id": "combo", "nome": "Corte + Barba", "preco": 4500, "duracao": 80}
            ],
            "diasFechados": [],
            "horariosPausaPadrao": [],
            "horariosBloqueadosPorData": {},
            "agendamentos": []
        }
        cursor.execute("INSERT INTO configuracoes (dados) VALUES (?)", (json.dumps(dados_iniciais),))
        conn.commit()
    conn.close()

inicializar_bd()

def carregar_do_bd():
    conn = sqlite3.connect("agendazap.db")
    cursor = conn.cursor()
    cursor.execute("SELECT dados FROM configuracoes ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return {}

def salvar_no_bd(dados):
    conn = sqlite3.connect("agendazap.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM configuracoes")
    cursor.execute("INSERT INTO configuracoes (dados) VALUES (?)", (json.dumps(dados),))
    conn.commit()
    conn.close()

class Agendamento(BaseModel):
    cliente: str
    servico: str
    preco: int
    data: str
    horario: str
    whatsapp: str

class Configuracao(BaseModel):
    nomeBarbearia: Optional[str] = None
    logoBarbearia: Optional[str] = None
    whatsYukio: Optional[str] = None
    instagramYukio: Optional[str] = None
    telegramYukio: Optional[str] = None
    senhaYukio: Optional[str] = None
    servicos: Optional[List[dict]] = None
    diasFechados: Optional[List[int]] = None
    horariosPausaPadrao: Optional[List[str]] = None  # <--- ESSENCIAL PARA GUARDAR AS PAUSAS
    horariosBloqueadosPorData: Optional[Dict[str, List[str]]] = None
    agendamentos: Optional[List[dict]] = None

@app.get("/api/dados")
def obter_dados():
    return carregar_do_bd()

@app.post("/api/agendar")
def realizar_agendamento(agendamento: Agendamento):
    db = carregar_do_bd()
    if "agendamentos" not in db:
        db["agendamentos"] = []
    db["agendamentos"].append(agendamento.dict())
    
    if "horariosBloqueadosPorData" not in db:
        db["horariosBloqueadosPorData"] = {}
    if agendamento.data not in db["horariosBloqueadosPorData"]:
        db["horariosBloqueadosPorData"][agendamento.data] = []
        
    if agendamento.horario not in db["horariosBloqueadosPorData"][agendamento.data]:
        db["horariosBloqueadosPorData"][agendamento.data].append(agendamento.horario)
        
    salvar_no_bd(db)
    return {"sucesso": True, "mensagem": "Agendamento confirmado!"}

@app.post("/api/configurar")
def atualizar_configuracao(config: Configuracao):
    db = carregar_do_bd()
    
    if config.nomeBarbearia is not None:
        db["nomeBarbearia"] = config.nomeBarbearia
    if config.logoBarbearia is not None:
        db["logoBarbearia"] = config.logoBarbearia
    if config.whatsYukio is not None:
        db["whatsYukio"] = config.whatsYukio
    if config.instagramYukio is not None:
        db["instagramYukio"] = config.instagramYukio
    if config.telegramYukio is not None:
        db["telegramYukio"] = config.telegramYukio
    if config.senhaYukio is not None:
        db["senhaYukio"] = config.senhaYukio
    if config.servicos is not None:
        db["servicos"] = config.servicos
    if config.diasFechados is not None:
        db["diasFechados"] = config.diasFechados
    if config.horariosPausaPadrao is not None:  # <--- GRAVA AS PAUSAS NA BASE DE DADOS
        db["horariosPausaPadrao"] = config.horariosPausaPadrao
    if config.horariosBloqueadosPorData is not None:
        db["horariosBloqueadosPorData"] = config.horariosBloqueadosPorData
    if config.agendamentos is not None:
        db["agendamentos"] = config.agendamentos
        
    salvar_no_bd(db)
    return {"sucesso": True, "banco": db}
