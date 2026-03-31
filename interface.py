import customtkinter as ctk
from tkinter import filedialog

class OrganizadorFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__() # Inicializa a janela base

        # Configurações da Janela
        self.title("Organizador Financeiro")
        self.geometry("600x400")
        
        # Variável para guardar o caminho do arquivo
        self.caminho_arquivo_csv = ""

        # --- Criação dos Elementos Visuais ---
        self.botao_selecionar = ctk.CTkButton(
            self, 
            text="📁 Selecionar Arquivo CSV", 
            command=self.selecionar_arquivo
        )
        self.botao_selecionar.pack(pady=20)

        self.label_arquivo = ctk.CTkLabel(
            self, 
            text="Nenhum arquivo selecionado.",
            text_color="gray"
        )
        self.label_arquivo.pack(pady=10)

    # --- Funções de Interação da Interface ---
    def selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o seu arquivo de finanças",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
        )
        
        if caminho:
            self.caminho_arquivo_csv = caminho
            self.label_arquivo.configure(text=f"Arquivo carregado:\n{caminho}")
            # Futuramente: passaremos esse caminho para o banco_de_dados.py