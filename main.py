import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ARQUIVO_BANCO = "banco.json"

def carregar_banco():
    if os.path.exists(ARQUIVO_BANCO):
        try:
            with open(ARQUIVO_BANCO, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "nomeBarbearia": "Barbearia Yukio",
        "logoUrl": "",
        "whatsYukio": "",
        "instagramYukio": "",
        "telegramYukio": "",
        "senhaYukio": "1234",
        "servicos": [
            {"id": 'corte', 'nome': 'Corte de Cabelo', 'preco': 3000, 'duracao': 50},
            {"id": 'combo', 'nome': 'Corte + Barba', 'preco': 4500, 'duracao': 80},
            {"id": 'barba', 'nome': 'Barba', 'preco': 2000, 'duracao': 30},
            {"id": 'sobrancelha', 'nome': 'Sobrancelha', 'preco': 1000, 'duracao': 20},
            {"id": 'simples', 'nome': 'Corte Simples', 'preco': 2500, 'duracao': 20}
        ],
        "diasFechados": [],
        "horariosPausaPadrao": [],
        "horariosBloqueadosPorData": {},
        "agendamentos": []
    }

def salvar_banco(dados):
    with open(ARQUIVO_BANCO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

class Agendamento(BaseModel):
    cliente: str
    servico: str
    preco: int
    data: str
    horario: str
    whatsapp: str
    horariosOcupados: Optional[List[str]] = None

class Configuracao(BaseModel):
    nomeBarbearia: Optional[str] = None
    logoUrl: Optional[str] = None
    whatsYukio: Optional[str] = None
    instagramYukio: Optional[str] = None
    telegramYukio: Optional[str] = None
    senhaYukio: Optional[str] = None
    servicos: Optional[List[dict]] = None
    diasFechados: Optional[List[int]] = None
    horariosPausaPadrao: Optional[List[str]] = None
    horariosBloqueadosPorData: Optional[Dict[str, List[str]]] = None
    agendamentos: Optional[List[dict]] = None

@app.get("/api/dados")
def obter_dados():
    return carregar_banco()

@app.post("/api/agendar")
def realizar_agendamento(agendamento: Agendamento):
    banco = carregar_banco()
    banco["agendamentos"].append(agendamento.dict())
    
    if agendamento.data not in banco["horariosBloqueadosPorData"]:
        banco["horariosBloqueadosPorData"][agendamento.data] = []
        
    # Bloqueia todos os horários correspondentes à duração do serviço
    horariosParaBloquear = agendamento.horariosOcupados if agendamento.horariosOcupados else [agendamento.horario]
    for h in horariosParaBloquear:
        if h not in banco["horariosBloqueadosPorData"][agendamento.data]:
            banco["horariosBloqueadosPorData"][agendamento.data].append(h)
        
    salvar_banco(banco)
    return {"sucesso": True, "mensagem": "Agendamento confirmado!"}

@app.post("/api/configurar")
def atualizar_configuracao(config: Configuracao):
    banco = carregar_banco()
    
    if config.nomeBarbearia is not None:
        banco["nomeBarbearia"] = config.nomeBarbearia
    if config.logoUrl is not None:
        banco["logoUrl"] = config.logoUrl
    if config.whatsYukio is not None:
        banco["whatsYukio"] = config.whatsYukio
    if config.instagramYukio is not None:
        banco["instagramYukio"] = config.instagramYukio
    if config.telegramYukio is not None:
        banco["telegramYukio"] = config.telegramYukio
    if config.senhaYukio is not None:
        banco["senhaYukio"] = config.senhaYukio
    if config.servicos is not None:
        banco["servicos"] = config.servicos
    if config.diasFechados is not None:
        banco["diasFechados"] = config.diasFechados
    if config.horariosPausaPadrao is not None:
        banco["horariosPausaPadrao"] = config.horariosPausaPadrao
    if config.horariosBloqueadosPorData is not None:
        banco["horariosBloqueadosPorData"] = config.horariosBloqueadosPorData
    if config.agendamentos is not None:
        banco["agendamentos"] = config.agendamentos
        
    salvar_banco(banco)
    return {"sucesso": True, "banco": banco}
