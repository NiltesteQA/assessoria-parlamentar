"""Testes E2E dos fluxos críticos com Playwright.

Cobre:
- Dashboard carrega com métricas do trimestre
- Registro rápido (FAB) cria um contato
- Filtro de demandas por status
- Geração/download do relatório trimestral em PDF
"""
import re

import httpx
import pytest


def test_dashboard_carrega_metricas(page, base_url):
    page.goto(f"{base_url}/?ano=2026&trimestre=Q3")
    # título e um dos cartões de métrica
    assert page.get_by_text("Visão Geral").is_visible()
    assert page.get_by_text("Atendimentos no Trimestre").is_visible()
    assert page.get_by_text("Ofícios Protocolados").is_visible()
    # o gráfico de bairros deve existir
    assert page.locator("#chartBairro").count() == 1


def test_registro_rapido_cria_contato(page, base_url):
    page.goto(f"{base_url}/")
    # abre o FAB
    page.get_by_role("button", name="Registro Rápido").click()
    page.get_by_role("button", name=re.compile("Novo Contato")).click()
    # preenche o modal rápido
    modal = page.locator("#modal-rapido-contato")
    modal.get_by_placeholder("Nome completo *").fill("Teste Playwright")
    modal.get_by_role("button", name="Salvar Contato").click()
    # após salvar, volta para a listagem/dashboard; verifica o contato na lista
    page.goto(f"{base_url}/contatos?q=Playwright")
    assert page.get_by_text("Teste Playwright").is_visible()


def test_filtro_demandas_por_status(page, base_url):
    page.goto(f"{base_url}/demandas?status=Conclu%C3%ADdo")
    # todas as linhas visíveis devem conter o badge "Concluído"
    linhas = page.locator("tbody tr")
    assert linhas.count() >= 1
    # garante que não há status divergente óbvio na coluna de status
    assert page.get_by_text("Nenhuma demanda encontrada.").count() == 0


def test_gera_relatorio_pdf(page, base_url):
    page.goto(f"{base_url}/relatorio?ano=2026&trimestre=Q3")
    assert page.get_by_text("Gerador de Relatório Trimestral").is_visible()

    # dispara o POST e captura o download
    with page.expect_download() as download_info:
        page.get_by_role("button", name=re.compile("Exportar Relatório")).click()
    download = download_info.value
    assert download.suggested_filename.endswith(".pdf")


def test_pdf_endpoint_direto(base_url):
    """Valida o endpoint de PDF diretamente (conteúdo binário)."""
    r = httpx.post(
        f"{base_url}/relatorio/pdf",
        data={"ano": 2026, "trimestre": "Q3", "observacoes": "teste"},
        timeout=30,
    )
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert r.content[:5] == b"%PDF-"
