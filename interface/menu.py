import os
import sys
from datetime import datetime, date

from servicos.cadastro import ServicoCadastro
from servicos.fila import FilaAtendimento
from servicos.atendimento import ServicoAtendimento
from relatorios.gerador import (
    tempo_medio_atendimento,
    tempo_medio_por_atendente,
    top_clientes,
    filtrar_por_data,
    exportar_csv_atendimentos,
    exportar_csv_clientes,
    atendimentos_ordenados_por_inicio,
)
import dados.repositorio as repo

SEPARADOR = "─" * 56


def limpar_tela() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pausar() -> None:
    input("\nPressione Enter para continuar...")


def cabecalho(titulo: str) -> None:
    print(f"\n{SEPARADOR}\n  {titulo}\n{SEPARADOR}")


def ler_input(prompt: str, obrigatorio: bool = True) -> str:
    while True:
        valor = input(prompt).strip()
        if obrigatorio and not valor:
            print("  ⚠  Campo obrigatorio. Tente novamente.")
            continue
        return valor


def ler_data(prompt: str) -> date | None:
    valor = ler_input(prompt, obrigatorio=False)
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        print("  ⚠  Data invalida. Use o formato AAAA-MM-DD.")
        return None


class Menu:
    def __init__(self):
        self.cadastro = ServicoCadastro()
        self.fila = FilaAtendimento()
        self.atendimento = ServicoAtendimento()

    def inicializar(self) -> None:
        self.cadastro.inicializar()
        self.atendimento.inicializar()
        em_aberto = self.atendimento.atendimentos_em_aberto()
        for a in em_aberto:
            cliente = self.cadastro.buscar_cliente_por_id(a.cliente_id)
            if cliente:
                self.fila.entrar_na_fila(cliente)

    def executar(self) -> None:
        self.inicializar()
        while True:
            self._exibir_menu_principal()
            escolha = input("  Opcao: ").strip()
            acoes = {
                "1": self._menu_clientes,
                "2": self._menu_atendentes,
                "3": self._abrir_atendimento,
                "4": self._chamar_proximo,
                "5": self._finalizar_atendimento,
                "6": self._desfazer_finalizacao,
                "7": self._ver_historico_cliente,
                "8": self._remover_inativos,
                "9": self._menu_relatorios,
                "0": self._sair,
            }
            if escolha in acoes:
                acoes[escolha]()
            else:
                print("  ⚠  Opcao invalida.")
                pausar()

    def _exibir_menu_principal(self) -> None:
        limpar_tela()
        tamanho = self.fila.tamanho()
        alertas = self.fila.alertas_espera()
        print(f"\n{'═' * 56}")
        print("   🏥  SISTEMA DE ATENDIMENTO")
        print(f"{'═' * 56}")
        print(f"  Fila: {tamanho['prioritaria']} prioritarios | {tamanho['comum']} comuns")
        if alertas:
            print(f"  ⚠  {len(alertas)} cliente(s) esperando ha mais de 5 min!")
        print(f"{'═' * 56}")
        opcoes = [
            ("1", "Gerenciar clientes"),
            ("2", "Gerenciar atendentes"),
            ("3", "Abrir atendimento (entrar na fila)"),
            ("4", "Chamar proximo"),
            ("5", "Finalizar atendimento"),
            ("6", "Desfazer ultima finalizacao"),
            ("7", "Historico de cliente"),
            ("8", "Remover clientes inativos"),
            ("9", "Relatorios"),
            ("0", "Sair"),
        ]
        for op, desc in opcoes:
            print(f"  [{op}] {desc}")
        print(f"{'═' * 56}")

    def _menu_clientes(self) -> None:
        cabecalho("GERENCIAR CLIENTES")
        print("  [1] Cadastrar cliente")
        print("  [2] Editar cliente")
        print("  [3] Buscar cliente por ID")
        print("  [4] Listar todos os clientes")
        print("  [5] Listar clientes ativos")
        print("  [0] Voltar")
        escolha = input("  Opcao: ").strip()
        if escolha == "1":
            self._cadastrar_cliente()
        elif escolha == "2":
            self._editar_cliente()
        elif escolha == "3":
            self._buscar_cliente()
        elif escolha == "4":
            self._listar_clientes()
        elif escolha == "5":
            self._listar_ativos()

    def _cadastrar_cliente(self) -> None:
        cabecalho("CADASTRAR CLIENTE")
        id = ler_input("  ID: ")
        nome = ler_input("  Nome: ")
        telefone = ler_input("  Telefone: ")
        print("  Prioridade: [1] normal  [2] prioritario")
        p = ler_input("  Escolha: ")
        prioridade = "prioritario" if p == "2" else "normal"
        ok, msg = self.cadastro.cadastrar_cliente(id, nome, telefone, prioridade)
        print(f"\n  {'✔' if ok else '✖'}  {msg if not ok else f'Cliente {id} cadastrado!'}")
        pausar()

    def _editar_cliente(self) -> None:
        cabecalho("EDITAR CLIENTE")
        id = ler_input("  ID do cliente: ")
        cliente = self.cadastro.buscar_cliente_por_id(id)
        if not cliente:
            print(f"  ✖  Cliente '{id}' nao encontrado.")
            pausar()
            return
        print(f"\n  Atual: {cliente.nome} | {cliente.telefone} | {cliente.prioridade}")
        nome = ler_input(f"  Novo nome [{cliente.nome}]: ", obrigatorio=False)
        telefone = ler_input(f"  Novo telefone [{cliente.telefone}]: ", obrigatorio=False)
        print("  Nova prioridade: [1] normal  [2] prioritario  [Enter] manter")
        p = ler_input("  Escolha: ", obrigatorio=False)
        prioridade = "prioritario" if p == "2" else ("normal" if p == "1" else None)
        ok, msg = self.cadastro.editar_cliente(id, nome or None, telefone or None, prioridade)
        print(f"\n  {'✔  Atualizado!' if ok else f'✖  {msg}'}")
        pausar()

    def _buscar_cliente(self) -> None:
        cabecalho("BUSCAR CLIENTE  [busca binaria O(log n)]")
        id = ler_input("  ID: ")
        cliente = self.cadastro.buscar_cliente_por_id(id)
        if cliente:
            print(f"\n  ✔  ID: {cliente.id} | Nome: {cliente.nome}")
            print(f"     Telefone: {cliente.telefone} | Prioridade: {cliente.prioridade}")
            print(f"     Ativo: {'sim' if cliente.ativo else 'nao'}")
        else:
            print(f"\n  ✖  Cliente '{id}' nao encontrado.")
        pausar()

    def _listar_clientes(self) -> None:
        cabecalho("TODOS OS CLIENTES  [ordenados por ID]")
        clientes = self.cadastro.listar_clientes()
        if not clientes:
            print("  Nenhum cliente cadastrado.")
        else:
            print(f"  {'ID':<12} {'NOME':<25} {'TELEFONE':<15} {'PRIOR.':<12} {'ATIVO'}")
            print("  " + "─" * 68)
            for c in clientes:
                print(f"  {c.id:<12} {c.nome[:25]:<25} {c.telefone:<15} {c.prioridade:<12} {'sim' if c.ativo else 'nao'}")
        pausar()

    def _listar_ativos(self) -> None:
        cabecalho("CLIENTES ATIVOS  [lista encadeada]")
        ativos = self.cadastro.listar_ativos()
        if not ativos:
            print("  Nenhum cliente ativo.")
        else:
            for c in ativos:
                print(f"  {c.id:<12} {c.nome}")
        pausar()

    def _menu_atendentes(self) -> None:
        cabecalho("GERENCIAR ATENDENTES")
        print("  [1] Cadastrar atendente")
        print("  [2] Listar atendentes")
        print("  [0] Voltar")
        escolha = input("  Opcao: ").strip()
        if escolha == "1":
            self._cadastrar_atendente()
        elif escolha == "2":
            self._listar_atendentes()

    def _cadastrar_atendente(self) -> None:
        cabecalho("CADASTRAR ATENDENTE")
        id = ler_input("  ID: ")
        nome = ler_input("  Nome: ")
        ok, msg = self.cadastro.cadastrar_atendente(id, nome)
        print(f"\n  {'✔  Atendente cadastrado!' if ok else f'✖  {msg}'}")
        pausar()

    def _listar_atendentes(self) -> None:
        cabecalho("ATENDENTES")
        atendentes = self.cadastro.listar_atendentes()
        if not atendentes:
            print("  Nenhum atendente cadastrado.")
        else:
            print(f"  {'ID':<12} {'NOME':<25} {'STATUS'}")
            print("  " + "─" * 50)
            for a in atendentes:
                status = f"atendendo {a.cliente_atual_id}" if not a.disponivel else "disponivel"
                print(f"  {a.id:<12} {a.nome[:25]:<25} {status}")
        pausar()

    def _abrir_atendimento(self) -> None:
        cabecalho("ABRIR ATENDIMENTO  (entrar na fila)")
        id = ler_input("  ID do cliente: ")
        cliente = self.cadastro.buscar_cliente_por_id(id)
        if not cliente:
            print(f"  ✖  Cliente '{id}' nao encontrado.")
            pausar()
            return
        if not cliente.ativo:
            print(f"  ✖  Cliente '{id}' esta inativo.")
            pausar()
            return
        if self.fila.esta_na_fila(id):
            print(f"  ✖  Cliente '{id}' ja esta na fila.")
            pausar()
            return
        self.fila.entrar_na_fila(cliente)
        repo.registrar_log(f"FILA cliente '{id}' prioridade '{cliente.prioridade}'")
        print(f"\n  ✔  {cliente.nome} entrou na fila {cliente.prioridade}.")
        t = self.fila.tamanho()
        print(f"     Fila: {t['prioritaria']} prioritarios | {t['comum']} comuns")
        pausar()

    def _chamar_proximo(self) -> None:
        cabecalho("CHAMAR PROXIMO")
        proximo = self.fila.proximo()
        if not proximo:
            print("  Fila vazia. Nenhum cliente aguardando.")
            pausar()
            return
        cliente, entrada = proximo
        atendentes = self.cadastro.listar_atendentes()
        disponiveis = [a for a in atendentes if a.disponivel]
        if not disponiveis:
            print("  Nenhum atendente disponivel no momento.")
            self.fila.entrar_na_fila(cliente)
            pausar()
            return
        print(f"\n  Proximo: {cliente.nome} ({cliente.prioridade})")
        print(f"\n  Atendentes disponiveis:")
        for i, a in enumerate(disponiveis, 1):
            print(f"    [{i}] {a.nome}")
        escolha = ler_input("\n  Escolha o atendente (numero): ")
        try:
            idx = int(escolha) - 1
            atendente = disponiveis[idx]
        except (ValueError, IndexError):
            print("  ✖  Escolha invalida. Cliente retornou a fila.")
            self.fila.entrar_na_fila(cliente)
            pausar()
            return
        ok, msg, atd = self.atendimento.iniciar(cliente, atendente, entrada)
        repo.salvar_atendentes(self.cadastro.atendentes)
        if ok:
            print(f"\n  ✔  {cliente.nome} sendo atendido por {atendente.nome}.")
        else:
            print(f"\n  ✖  {msg}")
            self.fila.entrar_na_fila(cliente)
        pausar()

    def _finalizar_atendimento(self) -> None:
        cabecalho("FINALIZAR ATENDIMENTO")
        atendentes = self.cadastro.listar_atendentes()
        ocupados = [a for a in atendentes if not a.disponivel]
        if not ocupados:
            print("  Nenhum atendente em atendimento.")
            pausar()
            return
        print("  Atendentes em atendimento:")
        for i, a in enumerate(ocupados, 1):
            print(f"    [{i}] {a.nome}  (cliente: {a.cliente_atual_id})")
        escolha = ler_input("\n  Escolha o atendente (numero): ")
        try:
            atendente = ocupados[int(escolha) - 1]
        except (ValueError, IndexError):
            print("  ✖  Escolha invalida.")
            pausar()
            return
        ok, msg, atd = self.atendimento.finalizar(atendente)
        repo.salvar_atendentes(self.cadastro.atendentes)
        if ok:
            print(f"\n  ✔  Atendimento finalizado. Duracao: {atd.duracao_segundos}s")
        else:
            print(f"\n  ✖  {msg}")
        pausar()

    def _desfazer_finalizacao(self) -> None:
        cabecalho("DESFAZER ULTIMA FINALIZACAO  [pilha]")
        id_atendente = ler_input("  ID do atendente: ")
        atendente = self.cadastro.buscar_atendente_por_id(id_atendente)
        if not atendente:
            print(f"  ✖  Atendente nao encontrado.")
            pausar()
            return
        ok, msg = self.atendimento.desfazer_ultima_finalizacao(atendente)
        repo.salvar_atendentes(self.cadastro.atendentes)
        print(f"\n  {'✔' if ok else '✖'}  {msg}")
        pausar()

    def _ver_historico_cliente(self) -> None:
        cabecalho("HISTORICO DO CLIENTE  [recursao]")
        id = ler_input("  ID do cliente: ")
        cliente = self.cadastro.buscar_cliente_por_id(id)
        if not cliente:
            print(f"  ✖  Cliente nao encontrado.")
            pausar()
            return
        historico = self.atendimento.historico_cliente(id)
        atendentes = {a.id: a.nome for a in self.cadastro.listar_atendentes()}
        print(f"\n  Historico de {cliente.nome} ({len(historico)} atendimento(s)):")
        if not historico:
            print("  Nenhum atendimento registrado.")
        else:
            print(f"\n  {'ID':<10} {'ATENDENTE':<20} {'INICIO':<20} {'DURACAO'}")
            print("  " + "─" * 60)
            for a in historico:
                dur = f"{a.duracao_segundos}s" if a.duracao_segundos else "em aberto"
                print(f"  {a.id:<10} {atendentes.get(a.atendente_id,'?')[:20]:<20} "
                      f"{a.inicio.strftime('%d/%m %H:%M'):<20} {dur}")
        pausar()

    def _remover_inativos(self) -> None:
        cabecalho("REMOVER CLIENTES INATIVOS  [lista encadeada]")
        em_aberto = self.atendimento.ids_clientes_em_aberto()
        removidos = self.cadastro.remover_inativos(em_aberto)
        if removidos:
            print(f"\n  ✔  {len(removidos)} cliente(s) marcado(s) como inativos: {removidos}")
        else:
            print("  Nenhum cliente inativo para remover.")
        pausar()

    def _menu_relatorios(self) -> None:
        cabecalho("RELATORIOS")
        print("  [1] Tempo medio de atendimento")
        print("  [2] Tempo medio por atendente")
        print("  [3] Top 5 clientes mais atendidos")
        print("  [4] Filtrar atendimentos por data")
        print("  [5] Exportar atendimentos CSV")
        print("  [6] Exportar clientes CSV")
        print("  [0] Voltar")
        escolha = input("  Opcao: ").strip()
        atendimentos = self.atendimento.todos()
        clientes = self.cadastro.listar_clientes()
        atendentes = self.cadastro.listar_atendentes()
        if escolha == "1":
            media = tempo_medio_atendimento(atendimentos)
            print(f"\n  Tempo medio: {media:.1f}s ({media/60:.1f} min)")
            pausar()
        elif escolha == "2":
            dados = tempo_medio_por_atendente(atendimentos, atendentes)
            print(f"\n  {'ATENDENTE':<20} {'TOTAL':>7} {'MEDIA (s)':>10}")
            print("  " + "─" * 40)
            for d in dados:
                print(f"  {d['nome'][:20]:<20} {d['total_atendimentos']:>7} {d['media_segundos']:>10.1f}")
            pausar()
        elif escolha == "3":
            top = top_clientes(atendimentos, clientes)
            print(f"\n  {'#':<4} {'CLIENTE':<20} {'TOTAL':>6}")
            print("  " + "─" * 32)
            for i, d in enumerate(top, 1):
                print(f"  {i:<4} {d['nome'][:20]:<20} {d['total']:>6}")
            pausar()
        elif escolha == "4":
            print("  Formato: AAAA-MM-DD")
            di = ler_data("  Data inicio: ")
            df = ler_data("  Data fim: ")
            if di and df:
                filtrados = filtrar_por_data(atendimentos, di, df)
                ordenados = atendimentos_ordenados_por_inicio(filtrados)
                print(f"\n  {len(ordenados)} atendimento(s) encontrado(s).")
                for a in ordenados:
                    print(f"  {a.id} | {a.cliente_id} | {a.inicio.strftime('%d/%m/%Y %H:%M')}")
            pausar()
        elif escolha == "5":
            caminho = exportar_csv_atendimentos(atendimentos, clientes, atendentes)
            print(f"\n  ✔  Exportado: {caminho}")
            pausar()
        elif escolha == "6":
            caminho = exportar_csv_clientes(clientes)
            print(f"\n  ✔  Exportado: {caminho}")
            pausar()

    def _sair(self) -> None:
        print("\n  Ate logo! 👋\n")
        sys.exit(0)