from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Atendente:
    id: str
    nome: str
    cliente_atual_id: str | None = None
    cadastrado_em: datetime = field(default_factory=datetime.now)

    @property
    def disponivel(self) -> bool:
        return self.cliente_atual_id is None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "cliente_atual_id": self.cliente_atual_id,
            "cadastrado_em": self.cadastrado_em.isoformat(),
        }

    @staticmethod
    def from_dict(d: dict) -> "Atendente":
        return Atendente(
            id=d["id"],
            nome=d["nome"],
            cliente_atual_id=d.get("cliente_atual_id"),
            cadastrado_em=datetime.fromisoformat(d["cadastrado_em"]),
        )


def validar_atendente(id: str, nome: str) -> tuple[bool, str]:
    if not id.strip():
        return False, "ID nao pode ser vazio."
    if len(id.strip()) > 20:
        return False, "ID deve ter no maximo 20 caracteres."
    if not nome.strip():
        return False, "Nome nao pode ser vazio."
    return True, ""