"""Gerador de Relatório Trimestral (visual + exportação PDF via WeasyPrint)."""
from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Configuracao
from app.services import anos_disponiveis, destaques_trimestre, metricas_trimestre
from app.templating import templates
from app.utils import rotulo_trimestre, trimestre_de_data

router = APIRouter(tags=["relatorio"])


def _contexto_relatorio(db: Session, ano: int, trimestre: str, observacoes: str = ""):
    m = metricas_trimestre(db, ano, trimestre)
    dest = destaques_trimestre(db, ano, trimestre)
    config = db.query(Configuracao).first()
    return {
        "metricas": m,
        "destaques": dest,
        "config": config,
        "rotulo": rotulo_trimestre(ano, trimestre),
        "ano": ano,
        "trimestre": trimestre.upper(),
        "observacoes": observacoes,
        "gerado_em": date.today().strftime("%d/%m/%Y"),
    }


@router.get("/relatorio", response_class=HTMLResponse)
def tela_relatorio(
    request: Request,
    ano: int = None,
    trimestre: str = None,
    db: Session = Depends(get_db),
):
    ano = ano or date.today().year
    trimestre = (trimestre or trimestre_de_data(date.today())).upper()

    ctx = _contexto_relatorio(db, ano, trimestre)
    ctx.update(
        {
            "request": request,
            "titulo": "Relatório Trimestral",
            "anos": anos_disponiveis(db),
            "trimestres": ["Q1", "Q2", "Q3", "Q4"],
            "active": "relatorio",
        }
    )
    return templates.TemplateResponse("relatorio.html", ctx)


@router.post("/configuracao/salvar")
def salvar_config(
    nome_assessor: str = Form(""),
    nome_mandato: str = Form(""),
    ano: int = Form(...),
    trimestre: str = Form(...),
    db: Session = Depends(get_db),
):
    config = db.query(Configuracao).first()
    if not config:
        config = Configuracao()
        db.add(config)
    config.nome_assessor = nome_assessor.strip() or "Assessor(a) Parlamentar"
    config.nome_mandato = nome_mandato.strip() or "Mandato Parlamentar"
    db.commit()
    return RedirectResponse(url=f"/relatorio?ano={ano}&trimestre={trimestre}&ok=1", status_code=303)


@router.post("/relatorio/pdf")
def gerar_pdf(
    request: Request,
    ano: int = Form(...),
    trimestre: str = Form(...),
    observacoes: str = Form(""),
    db: Session = Depends(get_db),
):
    from weasyprint import HTML

    ctx = _contexto_relatorio(db, ano, trimestre.upper(), observacoes)
    ctx["request"] = request

    html_str = templates.get_template("relatorio_pdf.html").render(ctx)
    pdf_bytes = HTML(string=html_str, base_url=str(request.base_url)).write_pdf()

    nome = f"relatorio_{trimestre.upper()}_{ano}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={nome}"},
    )
