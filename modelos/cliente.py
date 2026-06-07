from dataclasses import dataclass, field
from datetime import datetime

PRIORIDADES_VALIDAS = {"normal", "prioritario"}


@dataclass
class Cliente:
    id: str
    nome: str
    telefone: str
    prioridade: str
    ativo: bool = True
    cadastrado_em: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "telefone": self.telefone,
            "prioridade": self.prioridade,
            "ativo": self.ativo,
            "cadastrado_em": self.cadastrado_em.isoformat(),
        }

    @staticmethod
    def from_dict(d: dict) -> "Cliente":
        return Cliente(
            id=d["id"],
            nome=d["nome"],
            telefone=d["telefone"],
            prioridade=d["prioridade"],
            ativo=d.get("ativo", True),
            cadastrado_em=datetime.fromisoformat(d["cadastrado_em"]),
        )


def validar_cliente(id: str, nome: str, telefone: str, prioridade: str) -> tuple[bool, str]:
    if not id.strip():
        return False, "ID nao pode ser vazio."
    if len(id.strip()) > 20:
        return False, "ID deve ter no maximo 20 caracteres."
    if not nome.strip():
        return False, "Nome nao pode ser vazio."
    if not telefone.strip():
        return False, "Telefone nao pode ser vazio."
    if prioridade.strip().lower() not in PRIORIDADES_VALIDAS:
        return False, f"Prioridade invalida. Use: {', '.join(PRIORIDADES_VALIDAS)}."
    return True, ""