"""Testes sem rede e sem credencial das funções puras de configuração e modalidade.

O `main.py` fica de fora de propósito: importá-lo abre o `scraper.log` na
pasta corrente (o `FileHandler` é criado na importação).
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config import Config  # noqa: E402
from src.scraper import AlunosScraper  # noqa: E402


def test_ids_das_tres_modalidades():
    assert Config.MODALIDADE_MESTRADO == 9
    assert Config.MODALIDADE_ESPECIALIZACAO == 10
    assert Config.MODALIDADE_DOUTORADO == 16


@pytest.mark.parametrize(
    ("modalidade_id", "nome"),
    [
        (9, "Mestrado"),
        (10, "Especialização"),
        (16, "Doutorado"),
        (99, "Modalidade 99"),
    ],
)
def test_nome_da_modalidade(modalidade_id, nome):
    assert AlunosScraper._get_modalidade_name(modalidade_id) == nome


def test_url_sem_modalidade_e_o_changelist_puro(monkeypatch):
    monkeypatch.setattr(Config, "SUAP_ALUNOS_URL", "https://suap.exemplo/admin/edu/aluno/")
    assert Config.get_alunos_url_filtered() == "https://suap.exemplo/admin/edu/aluno/"


def test_url_com_modalidade_filtra_pelo_id(monkeypatch):
    monkeypatch.setattr(Config, "SUAP_ALUNOS_URL", "https://suap.exemplo/admin/edu/aluno/")
    assert Config.get_alunos_url_filtered(10) == (
        "https://suap.exemplo/admin/edu/aluno/"
        "?curso_campus__modalidade__id__exact=10&tab=tab_any_data"
    )


def test_validate_sem_credencial_aponta_usuario_e_senha(monkeypatch):
    monkeypatch.setattr(Config, "SUAP_USERNAME", "")
    monkeypatch.setattr(Config, "SUAP_PASSWORD", "")
    monkeypatch.setattr(Config, "OUTPUT_FORMAT", "csv")
    assert Config.validate() == ["SUAP_USERNAME is required", "SUAP_PASSWORD is required"]


def test_validate_recusa_formato_desconhecido(monkeypatch):
    monkeypatch.setattr(Config, "SUAP_USERNAME", "usuario")
    monkeypatch.setattr(Config, "SUAP_PASSWORD", "senha-de-teste")
    monkeypatch.setattr(Config, "OUTPUT_FORMAT", "parquet")
    assert Config.validate() == ["Invalid OUTPUT_FORMAT: parquet"]


def test_validate_aceita_configuracao_completa(monkeypatch):
    monkeypatch.setattr(Config, "SUAP_USERNAME", "usuario")
    monkeypatch.setattr(Config, "SUAP_PASSWORD", "senha-de-teste")
    for fmt in ("csv", "json", "xlsx"):
        monkeypatch.setattr(Config, "OUTPUT_FORMAT", fmt)
        assert Config.validate() == []
