"""Modelos de dados: Contatos, Demandas e Ofícios.

Os três módulos centrais do sistema de Gestão de Assessoria Parlamentar.
"""
from datetime import date, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


# --- Opções (constantes) usadas em selects e validações -------------------

CARGOS = [
    "Presidente de Bairro",
    "Comerciante",
    "Líder Comunitário",
    "Eleitor",
    "Apoiador",
    "Outro",
]

CATEGORIAS_DEMANDA = [
    "Saúde",
    "Obras / Tapa-buraco",
    "Iluminação",
    "Educação",
    "Segurança",
    "Transporte",
    "Outros",
]

STATUS_DEMANDA = ["Pendente", "Em Andamento", "Concluído", "Cancelado"]

STATUS_OFICIO = [
    "Enviado",
    "Aguardando Resposta",
    "Respondido / Atendido",
    "Arquivado",
]


class Contato(Base):
    """Contatos / Redes Políticas."""

    __tablename__ = "contatos"

    id = Column(Integer, primary_key=True, index=True)
    nome_completo = Column(String(200), nullable=False)
    cargo = Column(String(100), nullable=False, default="Eleitor")
    bairro = Column(String(120), nullable=False, default="")
    telefone = Column(String(40), default="")
    nivel_apoio = Column(Integer, default=3)  # escala 1 a 5
    data_cadastro = Column(Date, default=date.today, nullable=False)
    notas = Column(Text, default="")

    demandas = relationship("Demanda", back_populates="solicitante")

    def to_dict(self):
        return {
            "id": self.id,
            "nome_completo": self.nome_completo,
            "cargo": self.cargo,
            "bairro": self.bairro,
            "telefone": self.telefone,
            "nivel_apoio": self.nivel_apoio,
            "data_cadastro": self.data_cadastro.isoformat() if self.data_cadastro else "",
            "notas": self.notas,
        }


class Demanda(Base):
    """Atendimentos e Demandas."""

    __tablename__ = "demandas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, index=True)  # Ex: DEM-001
    data_entrada = Column(Date, default=date.today, nullable=False)
    solicitante_id = Column(Integer, ForeignKey("contatos.id"), nullable=True)
    solicitante_nome = Column(String(200), default="")  # fallback textual
    bairro = Column(String(120), default="")
    categoria = Column(String(60), default="Outros")
    descricao = Column(Text, default="")
    status = Column(String(30), default="Pendente")
    anexo = Column(String(300), default="")  # caminho relativo do arquivo

    solicitante = relationship("Contato", back_populates="demandas")

    def to_dict(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "data_entrada": self.data_entrada.isoformat() if self.data_entrada else "",
            "solicitante_id": self.solicitante_id,
            "solicitante_nome": (
                self.solicitante.nome_completo
                if self.solicitante
                else self.solicitante_nome
            ),
            "bairro": self.bairro,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "status": self.status,
            "anexo": self.anexo,
        }


class Oficio(Base):
    """Ofícios e Ações Oficiais."""

    __tablename__ = "oficios"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(40), unique=True, index=True)  # Ex: OF-042/2026
    data_envio = Column(Date, default=date.today, nullable=False)
    orgao_destinatario = Column(String(200), default="")
    assunto = Column(String(300), default="")
    status = Column(String(40), default="Enviado")
    numero_protocolo = Column(String(80), default="")
    impacto_estimado = Column(Integer, default=0)  # nº de pessoas/famílias
    anexo = Column(String(300), default="")

    def to_dict(self):
        return {
            "id": self.id,
            "numero": self.numero,
            "data_envio": self.data_envio.isoformat() if self.data_envio else "",
            "orgao_destinatario": self.orgao_destinatario,
            "assunto": self.assunto,
            "status": self.status,
            "numero_protocolo": self.numero_protocolo,
            "impacto_estimado": self.impacto_estimado,
            "anexo": self.anexo,
        }


class Configuracao(Base):
    """Configurações do mandato (cabeçalho de relatórios)."""

    __tablename__ = "configuracao"

    id = Column(Integer, primary_key=True)
    nome_assessor = Column(String(200), default="Assessor(a) Parlamentar")
    nome_mandato = Column(String(200), default="Mandato Parlamentar")
    atualizado_em = Column(DateTime, default=datetime.utcnow)
