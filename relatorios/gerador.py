import csv
import os
from datetime import datetime, date

from modelos.atendimento import Atendimento
from modelos.cliente import Cliente
from modelos.atendente import Atendente

PASTA_RELATORIOS = os.path.join(os.path.dirname(__file__), "exportados")


def _garantir_pasta() -> None:
    os.makedirs(PASTA_RELATORIOS, exist_ok=True)


def _merge_sort(lista: list[Atendimento], chave) -> list[Atendimento]:
    if len(lista) <= 1:
        return lista
    meio = len(lista) // 2
    esq = _merge_sort(lista[:meio], chave)
    dir = _merge_sort(lista[meio:], chave)
    return _merge(esq, dir, chave)


def _merge(esq: list, dir: list, chave) -> list:
    resultado = []
    i = j = 0
    while i < len(esq) and j < len(dir):
        if chave(esq[i]) <= chave(dir[j]):
            resultado.append(esq[i])
            i += 1
        else:
            resultado.append(dir[j])
            j += 1
    resultado.extend(esq[i:])
    resultado.extend(dir[j:])
    return resultado


def tempo_medio_atendimento(atendimentos: list[Atendimento]) -> float:
    finalizados = [a for a in atendimentos if a.finalizado and a.duracao_segundos]
    if not finalizados:
        return 0.0
    total = sum(a.duracao_segundos for a in finalizados)
    return total / len(finalizados)


def tempo_medio_por_atendente(atendimentos: list[Atendimento],
                               atendentes: list[Atendente]) -> list[dict]:
    resultado = []
    for atendente in atendentes:
        finalizados = [
            a for a in atendimentos
            if a.atendente_id == atendente.id and a.finalizado and a.duracao_segundos
        ]
        media = sum(a.duracao_segundos for a in finalizados) / len(finalizados) if finalizados else 0
        resultado.append({
            "atendente_id": atendente.id,
            "nome": atendente.nome,
            "total_atendimentos": len(finalizados),
            "media_segundos": round(media, 1),
        })
    return resultado


def top_clientes(atendimentos: list[Atendimento],
                 clientes: list[Cliente], n: int = 5) -> list[dict]:
    contagem: dict[str, int] = {}
    for a in atendimentos:
        if a.finalizado:
            contagem[a.cliente_id] = contagem.get(a.cliente_id, 0) + 1
    clientes_map = {c.id: c.nome for c in clientes}
    ranking = [
        {"cliente_id": cid, "nome": clientes_map.get(cid, "?"), "total": total}
        for cid, total in contagem.items()
    ]
    ranking.sort(key=lambda x: x["total"], reverse=True)
    return ranking[:n]


def filtrar_por_data(atendimentos: list[Atendimento],
                     data_inicio: date, data_fim: date) -> list[Atendimento]:
    return [
        a for a in atendimentos
        if data_inicio <= a.inicio.date() <= data_fim
    ]


def atendimentos_ordenados_por_inicio(atendimentos: list[Atendimento]) -> list[Atendimento]:
    return _merge_sort(list(atendimentos), chave=lambda a: a.inicio)


def exportar_csv_atendimentos(atendimentos: list[Atendimento],
                               clientes: list[Cliente],
                               atendentes: list[Atendente]) -> str:
    _garantir_pasta()
    nome_arquivo = f"atendimentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    caminho = os.path.join(PASTA_RELATORIOS, nome_arquivo)
    clientes_map = {c.id: c.nome for c in clientes}
    atendentes_map = {a.id: a.nome for a in atendentes}
    ordenados = atendimentos_ordenados_por_inicio(atendimentos)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "cliente_id", "cliente_nome", "atendente_id",
            "atendente_nome", "inicio", "fim", "duracao_segundos"
        ])
        for a in ordenados:
            writer.writerow([
                a.id,
                a.cliente_id,
                clientes_map.get(a.cliente_id, ""),
                a.atendente_id,
                atendentes_map.get(a.atendente_id, ""),
                a.inicio.strftime("%Y-%m-%d %H:%M:%S"),
                a.fim.strftime("%Y-%m-%d %H:%M:%S") if a.fim else "",
                a.duracao_segundos or "",
            ])
    return caminho


def exportar_csv_clientes(clientes: list[Cliente]) -> str:
    _garantir_pasta()
    nome_arquivo = f"clientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    caminho = os.path.join(PASTA_RELATORIOS, nome_arquivo)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "nome", "telefone", "prioridade", "ativo", "cadastrado_em"])
        for c in clientes:
            writer.writerow([
                c.id, c.nome, c.telefone, c.prioridade,
                "sim" if c.ativo else "nao",
                c.cadastrado_em.strftime("%Y-%m-%d %H:%M:%S"),
            ])
    return caminho