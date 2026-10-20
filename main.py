from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.compartilhado.infra.ciclo_vida import ciclo_de_vida_app
from app.compartilhado.infra.config import config
from app.modulos.espacos.interface.roteador import roteador as roteador_espacos
from app.modulos.projeto.interface.roteador import roteador as roteador_projetos
from app.modulos.usuarios.interface.roteador import roteador as roteador_usuarios

app = FastAPI(
    title="API COLAB - IFAL",
    description="Sistema de Gestão e Agendamento do COLAB",
    version="0.1.0",
    lifespan=ciclo_de_vida_app,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.lista_origens_cors,
    allow_credentials=config.permite_credenciais_cors,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=config.lista_hosts_permitidos,
)

app.include_router(roteador_usuarios)
app.include_router(roteador_espacos)
app.include_router(roteador_projetos)

@app.get("/", tags=["Status"])
def raiz():
    return {"mensagem": "API do COLAB operando com sucesso!"}
