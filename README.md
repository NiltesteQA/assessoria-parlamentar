# Gestão de Assessoria Parlamentar & Prestação de Contas Trimestral

Aplicação **web e mobile (responsiva)** para assessores de mandato parlamentar,
com foco em **agilidade no registro diário** de dados e na **geração de relatórios
trimestrais** (Q1–Q4) prontos para impressão/entrega ao parlamentar.

Construída em **Python** com **FastAPI**, banco **SQLite** e testes **E2E com Playwright**.

---

## ✨ Funcionalidades

- **Dashboard** com filtro por trimestre (Q1–Q4), cartões de métricas
  (atendimentos, % concluídos, ofícios respondidos/pendentes, novos contatos,
  impacto estimado) e gráficos (demandas por bairro e por categoria).
- **3 módulos de gestão** com busca, filtros e exportação **CSV/Excel**:
  - **Contatos / Redes Políticas** (nível de apoio 1–5, cargo, bairro, notas)
  - **Atendimentos e Demandas** (código `DEM-001`, categoria, status, anexos)
  - **Ofícios e Ações Oficiais** (número `OF-042/2026`, protocolo, impacto, PDF)
- **Registro Rápido** — botão flutuante (FAB) mobile-first para cadastrar
  contato, demanda ou ofício em poucos toques.
- **Gerador de Relatório Trimestral** — compila o período e exporta um
  **PDF profissional** (via WeasyPrint) com cabeçalho do mandato, resumo de
  performance, destaques, mapeamento regional e observações editáveis.
- **Feedback visual** de sucesso (toast) a cada gravação.

---

## 🧱 Stack

| Camada | Tecnologia |
|---|---|
| Backend / API | FastAPI + Uvicorn |
| Banco de dados | SQLite (via SQLAlchemy) — pronto para PostgreSQL |
| Templates | Jinja2 |
| UI / Responsivo | Tailwind CSS (CDN) |
| Gráficos | Chart.js (CDN) |
| Geração de PDF | WeasyPrint |
| Exportação CSV/Excel | pandas + openpyxl |
| Testes E2E | Playwright (pytest-playwright) |

> **Sobre o Playwright:** ele **não** constrói a aplicação — é uma ferramenta de
> automação de navegador. Aqui ele cumpre o papel correto: **testar os fluxos
> críticos de ponta a ponta** (ver `tests/`).

---

## 🚀 Como rodar

### 1. Pré-requisitos
- Python 3.12+
- Bibliotecas de sistema do WeasyPrint (Pango, Cairo, GDK-Pixbuf). No Debian/Ubuntu:
  ```bash
  sudo apt-get install -y libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev
  ```

### 2. Instalar dependências
```bash
pip install -r requirements.txt
```

### 3. (Opcional) Popular com dados de exemplo
```bash
python seed.py --reset
```

### 4. Iniciar a aplicação
```bash
./run.sh
# ou:
uvicorn app.main:app --reload
```
Acesse **http://localhost:8000**.

---

## 🧪 Testes E2E (Playwright)

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium
python -m pytest tests/ -v
```

Os testes sobem um servidor isolado com banco temporário e cobrem: dashboard,
registro rápido, filtros e geração/download do relatório em PDF.

---

## 📁 Estrutura

```
app/
├── main.py            # App FastAPI + dashboard
├── database.py        # Conexão SQLAlchemy (SQLite → PostgreSQL)
├── models.py          # Contato, Demanda, Oficio, Configuracao
├── services.py        # Métricas e agregações do trimestre
├── utils.py           # Trimestres, códigos sequenciais, uploads
├── templating.py      # Jinja2 + filtros
├── routers/           # contatos, demandas, oficios, relatorio
├── templates/         # HTML (base, dashboard, listagens, relatório, PDF)
└── static/            # CSS e JS
seed.py                # Dados de exemplo
tests/                 # Testes E2E Playwright
```

---

## 🔧 Migrar para PostgreSQL

Defina a variável de ambiente antes de iniciar:
```bash
export DATABASE_URL="postgresql+psycopg://usuario:senha@host:5432/banco"
```
A aplicação cria as tabelas automaticamente no primeiro start.
