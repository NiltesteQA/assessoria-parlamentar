"""Rotas do módulo de Ofícios e Ações Oficiais."""
import io
from datetime import date, datetime

import pandas as pd
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import STATUS_OFICIO, Oficio
from app.templating import templates
from app.utils import proximo_numero_oficio, salvar_upload

router = APIRouter(prefix="/oficios", tags=["oficios"])


def _filtrar(db, q, status, orgao, data_ini, data_fim):
    query = db.query(Oficio)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Oficio.assunto.ilike(like),
                Oficio.numero.ilike(like),
                Oficio.orgao_destinatario.ilike(like),
                Oficio.numero_protocolo.ilike(like),
            )
        )
    if status:
        query = query.filter(Oficio.status == status)
    if orgao:
        query = query.filter(Oficio.orgao_destinatario == orgao)
    if data_ini:
        try:
            query = query.filter(Oficio.data_envio >= datetime.strptime(data_ini, "%Y-%m-%d").date())
        except ValueError:
            pass
    if data_fim:
        try:
            query = query.filter(Oficio.data_envio <= datetime.strptime(data_fim, "%Y-%m-%d").date())
        except ValueError:
            pass
    return query.order_by(Oficio.data_envio.desc(), Oficio.id.desc()).all()


@router.get("", response_class=HTMLResponse)
def listar(
    request: Request,
    q: str = "",
    status: str = "",
    orgao: str = "",
    data_ini: str = "",
    data_fim: str = "",
    db: Session = Depends(get_db),
):
    oficios = _filtrar(db, q, status, orgao, data_ini, data_fim)
    orgaos = sorted({o.orgao_destinatario for o in db.query(Oficio).all() if o.orgao_destinatario})
    return templates.TemplateResponse(
        "oficios.html",
        {
            "request": request,
            "titulo": "Ofícios e Ações Oficiais",
            "oficios": oficios,
            "status_opcoes": STATUS_OFICIO,
            "orgaos": orgaos,
            "proximo_numero": proximo_numero_oficio(db),
            "filtros": {"q": q, "status": status, "orgao": orgao, "data_ini": data_ini, "data_fim": data_fim},
            "active": "oficios",
        },
    )


@router.post("/novo")
def criar(
    orgao_destinatario: str = Form(""),
    assunto: str = Form(""),
    status: str = Form("Enviado"),
    numero_protocolo: str = Form(""),
    impacto_estimado: int = Form(0),
    data_envio: str = Form(""),
    numero: str = Form(""),
    anexo: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    dv = date.today()
    if data_envio:
        try:
            dv = datetime.strptime(data_envio, "%Y-%m-%d").date()
        except ValueError:
            pass
    num = numero.strip() or proximo_numero_oficio(db, dv.year)
    oficio = Oficio(
        numero=num,
        data_envio=dv,
        orgao_destinatario=orgao_destinatario.strip(),
        assunto=assunto.strip(),
        status=status,
        numero_protocolo=numero_protocolo.strip(),
        impacto_estimado=int(impacto_estimado or 0),
        anexo=salvar_upload(anexo, "oficios"),
    )
    db.add(oficio)
    db.commit()
    return RedirectResponse(url="/oficios?ok=1", status_code=303)


@router.post("/{oficio_id}/editar")
def editar(
    oficio_id: int,
    orgao_destinatario: str = Form(""),
    assunto: str = Form(""),
    status: str = Form("Enviado"),
    numero_protocolo: str = Form(""),
    impacto_estimado: int = Form(0),
    db: Session = Depends(get_db),
):
    o = db.get(Oficio, oficio_id)
    if o:
        o.orgao_destinatario = orgao_destinatario.strip()
        o.assunto = assunto.strip()
        o.status = status
        o.numero_protocolo = numero_protocolo.strip()
        o.impacto_estimado = int(impacto_estimado or 0)
        db.commit()
    return RedirectResponse(url="/oficios?ok=1", status_code=303)


@router.post("/{oficio_id}/status")
def mudar_status(oficio_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    o = db.get(Oficio, oficio_id)
    if o:
        o.status = status
        db.commit()
    return RedirectResponse(url="/oficios?ok=1", status_code=303)


@router.post("/{oficio_id}/excluir")
def excluir(oficio_id: int, db: Session = Depends(get_db)):
    o = db.get(Oficio, oficio_id)
    if o:
        db.delete(o)
        db.commit()
    return RedirectResponse(url="/oficios?ok=1", status_code=303)


def _dataframe(db, **filtros) -> pd.DataFrame:
    oficios = _filtrar(db, **filtros)
    return pd.DataFrame(
        [
            {
                "Número": o.numero,
                "Data Envio": o.data_envio.strftime("%d/%m/%Y") if o.data_envio else "",
                "Órgão/Destinatário": o.orgao_destinatario,
                "Assunto": o.assunto,
                "Status": o.status,
                "Protocolo": o.numero_protocolo,
                "Impacto Estimado": o.impacto_estimado,
            }
            for o in oficios
        ]
    )


@router.get("/exportar/csv")
def exportar_csv(
    q: str = "", status: str = "", orgao: str = "", data_ini: str = "", data_fim: str = "",
    db: Session = Depends(get_db),
):
    df = _dataframe(db, q=q, status=status, orgao=orgao, data_ini=data_ini, data_fim=data_fim)
    stream = io.StringIO()
    df.to_csv(stream, index=False, encoding="utf-8-sig")
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=oficios.csv"},
    )


@router.get("/exportar/excel")
def exportar_excel(
    q: str = "", status: str = "", orgao: str = "", data_ini: str = "", data_fim: str = "",
    db: Session = Depends(get_db),
):
    df = _dataframe(db, q=q, status=status, orgao=orgao, data_ini=data_ini, data_fim=data_fim)
    stream = io.BytesIO()
    with pd.ExcelWriter(stream, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Oficios")
    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=oficios.xlsx"},
    )
