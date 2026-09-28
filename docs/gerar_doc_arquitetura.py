"""Gera um PDF com o desenho da arquitetura de acesso (login e perfis).

Uso: python docs/gerar_doc_arquitetura.py
Saída: docs/arquitetura-acesso.pdf
"""
import os
from datetime import date

from weasyprint import HTML

BASE = os.path.dirname(os.path.abspath(__file__))

HTML_DOC = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8" />
<style>
  @page {{
    size: A4;
    margin: 1.8cm 1.8cm;
    @bottom-center {{
      content: "Assessoria Águia · Arquitetura de Acesso · página " counter(page) " de " counter(pages);
      font-size: 8pt; color: #94a3b8;
    }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: #1e293b; font-size: 10.5pt; line-height: 1.5; }}
  .capa {{ border-bottom: 3px solid #243b53; padding-bottom: 14px; margin-bottom: 20px; }}
  .capa .eyebrow {{ font-size: 8pt; text-transform: uppercase; letter-spacing: 1px; color: #64748b; }}
  .capa h1 {{ font-size: 20pt; color: #102a43; margin: 4px 0; }}
  .capa .sub {{ font-size: 10pt; color: #475569; }}
  h2 {{ font-size: 12pt; color: #243b53; border-left: 4px solid #334e68; padding-left: 8px; margin: 22px 0 8px; }}
  h3 {{ font-size: 10.5pt; color: #334e68; margin: 14px 0 4px; }}
  .card {{ border: 1px solid #cbd5e1; border-radius: 8px; padding: 12px 14px; margin: 8px 0; background: #f8fafc; }}
  .card.admin {{ border-color: #b45309; background: #fffbeb; }}
  .card.user {{ border-color: #1d4ed8; background: #eff6ff; }}
  .card .titulo {{ font-weight: bold; font-size: 11pt; margin-bottom: 4px; }}
  ul {{ margin: 4px 0 4px 0; padding-left: 18px; }}
  li {{ margin: 2px 0; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 6px 0; }}
  th {{ background: #243b53; color: #fff; text-align: left; padding: 6px 8px; }}
  td {{ padding: 5px 8px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }}
  tr:nth-child(even) td {{ background: #f8fafc; }}
  .diagrama {{ text-align: center; margin: 14px 0; }}
  .box {{ display: inline-block; border: 2px solid #243b53; border-radius: 8px; padding: 10px 16px; margin: 6px; font-size: 9.5pt; background: #fff; }}
  .box.adminbox {{ border-color: #b45309; background: #fffbeb; font-weight: bold; }}
  .seta {{ font-size: 14pt; color: #64748b; margin: 4px 0; }}
  .fila {{ margin: 8px 0; }}
  .nota {{ font-size: 9pt; color: #64748b; font-style: italic; }}
  .badge {{ display:inline-block; font-size:8pt; padding:1px 8px; border-radius:10px; }}
  .p-alta {{ background:#fee2e2; color:#b91c1c; }}
  .p-media {{ background:#ffedd5; color:#c2410c; }}
  .p-baixa {{ background:#fef9c3; color:#a16207; }}
</style>
</head>
<body>

  <div class="capa">
    <div class="eyebrow">Documento Técnico · Planejamento</div>
    <h1>Arquitetura de Controle de Acesso</h1>
    <div class="sub">Assessoria Águia — Sistema de Gestão de Assessoria Parlamentar</div>
    <div class="sub">Gerado em {date.today().strftime('%d/%m/%Y')}</div>
  </div>

  <h2>1. Objetivo</h2>
  <p>Implementar um sistema de acesso com <b>dois níveis hierárquicos</b>, permitindo que cada
  assessor gerencie apenas os seus próprios dados e que o vereador / chefe de gabinete
  supervisione o trabalho de toda a equipe.</p>

  <h2>2. Níveis de Acesso (Perfis)</h2>

  <div class="card user">
    <div class="titulo">👤 Assessor (usuário comum)</div>
    <ul>
      <li>Login individual (credenciais próprias).</li>
      <li>Vê e gerencia <b>apenas os seus próprios</b> contatos, demandas e ofícios.</li>
      <li>Não enxerga o trabalho dos demais assessores.</li>
      <li>Gera os próprios relatórios trimestrais.</li>
    </ul>
  </div>

  <div class="card admin">
    <div class="titulo">👑 Vereador / Chefe de Gabinete (administrador)</div>
    <ul>
      <li>Login com conta administrativa (senha mestre).</li>
      <li>Visualiza o trabalho de <b>todos os assessores</b>.</li>
      <li>Painel de supervisão: acompanha produtividade e cumprimento de tarefas.</li>
      <li>Filtra os dados por assessor.</li>
      <li>Cria, edita e desativa contas de assessores.</li>
      <li>Relatório consolidado de todo o gabinete.</li>
    </ul>
  </div>

  <h2>3. Diagrama de Hierarquia</h2>
  <div class="diagrama">
    <div class="fila">
      <div class="box adminbox">👑 VEREADOR / CHEFE DE GABINETE<br/><span class="nota">enxerga tudo de todos</span></div>
    </div>
    <div class="seta">▲ &nbsp; supervisiona</div>
    <div class="fila">
      <div class="box">👤 Assessor A<br/><span class="nota">só vê o dele</span></div>
      <div class="box">👤 Assessor B<br/><span class="nota">só vê o dele</span></div>
      <div class="box">👤 Assessor C<br/><span class="nota">só vê o dele</span></div>
    </div>
  </div>
  <p class="nota">Cada contato, demanda e ofício fica vinculado ao assessor que o criou.
  O administrador tem visão agregada; os assessores têm visão isolada dos próprios dados.</p>

  <h2>4. Roteiro de Implementação (por etapas)</h2>
  <p>As mudanças serão adicionadas <b>aos poucos</b>, cada etapa com código, testes automatizados e envio ao repositório.</p>
  <table>
    <thead>
      <tr><th style="width:8%">Etapa</th><th>Descrição</th><th style="width:20%">Prioridade</th></tr>
    </thead>
    <tbody>
      <tr><td>1</td><td>Modelo de <b>Usuário</b> com papéis (assessor / admin) e senhas protegidas por hash.</td><td><span class="badge p-alta">Essencial</span></td></tr>
      <tr><td>2</td><td>Tela de <b>login / logout</b> e proteção de todas as rotas.</td><td><span class="badge p-alta">Essencial</span></td></tr>
      <tr><td>3</td><td>Vincular contatos, demandas e ofícios ao <b>assessor dono</b>.</td><td><span class="badge p-alta">Essencial</span></td></tr>
      <tr><td>4</td><td>Filtragem de dados: assessor vê os seus; admin vê todos.</td><td><span class="badge p-alta">Essencial</span></td></tr>
      <tr><td>5</td><td><b>Painel do gestor</b>: supervisão de produtividade por assessor.</td><td><span class="badge p-media">Importante</span></td></tr>
      <tr><td>6</td><td>Administração de contas: criar, editar e desativar assessores.</td><td><span class="badge p-media">Importante</span></td></tr>
    </tbody>
  </table>

  <h2>5. Considerações de Segurança</h2>
  <ul>
    <li>Senhas nunca são armazenadas em texto puro — sempre com <b>hash</b> (ex.: bcrypt).</li>
    <li>Sessões seguras e proteção contra acesso não autorizado às rotas.</li>
    <li>Isolamento de dados entre assessores (um não acessa dados do outro).</li>
    <li>Recomendado: HTTPS, backups automáticos e banco PostgreSQL em produção.</li>
    <li><b>LGPD:</b> como há dados pessoais, recomenda-se política de privacidade, base legal
    para o tratamento e mecanismo de exclusão a pedido do titular. Consultar profissional jurídico.</li>
  </ul>

  <p class="nota">Documento de planejamento técnico. As definições podem ser ajustadas conforme a evolução do projeto.</p>

</body>
</html>
"""


def main():
    out = os.path.join(BASE, "arquitetura-acesso.pdf")
    HTML(string=HTML_DOC).write_pdf(out)
    print("PDF gerado:", out)


if __name__ == "__main__":
    main()
