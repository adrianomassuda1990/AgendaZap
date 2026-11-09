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

banco_dados = {
    "whatsYukio": "",
    "instagramYukio": "",
    "telegramYukio": "",
    "senhaYukio": "1234",
    "servicos": [
        {"id": "corte", "nome": "Corte de Cabelo", "preco": 3000},
        {"id": "combo", "nome": "Corte + Barba", "preco": 4500}
    ],
    "diasFechados": [],
    "horariosPausaPadrao": [],  # <--- Pausas fixas recorrentes
    "horariosBloqueadosPorData": {},
    "agendamentos": []
}

class Agendamento(BaseModel):
    cliente: str
    servico: str
    preco: int
    data: str
    horario: str
    whatsapp: str

class Configuracao(BaseModel):
    whatsYukio: Optional[str] = None
    instagramYukio: Optional[str] = None
    telegramYukio: Optional[str] = None
    senhaYukio: Optional[str] = None
    servicos: Optional[List[dict]] = None
    diasFechados: Optional[List[int]] = None
    horariosPausaPadrao: Optional[List[str]] = None  # <--- Aceita pausas fixas
    horariosBloqueadosPorData: Optional[Dict[str, List[str]]] = None

@app.get("/api/dados")
def obter_dados():
    return banco_dados

@app.post("/api/agendar")
def realizar_agendamento(agendamento: Agendamento):
    banco_dados["agendamentos"].append(agendamento.dict())
    
    if agendamento.data not in banco_dados["horariosBloqueadosPorData"]:
        banco_dados["horariosBloqueadosPorData"][agendamento.data] = []
        
    if agendamento.horario not in banco_dados["horariosBloqueadosPorData"][agendamento.data]:
        banco_dados["horariosBloqueadosPorData"][agendamento.data].append(agendamento.horario)
        
    return {"sucesso": True, "mensagem": "Agendamento confirmado!"}

@app.post("/api/configurar")
def atualizar_configuracao(config: Configuracao):
    if config.whatsYukio is not None:
        banco_dados["whatsYukio"] = config.whatsYukio
    if config.instagramYukio is not None:
        banco_dados["instagramYukio"] = config.instagramYukio
    if config.telegramYukio is not None:
        banco_dados["telegramYukio"] = config.telegramYukio
    if config.senhaYukio is not None:
        banco_dados["senhaYukio"] = config.senhaYukio
    if config.servicos is not None:
        banco_dados["servicos"] = config.servicos
    if config.diasFechados is not None:
        banco_dados["diasFechados"] = config.diasFechados
    if config.horariosPausaPadrao is not None:
        banco_dados["horariosPausaPadrao"] = config.horariosPausaPadrao
    if config.horariosBloqueadosPorData is not None:
        banco_dados["horariosBloqueadosPorData"] = config.horariosBloqueadosPorData
        
    return {"sucesso": True, "banco": banco_dados}
