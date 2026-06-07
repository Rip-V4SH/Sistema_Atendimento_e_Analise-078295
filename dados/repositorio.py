import json
import os
from datetime import datetime

from modelos.cliente import Cliente
from modelos.atendente import Atendente
from modelos.atendente import Atendimento

PASTA_DADOS = os.path.join(os.path.dirname(__file__), "arquivos")
ARQUIVO_CLIENTES = os.path.join(PASTA_DADOS, "clientes.json")
ARQUIVO_ATENDENTES = os.path.join(PASTA_DADOS, "atendentes.json")
ARQUIVO_ATENDIMENTOS = os.path.join(PASTA_DADOS, "atendimentos.json")
ARQUIVO_LOG = os.path.join(PASTA_DADOS, "operacoes.log")


def _garantir_pasta() -> None:
    os.makedirs(PASTA_DADOS, exist_ok=True)


def _salvar_json(caminho: str, dados: list[dict]) -> None:
    _garantir_pasta()
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def _carregar_json(caminho: str) -> list[dict]:
    if not os.path.exists(caminho):
        return []
    with open(caminho, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def salvar_clientes(clientes: list[Cliente]) -> None:
    _salvar_json(ARQUIVO_CLIENTES, [c.to_dict() for c in clientes])


def carregar_clientes() -> list[Cliente]:
    return [Cliente.from_dict(d) for d in _carregar_json(ARQUIVO_CLIENTES)]


def salvar_atendentes(atendentes: list[Atendente]) -> None:
    _salvar_json(ARQUIVO_ATENDENTES, [a.to_dict() for a in atendentes])


def carregar_atendentes() -> list[Atendente]:
    return [Atendente.from_dict(d) for d in _carregar_json(ARQUIVO_ATENDENTES)]


def salvar_atendimentos(atendimentos: list[Atendimento]) -> None:
    _salvar_json(ARQUIVO_ATENDIMENTOS, [a.to_dict() for a in atendimentos])


def carregar_atendimentos() -> list[Atendimento]:
    return [Atendimento.from_dict(d) for d in _carregar_json(ARQUIVO_ATENDIMENTOS)]


def registrar_log(operacao: str) -> None:
    _garantir_pasta()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {operacao}\n")