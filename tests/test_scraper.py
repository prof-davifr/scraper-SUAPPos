"""Testes sem rede da leitura do XLS exportado pelo SUAP."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scraper import AlunosScraper  # noqa: E402


def test_xlrd_ausente_diz_a_causa_e_como_instalar(monkeypatch):
    # Com None em sys.modules, `import xlrd` falha como se o pacote não existisse.
    monkeypatch.setitem(sys.modules, "xlrd", None)

    with pytest.raises(ImportError) as excinfo:
        AlunosScraper._read_xls(b"conteudo qualquer de um .xls")

    message = str(excinfo.value)
    assert "xlrd" in message
    assert "pip install -r requirements.txt" in message
    assert "zip" not in message


class _FakeLink:
    def click(self):
        pass


class _FakeDriver:
    def find_element(self, by, value):
        return _FakeLink()

    def get_cookies(self):
        return []

    def execute_script(self, script):
        return "pytest"


class _FakeResponse:
    status_code = 200
    content = b"\xd0\xcf\x11\xe0" + b"\x00" * 200


class _FakeSession:
    def __init__(self):
        self.cookies = self
        self.headers = {}

    def set(self, *args, **kwargs):
        pass

    def get(self, url, **kwargs):
        return _FakeResponse()


def test_xlrd_ausente_interrompe_a_coleta(monkeypatch, tmp_path):
    """O ImportError sai do _export_and_parse em vez de virar lista vazia."""
    import requests

    from src.config import Config

    monkeypatch.setitem(sys.modules, "xlrd", None)
    monkeypatch.setattr(requests, "Session", _FakeSession)
    monkeypatch.setattr(Config, "OUTPUT_DIR", str(tmp_path))
    monkeypatch.setattr(AlunosScraper, "_wait_for_task_completion", lambda self: "1")

    scraper = AlunosScraper(_FakeDriver())
    with pytest.raises(ImportError, match="pip install -r requirements.txt"):
        scraper._export_and_parse()


def test_arquivo_ilegivel_mantem_o_erro_do_xlrd():
    pytest.importorskip("xlrd")

    with pytest.raises(ValueError) as excinfo:
        AlunosScraper._read_xls(b"isto nao e uma planilha")

    assert "xlrd said" in str(excinfo.value)
    assert excinfo.value.__cause__ is not None
