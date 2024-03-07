class Produto:
    def __init__(self, codigo, nome, preco):
        self.codigo = codigo
        self.nome = nome
        self.preco = preco

class Pedido:
    def __init__(self, numero, cliente):
        self.numero = numero
        self.cliente = cliente
        self.itens = []
        self.total = 0  # Adicione um atributo para armazenar o total do pedido

    def adicionar_item(self, produto, quantidade):
        self.itens.append((produto, quantidade))
        self.calcular_total()

    def calcular_total(self):
        self.total = sum(produto.preco * quantidade for produto, quantidade in self.itens)
        return self.total