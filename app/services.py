"""Serviços de agregação: métricas do dashboard e dados do relatório trimestral."""
from collections import Counter

from sqlalchemy.orm import Session

from app.models import Contato, Demanda, Oficio
from app.utils import trimestre_range


def _demandas_periodo(db: Session, inicio, fim):
    return (
        db.query(Demanda)
        .filter(Demanda.data_entrada >= inicio, Demanda.data_entrada <= fim)
        .all()
    )


def _oficios_periodo(db: Session, inicio, fim):
    return (
        db.query(Oficio)
        .filter(Oficio.data_envio >= inicio, Oficio.data_envio <= fim)
        .all()
    )


def _contatos_periodo(db: Session, inicio, fim):
    return (
        db.query(Contato)
        .filter(Contato.data_cadastro >= inicio, Contato.data_cadastro <= fim)
        .all()
    )


def metricas_trimestre(db: Session, ano: int, trimestre: str) -> dict:
    """Calcula todas as métricas e agregações de um trimestre."""
    inicio, fim = trimestre_range(ano, trimestre)

    demandas = _demandas_periodo(db, inicio, fim)
    oficios = _oficios_periodo(db, inicio, fim)
    contatos = _contatos_periodo(db, inicio, fim)

    total_demandas = len(demandas)
    concluidas = sum(1 for d in demandas if d.status == "Concluído")
    taxa_resolucao = round((concluidas / total_demandas) * 100) if total_demandas else 0

    total_oficios = len(oficios)
    oficios_respondidos = sum(
        1 for o in oficios if o.status == "Respondido / Atendido"
    )
    oficios_pendentes = sum(
        1 for o in oficios if o.status in ("Enviado", "Aguardando Resposta")
    )

    # Distribuição por bairro (demandas)
    por_bairro = Counter(d.bairro or "Não informado" for d in demandas)
    # Distribuição por categoria
    por_categoria = Counter(d.categoria or "Outros" for d in demandas)

    # Top 5 bairros
    top_bairros = por_bairro.most_common(5)

    # Impacto total estimado dos ofícios
    impacto_total = sum(o.impacto_estimado or 0 for o in oficios)

    return {
        "ano": ano,
        "trimestre": trimestre.upper(),
        "periodo_inicio": inicio.isoformat(),
        "periodo_fim": fim.isoformat(),
        "total_demandas": total_demandas,
        "demandas_concluidas": concluidas,
        "taxa_resolucao": taxa_resolucao,
        "total_oficios": total_oficios,
        "oficios_respondidos": oficios_respondidos,
        "oficios_pendentes": oficios_pendentes,
        "novos_contatos": len(contatos),
        "impacto_total": impacto_total,
        "por_bairro": dict(por_bairro),
        "por_categoria": dict(por_categoria),
        "top_bairros": top_bairros,
        "_demandas": demandas,
        "_oficios": oficios,
    }


def destaques_trimestre(db: Session, ano: int, trimestre: str) -> dict:
    """Retorna os destaques (top 5) de demandas e ofícios do período."""
    m = metricas_trimestre(db, ano, trimestre)

    # Top 5 demandas concluídas primeiro, depois em andamento (mais recentes)
    ordem_status = {"Concluído": 0, "Em Andamento": 1, "Pendente": 2, "Cancelado": 3}
    demandas = sorted(
        m["_demandas"],
        key=lambda d: (ordem_status.get(d.status, 9), d.data_entrada),
    )[:5]

    # Top 5 ofícios por impacto estimado
    oficios = sorted(
        m["_oficios"],
        key=lambda o: (o.impacto_estimado or 0),
        reverse=True,
    )[:5]

    return {"demandas": demandas, "oficios": oficios}


def anos_disponiveis(db: Session) -> list[int]:
    """Retorna a lista de anos que possuem qualquer registro (para o filtro)."""
    anos = set()
    for (d,) in db.query(Demanda.data_entrada).all():
        if d:
            anos.add(d.year)
    for (d,) in db.query(Oficio.data_envio).all():
        if d:
            anos.add(d.year)
    for (d,) in db.query(Contato.data_cadastro).all():
        if d:
            anos.add(d.year)
    from datetime import date

    anos.add(date.today().year)
    return sorted(anos, reverse=True)
