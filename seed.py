"""Popula o banco com dados de exemplo realistas para demonstração.

Uso:
    python seed.py          # adiciona dados (mantém existentes)
    python seed.py --reset  # apaga tudo e recria
"""
import sys
from datetime import date

from app.database import SessionLocal, init_db
from app.models import Configuracao, Contato, Demanda, Oficio
from app.utils import proximo_codigo_demanda, proximo_numero_oficio


def reset(db):
    db.query(Demanda).delete()
    db.query(Oficio).delete()
    db.query(Contato).delete()
    db.commit()


def run(reset_first=False):
    init_db()
    db = SessionLocal()

    if reset_first:
        reset(db)

    # --- Configuração do mandato -----------------------------------------
    config = db.query(Configuracao).first()
    if not config:
        config = Configuracao()
        db.add(config)
    config.nome_assessor = "Carlos Andrade"
    config.nome_mandato = "Mandato Vereador João Ribeiro"
    db.commit()

    # --- Contatos ---------------------------------------------------------
    contatos_data = [
        ("Maria de Souza", "Presidente de Bairro", "Jardim das Flores", "(11) 98888-1010", 5, date(2026, 7, 12)),
        ("José Pereira", "Comerciante", "Centro", "(11) 97777-2020", 4, date(2026, 7, 20)),
        ("Ana Lima", "Líder Comunitário", "Vila Nova", "(11) 96666-3030", 5, date(2026, 8, 3)),
        ("Roberto Dias", "Eleitor", "Parque Industrial", "(11) 95555-4040", 3, date(2026, 8, 15)),
        ("Fernanda Castro", "Apoiador", "Jardim das Flores", "(11) 94444-5050", 4, date(2026, 9, 2)),
        ("Paulo Mendes", "Comerciante", "Centro", "(11) 93333-6060", 2, date(2026, 9, 18)),
    ]
    contatos = []
    for nome, cargo, bairro, tel, nivel, dt in contatos_data:
        c = Contato(
            nome_completo=nome, cargo=cargo, bairro=bairro,
            telefone=tel, nivel_apoio=nivel, data_cadastro=dt,
            notas="Contato mapeado em visita de campo.",
        )
        db.add(c)
        contatos.append(c)
    db.commit()

    # --- Demandas (Q3 2026) ----------------------------------------------
    demandas_data = [
        (contatos[0], "Jardim das Flores", "Saúde", "Ampliação do horário do posto de saúde do bairro.", "Concluído", date(2026, 7, 14)),
        (contatos[1], "Centro", "Obras / Tapa-buraco", "Buracos na Rua Principal causando acidentes.", "Concluído", date(2026, 7, 22)),
        (contatos[2], "Vila Nova", "Iluminação", "Troca de lâmpadas queimadas na Praça Central.", "Em Andamento", date(2026, 8, 5)),
        (contatos[3], "Parque Industrial", "Segurança", "Solicitação de ronda policial no período noturno.", "Pendente", date(2026, 8, 17)),
        (contatos[4], "Jardim das Flores", "Educação", "Reforma da quadra da escola municipal.", "Em Andamento", date(2026, 9, 4)),
        (contatos[5], "Centro", "Transporte", "Nova linha de ônibus para o bairro Centro.", "Pendente", date(2026, 9, 20)),
        (contatos[0], "Jardim das Flores", "Saúde", "Campanha de vacinação itinerante.", "Concluído", date(2026, 9, 25)),
        (contatos[2], "Vila Nova", "Obras / Tapa-buraco", "Recapeamento da Avenida das Palmeiras.", "Concluído", date(2026, 8, 28)),
    ]
    for solic, bairro, cat, desc, status, dt in demandas_data:
        d = Demanda(
            codigo=proximo_codigo_demanda(db),
            data_entrada=dt, solicitante_id=solic.id,
            solicitante_nome=solic.nome_completo, bairro=bairro,
            categoria=cat, descricao=desc, status=status,
        )
        db.add(d)
        db.commit()  # commit por item para o código sequencial funcionar

    # --- Ofícios (Q3 2026) -----------------------------------------------
    oficios_data = [
        ("Secretaria de Saúde", "Ampliação do horário de atendimento — UBS Jardim das Flores", "Respondido / Atendido", "PROT-2026-1123", 3200, date(2026, 7, 16)),
        ("Secretaria de Obras", "Recapeamento e tapa-buraco Rua Principal", "Respondido / Atendido", "PROT-2026-1200", 5000, date(2026, 7, 25)),
        ("Prefeitura Municipal", "Iluminação pública da Praça Central", "Aguardando Resposta", "PROT-2026-1310", 1500, date(2026, 8, 8)),
        ("Secretaria de Segurança", "Reforço de policiamento no Parque Industrial", "Enviado", "", 2000, date(2026, 8, 20)),
        ("Secretaria de Educação", "Reforma da quadra da E.M. Jardim das Flores", "Aguardando Resposta", "PROT-2026-1450", 800, date(2026, 9, 6)),
    ]
    for orgao, assunto, status, prot, impacto, dt in oficios_data:
        o = Oficio(
            numero=proximo_numero_oficio(db, dt.year),
            data_envio=dt, orgao_destinatario=orgao, assunto=assunto,
            status=status, numero_protocolo=prot, impacto_estimado=impacto,
        )
        db.add(o)
        db.commit()

    total = (
        db.query(Contato).count(),
        db.query(Demanda).count(),
        db.query(Oficio).count(),
    )
    db.close()
    print(f"Seed concluído: {total[0]} contatos, {total[1]} demandas, {total[2]} ofícios.")


if __name__ == "__main__":
    run(reset_first="--reset" in sys.argv)
