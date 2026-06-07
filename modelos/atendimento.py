from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Atendimento:
    id: str
    cliente_id: str
    atendente_id: str
    inicio: datetime = field(default_factory=datetime.now)
    fim: datetime | None = None
    duracao_segundos: int | None = None

    @property
    def finalizado(self) -> bool:
        return self.fim is not None

    def finalizar(self) -> None:
        self.fim = datetime.now()
        delta = self.fim - self.inicio
        self.duracao_segundos = int(delta.total_seconds())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "atendente_id": self.atendente_id,
            "inicio": self.inicio.isoformat(),
            "fim": self.fim.isoformat() if self.fim else None,
            "duracao_segundos": self.duracao_segundos,
        }

    @staticmethod
    def from_dict(d: dict) -> "Atendimento":
        a = Atendimento(
            id=d["id"],
            cliente_id=d["cliente_id"],
            atendente_id=d["atendente_id"],
            inicio=datetime.fromisoformat(d["inicio"]),
        )
        if d.get("fim"):
            a.fim = datetime.fromisoformat(d["fim"])
        a.duracao_segundos = d.get("duracao_segundos")
        return a