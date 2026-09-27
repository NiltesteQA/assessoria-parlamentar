"""Rotas do módulo de Contatos / Redes Políticas."""
import io
from datetime import date, datetime

import pandas as pd
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CARGOS, Contato
from app.templating import templates

router = APIRouter(prefix="/contatos", tags=["contatos"])


def _filtrar(db: Session, q: str, bairro: str, cargo: str):
    query = db.query(Contato)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Contato.nome_completo.ilike(like),
                Contato.notas.ilike(like),
                Contato.telefone.ilike(like),
            )
        )
    if bairro:
        query = query.filter(Contato.bairro == bairro)
    if cargo:
        query = query.filter(Contato.cargo == cargo)
    return query.order_by(Contato.nome_completo).all()


@router.get("", response_class=HTMLResponse)
def listar(
    request: Request,
    q: str = "",
    bairro: str = "",
    cargo: str = "",
    db: Session = Depends(get_db),
):
    contatos = _filtrar(db, q, bairro, cargo)
    bairros = sorted({c.bairro for c in db.query(Contato).all() if c.bairro})
    return templates.TemplateResponse(
        "contatos.html",
        {
            "request": request,
            "titulo": "Contatos / Redes Políticas",
            "contatos": contatos,
            "cargos": CARGOS,
            "bairros": bairros,
            "filtros": {"q": q, "bairro": bairro, "cargo": cargo},
            "active": "contatos",
        },
    )


@router.post("/novo")
def criar(
    nome_completo: str = Form(...),
    cargo: str = Form("Eleitor"),
    bairro: str = Form(""),
    telefone: str = Form(""),
    nivel_apoio: int = Form(3),
    notas: str = Form(""),
    data_cadastro: str = Form(""),
    db: Session = Depends(get_db),
):
    dc = date.today()
    if data_cadastro:
        try:
            dc = datetime.strptime(data_cadastro, "%Y-%m-%d").date()
        except ValueError:
            pass
    contato = Contato(
        nome_completo=nome_completo.strip(),
        cargo=cargo,
        bairro=bairro.strip(),
        telefone=telefone.strip(),
        nivel_apoio=max(1, min(5, int(nivel_apoio or 3))),
        notas=notas.strip(),
        data_cadastro=dc,
    )
    db.add(contato)
    db.commit()
    return RedirectResponse(url="/contatos?ok=1", status_code=303)


@router.post("/{contato_id}/editar")
def editar(
    contato_id: int,
    nome_completo: str = Form(...),
    cargo: str = Form("Eleitor"),
    bairro: str = Form(""),
    telefone: str = Form(""),
    nivel_apoio: int = Form(3),
    notas: str = Form(""),
    db: Session = Depends(get_db),
):
    contato = db.get(Contato, contato_id)
    if contato:
        contato.nome_completo = nome_completo.strip()
        contato.cargo = cargo
        contato.bairro = bairro.strip()
        contato.telefone = telefone.strip()
        contato.nivel_apoio = max(1, min(5, int(nivel_apoio or 3)))
        contato.notas = notas.strip()
        db.commit()
    return RedirectResponse(url="/contatos?ok=1", status_code=303)


@router.post("/{contato_id}/excluir")
def excluir(contato_id: int, db: Session = Depends(get_db)):
    contato = db.get(Contato, contato_id)
    if contato:
        db.delete(contato)
        db.commit()
    return RedirectResponse(url="/contatos?ok=1", status_code=303)


def _dataframe(db: Session, q, bairro, cargo) -> pd.DataFrame:
    contatos = _filtrar(db, q, bairro, cargo)
    return pd.DataFrame(
        [
            {
                "Nome": c.nome_completo,
                "Cargo": c.cargo,
                "Bairro": c.bairro,
                "Telefone": c.telefone,
                "Nível de Apoio": c.nivel_apoio,
                "Data Cadastro": c.data_cadastro.strftime("%d/%m/%Y")
                if c.data_cadastro
                else "",
                "Notas": c.notas,
            }
            for c in contatos
        ]
    )


@router.get("/exportar/csv")
def exportar_csv(q: str = "", bairro: str = "", cargo: str = "", db: Session = Depends(get_db)):
    df = _dataframe(db, q, bairro, cargo)
    stream = io.StringIO()
    df.to_csv(stream, index=False, encoding="utf-8-sig")
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=contatos.csv"},
    )


@router.get("/exportar/excel")
def exportar_excel(q: str = "", bairro: str = "", cargo: str = "", db: Session = Depends(get_db)):
    df = _dataframe(db, q, bairro, cargo)
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Contatos")
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=contatos.xlsx"},
    )
