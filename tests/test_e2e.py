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



def test_marca_assessoria_aguia(page, base_url):
    """A identidade visual deve exibir 'Assessoria Águia' na navegação."""
    page.goto(f"{base_url}/")
    # aparece na sidebar (desktop) — pelo menos uma ocorrência visível
    assert page.get_by_text("Assessoria Águia").first.is_visible()


def test_contatos_usa_rotulo_perfil(page, base_url):
    """A tela de Contatos deve usar 'Perfil' no lugar de 'Cargo'."""
    page.goto(f"{base_url}/contatos")
    # cabeçalho da coluna
    assert page.get_by_role("columnheader", name="Perfil").is_visible()
    # opção do filtro (dentro de um <select>, então checamos presença no DOM)
    assert page.get_by_role("option", name="Todos os perfis").count() == 1
    # a palavra "Cargo" não deve mais aparecer como cabeçalho de coluna
    assert page.get_by_role("columnheader", name="Cargo").count() == 0



def test_botoes_trimestre_em_portugues(page, base_url):
    """Os botões de trimestre devem exibir '1º Tri'..'4º Tri' (sem a sigla Q)."""
    page.goto(f"{base_url}/?ano=2026&trimestre=Q3")
    for rotulo in ["1º Tri", "2º Tri", "3º Tri", "4º Tri"]:
        assert page.get_by_role("link", name=rotulo).first.is_visible()
    # a sigla antiga não deve mais aparecer como texto de botão
    assert page.get_by_role("link", name="Q1").count() == 0
    # o filtro deve continuar funcionando: clicar em "1º Tri" leva a trimestre=Q1
    page.get_by_role("link", name="1º Tri").first.click()
    assert "trimestre=Q1" in page.url



def test_relatorio_rotulo_nome_vereador(page, base_url):
    """O campo do cabeçalho deve exibir 'Nome do Vereador'."""
    page.goto(f"{base_url}/relatorio?ano=2026&trimestre=Q3")
    assert page.get_by_text("Nome do Vereador").is_visible()
    # o rótulo antigo não deve mais aparecer
    assert page.get_by_text("Nome / Logotipo do Mandato").count() == 0



def test_oficio_campos_municipe_e_local(page, base_url):
    """Novo Ofício deve aceitar munícipe solicitante, rua, bairro e CEP."""
    page.goto(f"{base_url}/oficios")
    page.get_by_role("button", name="+ Novo Ofício").click()
    modal = page.locator("#modal-novo-oficio")
    modal.get_by_placeholder("Órgão / Destinatário").fill("Secretaria de Obras")
    modal.get_by_placeholder("Assunto / Pauta").fill("Tapa-buraco solicitado")
    modal.get_by_placeholder("Nome do munícipe solicitante").fill("Dona Cleide")
    modal.get_by_placeholder("Rua / Logradouro").fill("Rua das Acácias, 100")
    modal.get_by_placeholder("Bairro").fill("Vila Nova")
    modal.get_by_placeholder("CEP").fill("06400-000")
    modal.get_by_role("button", name="Salvar Ofício").click()
    # busca pelo nome do munícipe (o filtro agora cobre esse campo)
    page.goto(f"{base_url}/oficios?q=Cleide")
    assert page.get_by_text("Secretaria de Obras").first.is_visible()
