from models import Produto, Pedido
from views import TkinterView
from tkinter import messagebox, simpledialog
import mysql.connector


class VendasController:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='root',
            database='BOLO_DE_POTE'
        )
        self.cursor = self.connection.cursor()
        self.view = TkinterView(self)
        self.produtos = []
        self.pedidos = []
        self.pedido_atual = None

    def executar_query(self, query, values=None):
        self.cursor.execute(query, values)
        self.connection.commit()

    def adicionar_produto(self, produto):
        query = "INSERT INTO produtos (codigo, nome, preco) VALUES (%s, %s, %s)"
        values = (produto.codigo, produto.nome, produto.preco)
        self.executar_query(query, values)

    def listar_produtos(self):
        query = "SELECT * FROM produtos"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.produtos = [Produto(codigo=row[0], nome=row[1], preco=row[2]) for row in result]
        return self.produtos

    def iniciar_pedido(self, numero_pedido, cliente):
        try:
            pedido = Pedido(numero_pedido, cliente)
            self.pedido_atual = pedido
            self.criar_pedido(pedido.numero, pedido.cliente)
            messagebox.showinfo("Sucesso", f"Pedido {numero_pedido} criado com sucesso!")
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um número de pedido válido.")

    def escolher_produtos(self, numero_pedido):
        # Inicia um novo pedido se não houver um pedido atual
        if not self.pedido_atual:
            numero_pedido = simpledialog.askinteger("Número do Pedido", "Digite o número do pedido:")
            if numero_pedido is not None and numero_pedido > 0:
                cliente = simpledialog.askstring("Nome do Cliente", "Digite o nome do cliente:")
                if cliente:
                    self.iniciar_pedido(numero_pedido, cliente)
                else:
                    messagebox.showwarning("Aviso", "Nome do cliente não inserido.")
                    return
            else:
                messagebox.showwarning("Aviso", "Número do pedido não inserido ou inválido.")
                return

        produtos = self.listar_produtos()
        produtos_escolhidos = []

        for produto in produtos:
            quantidade = simpledialog.askinteger("Quantidade", f"Quantidade para {produto.nome}:")
            if quantidade is not None and quantidade > 0:
                produtos_escolhidos.append((produto, quantidade))

        if produtos_escolhidos:
            messagebox.showinfo("Produtos Escolhidos", "Produtos adicionados ao pedido!")
            self.adicionar_produtos_a_pedido(self.pedido_atual.numero, "Cliente Padrão", produtos_escolhidos)
        else:
            messagebox.showwarning("Aviso", "Nenhum produto escolhido.")

        return produtos_escolhidos

    def adicionar_produtos_a_pedido(self, numero_pedido, cliente, produtos_escolhidos):
        try:
            if not self.pedido_existe(numero_pedido):
                messagebox.showerror("Erro", "O pedido não existe. Crie um pedido antes de adicionar produtos.")
                return

            for produto, quantidade in produtos_escolhidos:
                self.pedido_atual.adicionar_item(produto, quantidade)

                # Adiciona os itens do pedido ao banco de dados
                for _ in range(quantidade):
                    self.adicionar_item_pedido_banco(numero_pedido, produto.codigo, 1)

            # Recalcula o total do pedido após adicionar os itens
            self.pedido_atual.calcular_total()

            messagebox.showinfo("Sucesso", f"Produtos adicionados ao Pedido {numero_pedido} com sucesso!\nTotal: R${self.pedido_atual.calcular_total():.2f}")
            self.view.mostrar_menu()
        except ValueError:
            messagebox.showerror("Erro", "Erro ao adicionar produtos ao pedido.")

    def adicionar_item_pedido_banco(self, numero_pedido, codigo_produto, quantidade):
        query = "INSERT INTO produtos_em_pedidos (numero_pedido, codigo_produto, quantidade) VALUES (%s, %s, %s)"
        values = (numero_pedido, codigo_produto, quantidade)
        try:
            self.executar_query(query, values)
        except mysql.connector.IntegrityError:
            messagebox.showerror("Erro", "Produto já adicionado a este pedido.")

    def listar_pedidos(self):
        query = "SELECT * FROM pedidos"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.pedidos = []

        for row in result:
            numero_pedido = row[0]
            cliente = row[1]

            # Obtém os itens do pedido
            query_itens = "SELECT p.codigo, p.nome, pep.quantidade, p.preco " \
                           "FROM produtos_em_pedidos pep " \
                           "JOIN produtos p ON pep.codigo_produto = p.codigo " \
                           "WHERE pep.numero_pedido = %s"
            values_itens = (numero_pedido,)
            self.cursor.execute(query_itens, values_itens)
            result_itens = self.cursor.fetchall()

            itens_pedido = [(Produto(codigo=row[0], nome=row[1], preco=row[3]), row[2]) for row in result_itens]

            # Cria o objeto Pedido com os itens
            pedido = Pedido(numero_pedido, cliente)
            pedido.itens = itens_pedido
            self.pedidos.append(pedido)

        return self.pedidos

    def adicionar_item_pedido(self, produto, quantidade):
        if not self.pedido_atual:
            messagebox.showerror("Erro", "Por favor, crie um pedido antes de adicionar itens.")
            return

        self.pedido_atual.adicionar_item(produto, quantidade)

    def atualizar_cliente_pedido(self, numero_pedido, cliente):
        query = "UPDATE pedidos SET cliente = %s WHERE numero = %s"
        values = (cliente, numero_pedido)
        self.executar_query(query, values)

    def pedido_existe(self, numero_pedido):
        query = "SELECT COUNT(*) FROM pedidos WHERE numero = %s"
        values = (numero_pedido,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return result[0] > 0

    def criar_pedido(self, numero_pedido, cliente):
        try:
            # Cria um pedido no banco de dados
            query = "INSERT INTO pedidos (numero, cliente) VALUES (%s, %s)"
            values = (numero_pedido, cliente)
            self.executar_query(query, values)

            # Atualiza o pedido atual
            self.pedido_atual = Pedido(numero_pedido, cliente)

            # Exibe mensagem de sucesso
            messagebox.showinfo("Sucesso", f"Pedido {numero_pedido} criado com sucesso!")
            self.view.mostrar_menu()

        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um número de pedido válido.")

    def remover_produto(self, produto):
        query = "DELETE FROM produtos WHERE codigo = %s"
        values = (produto.codigo,)
        self.executar_query(query, values)
        self.produtos = [p for p in self.produtos if p.codigo != produto.codigo]

    def remover_pedido(self, pedido):
        query = "DELETE FROM pedidos WHERE numero = %s"
        values = (pedido.numero,)
        self.executar_query(query, values)
        self.pedidos = [p for p in self.pedidos if p.numero != pedido.numero]

    def salvar_pedido(self, numero, cliente):
        try:
            pedido = Pedido(numero, cliente)
            self.pedido_atual = pedido
            self.criar_pedido(pedido.numero, pedido.cliente)
            messagebox.showinfo("Sucesso", f"Pedido {numero} criado com sucesso!")
            self.view.mostrar_menu()
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um número de pedido válido.")

    def iniciar(self):
        self.view.iniciar()

if __name__ == "__main__":
    controller = VendasController()
    controller.iniciar()
