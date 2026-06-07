from modelos.cliente import Cliente


class No:
    def __init__(self, cliente: Cliente):
        self.cliente = cliente
        self.proximo: "No | None" = None


class ListaEncadeada:
    def __init__(self):
        self.cabeca: No | None = None
        self._tamanho: int = 0

    def inserir(self, cliente: Cliente) -> None:
        novo = No(cliente)
        novo.proximo = self.cabeca
        self.cabeca = novo
        self._tamanho += 1

    def remover(self, cliente_id: str) -> bool:
        anterior = None
        atual = self.cabeca
        while atual:
            if atual.cliente.id == cliente_id:
                if anterior:
                    anterior.proximo = atual.proximo
                else:
                    self.cabeca = atual.proximo
                self._tamanho -= 1
                return True
            anterior = atual
            atual = atual.proximo
        return False

    def buscar(self, cliente_id: str) -> Cliente | None:
        atual = self.cabeca
        while atual:
            if atual.cliente.id == cliente_id:
                return atual.cliente
            atual = atual.proximo
        return None

    def listar(self) -> list[Cliente]:
        resultado = []
        atual = self.cabeca
        while atual:
            resultado.append(atual.cliente)
            atual = atual.proximo
        return resultado

    def __len__(self) -> int:
        return self._tamanho