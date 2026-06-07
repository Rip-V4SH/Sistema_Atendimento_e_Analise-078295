from collections import deque
from datetime import datetime

from modelos.cliente import Cliente

ALERTA_ESPERA_SEGUNDOS = 300


class FilaAtendimento:
    def __init__(self):
        self._fila_prioritaria: deque[tuple[Cliente, datetime]] = deque()
        self._fila_comum: deque[tuple[Cliente, datetime]] = deque()

    def entrar_na_fila(self, cliente: Cliente) -> None:
        entrada = (cliente, datetime.now())
        if cliente.prioridade == "prioritario":
            self._fila_prioritaria.append(entrada)
        else:
            self._fila_comum.append(entrada)

    def proximo(self) -> tuple[Cliente, datetime] | None:
        if self._fila_prioritaria:
            return self._fila_prioritaria.popleft()
        if self._fila_comum:
            return self._fila_comum.popleft()
        return None

    def esta_na_fila(self, cliente_id: str) -> bool:
        for c, _ in self._fila_prioritaria:
            if c.id == cliente_id:
                return True
        for c, _ in self._fila_comum:
            if c.id == cliente_id:
                return True
        return False

    def remover_da_fila(self, cliente_id: str) -> bool:
        for fila in (self._fila_prioritaria, self._fila_comum):
            for i, (c, _) in enumerate(fila):
                if c.id == cliente_id:
                    del fila[i]
                    return True
        return False

    def tamanho(self) -> dict[str, int]:
        return {
            "prioritaria": len(self._fila_prioritaria),
            "comum": len(self._fila_comum),
            "total": len(self._fila_prioritaria) + len(self._fila_comum),
        }

    def alertas_espera(self) -> list[tuple[Cliente, int]]:
        agora = datetime.now()
        alertas = []
        for c, entrada in list(self._fila_prioritaria) + list(self._fila_comum):
            segundos = int((agora - entrada).total_seconds())
            if segundos >= ALERTA_ESPERA_SEGUNDOS:
                alertas.append((c, segundos))
        return alertas

    def listar_fila(self) -> list[tuple[Cliente, datetime, str]]:
        resultado = []
        for c, entrada in self._fila_prioritaria:
            resultado.append((c, entrada, "prioritaria"))
        for c, entrada in self._fila_comum:
            resultado.append((c, entrada, "comum"))
        return resultado