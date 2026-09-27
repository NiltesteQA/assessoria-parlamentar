"""Aplicação principal — Gestão de Assessoria Parlamentar."""
import os

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import get_db, init_db
from app.models import Configuracao
from app.routers import contatos, demandas, oficios, relatorio
from app.services import anos_disponiveis, metricas_trimestre
from app.templating import templates
from app.utils import UPLOAD_DIR, rotulo_trimestre, trimestre_de_data

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Gestão de Assessoria Parlamentar")

# garante diretório de uploads
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

app.include_router(contatos.router)
app.include_router(demandas.router)
app.include_router(oficios.router)
app.include_router(relatorio.router)


@app.on_event("startup")
def _startup():
    init_db()
    # garante uma linha de configuração
    from app.database import SessionLocal

    db = SessionLocal()
    if not db.query(Configuracao).first():
        db.add(Configuracao())
        db.commit()
    db.close()


def _trimestre_atual() -> str:
    from datetime import date

    return trimestre_de_data(date.today())


@app.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    ano: int = None,
    trimestre: str = None,
    db: Session = Depends(get_db),
):
    from datetime import date

    ano = ano or date.today().year
    trimestre = (trimestre or _trimestre_atual()).upper()

    m = metricas_trimestre(db, ano, trimestre)
    config = db.query(Configuracao).first()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "titulo": "Dashboard",
            "metricas": m,
            "rotulo": rotulo_trimestre(ano, trimestre),
            "ano": ano,
            "trimestre": trimestre,
            "anos": anos_disponiveis(db),
            "trimestres": ["Q1", "Q2", "Q3", "Q4"],
            "config": config,
            "active": "dashboard",
        },
    )


@app.post("/configuracao")
def salvar_config(
    request: Request,
    nome_assessor: str = Depends(lambda: None),
):
    # placeholder; a config é editada na tela de relatório
    return {"ok": True}
