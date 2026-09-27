"""Funções utilitárias: trimestres, códigos sequenciais e uploads."""
import os
import re
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")

# --- Trimestres -----------------------------------------------------------

TRIMESTRES = {
    "Q1": (1, 3),
    "Q2": (4, 6),
    "Q3": (7, 9),
    "Q4": (10, 12),
}


def trimestre_range(ano: int, trimestre: str):
    """Retorna (data_inicio, data_fim) para um trimestre/ano."""
    trimestre = trimestre.upper()
    if trimestre not in TRIMESTRES:
        raise ValueError(f"Trimestre inválido: {trimestre}")
    mes_ini, mes_fim = TRIMESTRES[trimestre]
    inicio = date(ano, mes_ini, 1)
    # último dia do mês final do trimestre
    if mes_fim == 12:
        fim = date(ano, 12, 31)
    else:
        # primeiro dia do mês seguinte menos um dia
        from calendar import monthrange

        ultimo = monthrange(ano, mes_fim)[1]
        fim = date(ano, mes_fim, ultimo)
    return inicio, fim


def trimestre_de_data(d: date) -> str:
    """Retorna 'Q1'..'Q4' para uma data."""
    return f"Q{(d.month - 1) // 3 + 1}"


def rotulo_trimestre(ano: int, trimestre: str) -> str:
    nomes = {
        "Q1": "1º Trimestre (Jan–Mar)",
        "Q2": "2º Trimestre (Abr–Jun)",
        "Q3": "3º Trimestre (Jul–Set)",
        "Q4": "4º Trimestre (Out–Dez)",
    }
    return f"{nomes.get(trimestre.upper(), trimestre)} / {ano}"


# --- Geração de códigos sequenciais ---------------------------------------

def proximo_codigo_demanda(db: Session) -> str:
    """Gera o próximo código no formato DEM-001."""
    from app.models import Demanda

    maior = 0
    for (codigo,) in db.query(Demanda.codigo).all():
        if codigo:
            m = re.search(r"DEM-(\d+)", codigo)
            if m:
                maior = max(maior, int(m.group(1)))
    return f"DEM-{maior + 1:03d}"


def proximo_numero_oficio(db: Session, ano: int | None = None) -> str:
    """Gera o próximo número no formato OF-042/2026."""
    from app.models import Oficio

    ano = ano or date.today().year
    maior = 0
    for (numero,) in db.query(Oficio.numero).all():
        if numero:
            m = re.match(rf"OF-(\d+)/{ano}", numero)
            if m:
                maior = max(maior, int(m.group(1)))
    return f"OF-{maior + 1:03d}/{ano}"


# --- Uploads ---------------------------------------------------------------

def salvar_upload(arquivo, subpasta: str = "") -> str:
    """Salva um UploadFile e retorna o caminho relativo (para servir via /static)."""
    if not arquivo or not getattr(arquivo, "filename", ""):
        return ""
    destino_dir = os.path.join(UPLOAD_DIR, subpasta) if subpasta else UPLOAD_DIR
    os.makedirs(destino_dir, exist_ok=True)

    nome_seguro = re.sub(r"[^A-Za-z0-9_.-]", "_", arquivo.filename)
    # evita colisão de nomes
    base, ext = os.path.splitext(nome_seguro)
    caminho = os.path.join(destino_dir, nome_seguro)
    contador = 1
    while os.path.exists(caminho):
        nome_seguro = f"{base}_{contador}{ext}"
        caminho = os.path.join(destino_dir, nome_seguro)
        contador += 1

    with open(caminho, "wb") as f:
        f.write(arquivo.file.read())

    rel = os.path.relpath(caminho, os.path.join(BASE_DIR, "static"))
    return f"/static/{rel.replace(os.sep, '/')}"
