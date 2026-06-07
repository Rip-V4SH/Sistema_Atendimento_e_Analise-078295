import bisect

from modelos.cliente import Cliente, validar_cliente
from modelos.atendente import Atendente, validar_atendente
from modelos.lista_encad import ListaEncadeada
import dados.repositorio as repo


class ServicoCadastro:
    def __init__(self):
        self._clientes_ordenados: list[Cliente] = []
        self._clientes_nao_ordenados: list[Cliente] = []
        self._atendentes: list[Atendente] = []
        self._lista_ativos: ListaEncadeada = ListaEncadeada()

    def inicializar(self) -> None:
        clientes = repo.carregar_clientes()
        atendentes = repo.carregar_atendentes()
        self._clientes_nao_ordenados = list(clientes)
        self._clientes_ordenados = sorted(clientes, key=lambda c: c.id)
        self._atendentes = list(atendentes)
        for c in clientes:
            if c.ativo:
                self._lista_ativos.inserir(c)

    def cadastrar_cliente(self, id: str, nome: str, telefone: str,
                          prioridade: str) -> tuple[bool, str]:
        id = id.strip().upper()
        ok, msg = validar_cliente(id, nome, telefone, prioridade)
        if not ok:
            return False, msg
        if self.buscar_cliente_por_id(id) is not None:
            return False, f"Cliente '{id}' ja existe."
        cliente = Cliente(id=id, nome=nome.strip(), telefone=telefone.strip(),
                          prioridade=prioridade.strip().lower())
        self._clientes_nao_ordenados.append(cliente)
        bisect.insort(self._clientes_ordenados, cliente, key=lambda c: c.id)
        self._lista_ativos.inserir(cliente)
        repo.salvar_clientes(self._clientes_nao_ordenados)
        repo.registrar_log(f"CADASTRO cliente '{id}' - {nome}")
        return True, ""

    def editar_cliente(self, id: str, nome: str | None, telefone: str | None,
                       prioridade: str | None) -> tuple[bool, str]:
        cliente = self.buscar_cliente_por_id(id)
        if not cliente:
            return False, f"Cliente '{id}' nao encontrado."
        if nome:
            cliente.nome = nome.strip()
        if telefone:
            cliente.telefone = telefone.strip()
        if prioridade:
            if prioridade.strip().lower() not in {"normal", "prioritario"}:
                return False, "Prioridade invalida."
            cliente.prioridade = prioridade.strip().lower()
        repo.salvar_clientes(self._clientes_nao_ordenados)
        repo.registrar_log(f"EDICAO cliente '{id}'")
        return True, ""

    def cadastrar_atendente(self, id: str, nome: str) -> tuple[bool, str]:
        id = id.strip().upper()
        ok, msg = validar_atendente(id, nome)
        if not ok:
            return False, msg
        if any(a.id == id for a in self._atendentes):
            return False, f"Atendente '{id}' ja existe."
        atendente = Atendente(id=id, nome=nome.strip())
        self._atendentes.append(atendente)
        repo.salvar_atendentes(self._atendentes)
        repo.registrar_log(f"CADASTRO atendente '{id}' - {nome}")
        return True, ""

    def buscar_cliente_por_id(self, id: str) -> Cliente | None:
        id = id.strip().upper()
        ids = [c.id for c in self._clientes_ordenados]
        pos = bisect.bisect_left(ids, id)
        if pos < len(self._clientes_ordenados) and self._clientes_ordenados[pos].id == id:
            return self._clientes_ordenados[pos]
        return None

    def buscar_atendente_por_id(self, id: str) -> Atendente | None:
        id = id.strip().upper()
        return next((a for a in self._atendentes if a.id == id), None)

    def listar_clientes(self) -> list[Cliente]:
        return list(self._clientes_ordenados)

    def listar_atendentes(self) -> list[Atendente]:
        return list(self._atendentes)

    def listar_ativos(self) -> list[Cliente]:
        return self._lista_ativos.listar()

    def remover_inativos(self, atendimentos_abertos_ids: set[str]) -> list[str]:
        removidos = []
        for cliente in self._clientes_nao_ordenados:
            if not cliente.ativo:
                continue
            if cliente.id in atendimentos_abertos_ids:
                continue
            cliente.ativo = False
            self._lista_ativos.remover(cliente.id)
            removidos.append(cliente.id)
        if removidos:
            repo.salvar_clientes(self._clientes_nao_ordenados)
            repo.registrar_log(f"REMOCAO inativos: {removidos}")
        return removidos

    def clientes_ordenados(self) -> list[Cliente]:
        return list(self._clientes_ordenados)

    @property
    def atendentes(self) -> list[Atendente]:
        return self._atendentes