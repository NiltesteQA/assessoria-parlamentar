"""Rotas do módulo de Atendimentos e Demandas."""
import io
from datetime import date, datetime

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CATEGORIAS_DEMANDA, STATUS_DEMANDA, Contato, Demanda
from app.templating import templates
from app.utils import proximo_codigo_demanda, salvar_upload

router = APIRouter(prefix="/demandas", tags=["demandas"])


def _filtrar(db, q, status, bairro, categoria, data_ini, data_fim):
    query = db.query(Demanda)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Demanda.descricao.ilike(like),
                Demanda.codigo.ilike(like),
                Demanda.solicitante_nome.ilike(like),
            )
        )
    if status:
        query = query.filter(Demanda.status == status)
    if bairro:
        query = query.filter(Demanda.bairro == bairro)
    if categoria:
        query = query.filter(Demanda.categoria == categoria)
    if data_ini:
        try:
            query = query.filter(Demanda.data_entrada >= datetime.strptime(data_ini, "%Y-%m-%d").date())
        except ValueError:
            pass
    if data_fim:
        try:
            query = query.filter(Demanda.data_entrada <= datetime.strptime(data_fim, "%Y-%m-%d").date())
        except ValueError:
            pass
    return query.order_by(Demanda.data_entrada.desc(), Demanda.id.desc()).all()


@router.get("", response_class=HTMLResponse)
def listar(
    request: Request,
    q: str = "",
    status: str = "",
    bairro: str = "",
    categoria: str = "",
    data_ini: str = "",
    data_fim: str = "",
    db: Session = Depends(get_db),
):
    demandas = _filtrar(db, q, status, bairro, categoria, data_ini, data_fim)
    bairros = sorted({d.bairro for d in db.query(Demanda).all() if d.bairro})
    contatos = db.query(Contato).order_by(Contato.nome_completo).all()
    return templates.TemplateResponse(
        "demandas.html",
        {
            "request": request,
            "titulo": "Atendimentos e Demandas",
            "demandas": demandas,
            "categorias": CATEGORIAS_DEMANDA,
            "status_opcoes": STATUS_DEMANDA,
            "bairros": bairros,
            "contatos": contatos,
            "proximo_codigo": proximo_codigo_demanda(db),
            "filtros": {
                "q": q, "status": status, "bairro": bairro,
                "categoria": categoria, "data_ini": data_ini, "data_fim": data_fim,
            },
            "active": "demandas",
        },
    )


@router.post("/novo")
def criar(
    solicitante_id: str = Form(""),
    solicitante_nome: str = Form(""),
    bairro: str = Form(""),
    categoria: str = Form("Outros"),
    descricao: str = Form(""),
    status: str = Form("Pendente"),
    data_entrada: str = Form(""),
    anexo: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    de = date.today()
    if data_entrada:
        try:
            de = datetime.strptime(data_entrada, "%Y-%m-%d").date()
        except ValueError:
            pass

    sid = int(solicitante_id) if solicitante_id.strip().isdigit() else None
    # se vinculou contato e não informou bairro, herda o bairro do contato
    if sid and not bairro:
        c = db.get(Contato, sid)
        if c:
            bairro = c.bairro

    demanda = Demanda(
        codigo=proximo_codigo_demanda(db),
        data_entrada=de,
        solicitante_id=sid,
        solicitante_nome=solicitante_nome.strip(),
        bairro=bairro.strip(),
        categoria=categoria,
        descricao=descricao.strip(),
        status=status,
        anexo=salvar_upload(anexo, "demandas"),
    )
    db.add(demanda)
    db.commit()
    return RedirectResponse(url="/demandas?ok=1", status_code=303)


@router.post("/{demanda_id}/editar")
def editar(
    demanda_id: int,
    solicitante_nome: str = Form(""),
    bairro: str = Form(""),
    categoria: str = Form("Outros"),
    descricao: str = Form(""),
    status: str = Form("Pendente"),
    db: Session = Depends(get_db),
):
    d = db.get(Demanda, demanda_id)
    if d:
        d.solicitante_nome = solicitante_nome.strip()
        d.bairro = bairro.strip()
        d.categoria = categoria
        d.descricao = descricao.strip()
        d.status = status
        db.commit()
    return RedirectResponse(url="/demandas?ok=1", status_code=303)


@router.post("/{demanda_id}/status")
def mudar_status(demanda_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    d = db.get(Demanda, demanda_id)
    if d:
        d.status = status
        db.commit()
    return RedirectResponse(url="/demandas?ok=1", status_code=303)


@router.post("/{demanda_id}/excluir")
def excluir(demanda_id: int, db: Session = Depends(get_db)):
    d = db.get(Demanda, demanda_id)
    if d:
        db.delete(d)
        db.commit()
    return RedirectResponse(url="/demandas?ok=1", status_code=303)


def _dataframe(db, **filtros) -> pd.DataFrame:
    demandas = _filtrar(db, **filtros)
    return pd.DataFrame(
        [
            {
                "Código": d.codigo,
                "Data": d.data_entrada.strftime("%d/%m/%Y") if d.data_entrada else "",
                "Solicitante": d.solicitante.nome_completo if d.solicitante else d.solicitante_nome,
                "Bairro": d.bairro,
                "Categoria": d.categoria,
                "Descrição": d.descricao,
                "Status": d.status,
            }
            for d in demandas
        ]
    )


@router.get("/exportar/csv")
def exportar_csv(
    q: str = "", status: str = "", bairro: str = "", categoria: str = "",
    data_ini: str = "", data_fim: str = "", db: Session = Depends(get_db),
):
    df = _dataframe(db, q=q, status=status, bairro=bairro, categoria=categoria, data_ini=data_ini, data_fim=data_fim)
    stream = io.StringIO()
    df.to_csv(stream, index=False, encoding="utf-8-sig")
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=demandas.csv"},
    )


@router.get("/exportar/excel")
def exportar_excel(
    q: str = "", status: str = "", bairro: str = "", categoria: str = "",
    data_ini: str = "", data_fim: str = "", db: Session = Depends(get_db),
):
    df = _dataframe(db, q=q, status=status, bairro=bairro, categoria=categoria, data_ini=data_ini, data_fim=data_fim)
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Demandas")
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=demandas.xlsx"},
    )
