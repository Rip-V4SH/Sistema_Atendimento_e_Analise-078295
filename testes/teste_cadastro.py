import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modelos.cliente import validar_cliente
from modelos.atendente import validar_atendente
from modelos.lista_encad import ListaEncadeada
from modelos.cliente import Cliente
from datetime import datetime


class TestValidarCliente(unittest.TestCase):
    def test_valido(self):
        ok, msg = validar_cliente("C001", "Ana", "99999", "normal")
        self.assertTrue(ok)

    def test_id_vazio(self):
        ok, msg = validar_cliente("", "Ana", "99999", "normal")
        self.assertFalse(ok)

    def test_prioridade_invalida(self):
        ok, msg = validar_cliente("C001", "Ana", "99999", "vip")
        self.assertFalse(ok)

    def test_nome_vazio(self):
        ok, msg = validar_cliente("C001", "", "99999", "normal")
        self.assertFalse(ok)

    def test_prioridade_prioritario(self):
        ok, msg = validar_cliente("C001", "Ana", "99999", "prioritario")
        self.assertTrue(ok)


class TestValidarAtendente(unittest.TestCase):
    def test_valido(self):
        ok, msg = validar_atendente("A001", "Carlos")
        self.assertTrue(ok)

    def test_id_vazio(self):
        ok, msg = validar_atendente("", "Carlos")
        self.assertFalse(ok)

    def test_nome_vazio(self):
        ok, msg = validar_atendente("A001", "")
        self.assertFalse(ok)


class TestListaEncadeada(unittest.TestCase):
    def _criar_cliente(self, id: str) -> Cliente:
        return Cliente(id=id, nome=f"Cliente {id}", telefone="0000",
                       prioridade="normal", cadastrado_em=datetime.now())

    def test_inserir_e_listar(self):
        lista = ListaEncadeada()
        lista.inserir(self._criar_cliente("C1"))
        lista.inserir(self._criar_cliente("C2"))
        self.assertEqual(len(lista), 2)

    def test_remover(self):
        lista = ListaEncadeada()
        lista.inserir(self._criar_cliente("C1"))
        lista.inserir(self._criar_cliente("C2"))
        removido = lista.remover("C1")
        self.assertTrue(removido)
        self.assertEqual(len(lista), 1)

    def test_remover_inexistente(self):
        lista = ListaEncadeada()
        removido = lista.remover("C99")
        self.assertFalse(removido)

    def test_buscar(self):
        lista = ListaEncadeada()
        lista.inserir(self._criar_cliente("C1"))
        cliente = lista.buscar("C1")
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.id, "C1")

    def test_buscar_inexistente(self):
        lista = ListaEncadeada()
        cliente = lista.buscar("C99")
        self.assertIsNone(cliente)


class TestFilaAtendimento(unittest.TestCase):
    def _criar_cliente(self, id: str, prioridade: str = "normal") -> Cliente:
        return Cliente(id=id, nome=f"Cliente {id}", telefone="0000",
                       prioridade=prioridade, cadastrado_em=datetime.now())

    def test_fila_prioridade_na_frente(self):
        from servicos.fila import FilaAtendimento
        fila = FilaAtendimento()
        fila.entrar_na_fila(self._criar_cliente("C1", "normal"))
        fila.entrar_na_fila(self._criar_cliente("C2", "prioritario"))
        proximo, _ = fila.proximo()
        self.assertEqual(proximo.id, "C2")

    def test_fila_vazia_retorna_none(self):
        from servicos.fila import FilaAtendimento
        fila = FilaAtendimento()
        self.assertIsNone(fila.proximo())

    def test_esta_na_fila(self):
        from servicos.fila import FilaAtendimento
        fila = FilaAtendimento()
        fila.entrar_na_fila(self._criar_cliente("C1"))
        self.assertTrue(fila.esta_na_fila("C1"))
        self.assertFalse(fila.esta_na_fila("C99"))


class TestRelatorios(unittest.TestCase):
    def _criar_atendimento(self, cliente_id: str, dur: int):
        from modelos.atendimento import Atendimento
        from datetime import timedelta
        a = Atendimento(id="X", cliente_id=cliente_id, atendente_id="A1")
        a.fim = a.inicio + timedelta(seconds=dur)
        a.duracao_segundos = dur
        return a

    def test_tempo_medio(self):
        from relatorios.gerador import tempo_medio_atendimento
        atds = [self._criar_atendimento("C1", 100), self._criar_atendimento("C2", 200)]
        self.assertAlmostEqual(tempo_medio_atendimento(atds), 150.0)

    def test_tempo_medio_sem_finalizados(self):
        from relatorios.gerador import tempo_medio_atendimento
        from modelos.atendimento import Atendimento
        atds = [Atendimento(id="X", cliente_id="C1", atendente_id="A1")]
        self.assertEqual(tempo_medio_atendimento(atds), 0.0)

    def test_top_clientes(self):
        from relatorios.gerador import top_clientes
        from modelos.cliente import Cliente
        from datetime import datetime
        atds = [
            self._criar_atendimento("C1", 60),
            self._criar_atendimento("C1", 60),
            self._criar_atendimento("C2", 60),
        ]
        clientes = [
            Cliente("C1", "Ana", "0", "normal", True, datetime.now()),
            Cliente("C2", "Bia", "0", "normal", True, datetime.now()),
        ]
        top = top_clientes(atds, clientes, n=5)
        self.assertEqual(top[0]["cliente_id"], "C1")
        self.assertEqual(top[0]["total"], 2)


if __name__ == "__main__":
    unittest.main()