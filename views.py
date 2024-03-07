import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models import Produto, Pedido

class TkinterView:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Sistema de Vendas de Bolo de Pote")

        # Configuração do estilo para botões
        style = ttk.Style()
        style.configure('TButton', padding=10, font=('Arial', 24), background='#FFC0CB', foreground='pink')
        style.map('TButton', background=[('active', '#fca8ff')])

        self.menu_frame = tk.Frame(self.root)
        self.produtos_frame = tk.Frame(self.root)
        self.pedidos_frame = tk.Frame(self.root)

        self.mostrar_menu()

    def mostrar_menu(self):
        self.limpar_frames()
        tk.Label(self.menu_frame, text="Bolos de Pote da Sabrina:", font=('Arial', 36)).pack()
        ttk.Button(self.menu_frame, text="Adicionar Bolo", command=self.adicionar_produto).pack(pady=10)
        ttk.Button(self.menu_frame, text="Listar Bolos", command=self.listar_produtos).pack(pady=10)
        ttk.Button(self.menu_frame, text="Criar Pedido", command=self.criar_pedido).pack(pady=10)
        ttk.Button(self.menu_frame, text="Listar Pedidos", command=self.listar_pedidos).pack(pady=10)
        ttk.Button(self.menu_frame, text="Sair", command=self.root.destroy).pack(pady=10)

        self.menu_frame.pack()

    def adicionar_produto(self):
        self.limpar_frames()
        tk.Label(self.produtos_frame, text="Código do Produto:", font=('Arial', 14)).pack()
        codigo_entry = tk.Entry(self.produtos_frame, font=('Arial', 12))
        codigo_entry.pack(pady=5)
        tk.Label(self.produtos_frame, text="Nome do Bolo:", font=('Arial', 14)).pack()
        nome_entry = tk.Entry(self.produtos_frame, font=('Arial', 12))
        nome_entry.pack(pady=5)
        tk.Label(self.produtos_frame, text="Preço do Bolo:", font=('Arial', 14)).pack()
        preco_entry = tk.Entry(self.produtos_frame, font=('Arial', 12))
        preco_entry.pack(pady=5)
        ttk.Button(self.produtos_frame, text="Salvar", command=lambda: self.salvar_produto(codigo_entry.get(), nome_entry.get(), preco_entry.get())).pack(pady=10)
        ttk.Button(self.produtos_frame, text="Voltar", command=self.mostrar_menu).pack(pady=10)

        self.produtos_frame.pack()

    def salvar_produto(self, codigo, nome, preco):
        try:
            produto = Produto(codigo, nome, float(preco))
            self.controller.adicionar_produto(produto)
            messagebox.showinfo("Sucesso", "Bolo adicionado com sucesso!")
            self.mostrar_menu()
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um preço válido.")

    def escolher_produtos(self, numero_entry):
        numero_pedido = numero_entry.get()
        produtos_escolhidos = self.controller.escolher_produtos(numero_pedido)

        if produtos_escolhidos:
            messagebox.showinfo("Bolos Escolhidos", "Bolos adicionados ao pedido!")
            self.controller.adicionar_produtos_a_pedido(numero_pedido, "Cliente Padrão", produtos_escolhidos)
        else:
            messagebox.showwarning("Aviso", "Nenhum bolo escolhido.")

    def criar_pedido(self):
        self.limpar_frames()
        tk.Label(self.pedidos_frame, text="Número do Pedido:", font=('Arial', 14)).pack()
        numero_entry = tk.Entry(self.pedidos_frame, font=('Arial', 12))
        numero_entry.pack(pady=5)
        tk.Label(self.pedidos_frame, text="Nome do Cliente:", font=('Arial', 14)).pack()
        cliente_entry = tk.Entry(self.pedidos_frame, font=('Arial', 12))
        cliente_entry.pack(pady=5)

        ttk.Button(self.pedidos_frame, text="Escolher Bolos", command=lambda: self.escolher_produtos(numero_entry)).pack(pady=10)
        ttk.Button(self.pedidos_frame, text="Salvar", command=lambda: self.controller.criar_pedido(numero_entry.get(), cliente_entry.get())).pack(pady=10)
        ttk.Button(self.pedidos_frame, text="Voltar", command=self.mostrar_menu).pack(pady=10)

        self.pedidos_frame.pack()

    def listar_produtos(self):
        self.limpar_frames()
        tk.Label(self.produtos_frame, text="Lista de Bolos:", font=('Arial', 16)).pack()
        produtos = self.controller.listar_produtos()
        for produto in produtos:
            tk.Label(self.produtos_frame, text=f"{produto.codigo}: {produto.nome} - R${produto.preco:.2f}", font=('Arial', 12)).pack()
            ttk.Button(self.produtos_frame, text="Adicionar ao Pedido", command=lambda p=produto: self.adicionar_produto_pedido(p)).pack(pady=5)
            ttk.Button(self.produtos_frame, text="Remover", command=lambda p=produto: self.remover_produto(p)).pack(pady=5)
        ttk.Button(self.produtos_frame, text="Voltar", command=self.mostrar_menu).pack(pady=10)

        self.produtos_frame.pack()

    def remover_produto(self, produto):
        resposta = messagebox.askyesno("Remover Bolo", f"Tem certeza que deseja remover o bolo {produto.numero}?")
        if resposta:
            self.controller.remover_produto(produto)
            self.listar_produtos()

    def adicionar_produto_pedido(self, produto):
        quantidade = simpledialog.askinteger("Quantidade", f"Quantidade para {produto.nome}:")
        if quantidade is not None and quantidade > 0:
            self.controller.adicionar_item_pedido(produto, quantidade)
            messagebox.showinfo("Sucesso", f"{quantidade} {produto.nome}(s) adicionado(s) ao pedido!")

    def listar_pedidos(self):
        self.limpar_frames()
        tk.Label(self.pedidos_frame, text="Lista de Pedidos:", font=('Arial', 16)).pack()
        pedidos = self.controller.listar_pedidos()
        for pedido in pedidos:
            detalhes_pedido = f"Pedido {pedido.numero} - Cliente: {pedido.cliente} - Total: R${pedido.calcular_total():.2f}\n"

            # Adiciona detalhes dos produtos ao texto do pedido
            detalhes_pedido += "Bolos:"
            for produto, quantidade in pedido.itens:
                detalhes_pedido += f"\n- {produto.nome} (Quantidade: {quantidade}) - R${produto.preco:.2f} cada"

            tk.Label(self.pedidos_frame, text=detalhes_pedido, font=('Arial', 12)).pack()
            ttk.Button(self.pedidos_frame, text="Remover", command=lambda p=pedido: self.remover_pedido(p)).pack(pady=5)

        ttk.Button(self.pedidos_frame, text="Voltar", command=self.mostrar_menu).pack(pady=10)

        self.pedidos_frame.pack()

    def remover_pedido(self, pedido):
        resposta = messagebox.askyesno("Remover Pedido", f"Tem certeza que deseja remover o pedido {pedido.numero}?")
        if resposta:
            self.controller.remover_pedido(pedido)
            self.listar_pedidos()        

    def limpar_frames(self):
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        for widget in self.produtos_frame.winfo_children():
            widget.destroy()

        for widget in self.pedidos_frame.winfo_children():
            widget.destroy()

        self.menu_frame.pack_forget()
        self.produtos_frame.pack_forget()
        self.pedidos_frame.pack_forget()

    def iniciar(self):
        self.root.mainloop()
