"""Configuração central do Jinja2 (compartilhada por routers e main)."""
import os
from datetime import date, datetime

from fastapi.templating import Jinja2Templates

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def _fmt_data(valor):
    if not valor:
        return ""
    if isinstance(valor, (date, datetime)):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def _rotulo_tri(t: str) -> str:
    """Converte a sigla técnica do trimestre (Q1..Q4) no rótulo exibido ao usuário."""
    mapa = {"Q1": "1º Tri", "Q2": "2º Tri", "Q3": "3º Tri", "Q4": "4º Tri"}
    return mapa.get(str(t).upper(), str(t))


def _badge_status(status: str) -> str:
    """Retorna classes Tailwind para o badge de status."""
    mapa = {
        "Pendente": "bg-amber-100 text-amber-800",
        "Em Andamento": "bg-blue-100 text-blue-800",
        "Concluído": "bg-emerald-100 text-emerald-800",
        "Cancelado": "bg-rose-100 text-rose-700",
        "Enviado": "bg-blue-100 text-blue-800",
        "Aguardando Resposta": "bg-amber-100 text-amber-800",
        "Respondido / Atendido": "bg-emerald-100 text-emerald-800",
        "Arquivado": "bg-slate-200 text-slate-600",
    }
    return mapa.get(status, "bg-slate-100 text-slate-700")


templates.env.filters["fmt_data"] = _fmt_data
templates.env.filters["badge_status"] = _badge_status
templates.env.filters["rotulo_tri"] = _rotulo_tri
templates.env.globals["ano_atual"] = date.today().year
