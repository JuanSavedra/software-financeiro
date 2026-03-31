import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from banco_de_dados import criar_csv_vazio

class OrganizadorFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Organizador Financeiro")
        self.geometry("600x400")
        self.caminho_arquivo_csv = ""

        # ==========================================
        # TELA 1: Configuração Inicial (Centro)
        # ==========================================
        self.frame_inicial = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inicial.pack(expand=True) # expand=True centraliza o frame na tela

        self.label_boas_vindas = ctk.CTkLabel(self.frame_inicial, text="Selecione ou crie um arquivo CSV para começar.", font=("Arial", 14))
        self.label_boas_vindas.pack(pady=10)

        self.botao_selecionar = ctk.CTkButton(self.frame_inicial, text="📁 Selecionar Arquivo", command=self.selecionar_arquivo)
        self.botao_selecionar.pack(pady=10)

        # Novo botão verde para criar
        self.botao_criar = ctk.CTkButton(self.frame_inicial, text="➕ Criar Novo CSV", fg_color="green", hover_color="darkgreen", command=self.criar_arquivo)
        self.botao_criar.pack(pady=10)

        # ==========================================
        # ELEMENTOS DA TELA 2 (Pós-vínculo)
        # ==========================================
        
        # O botão superior direito (inicia invisível)
        self.botao_alterar_arquivo = ctk.CTkButton(self, text="⚙️ Alterar CSV", width=100, height=30, fg_color="gray", command=self.voltar_tela_inicial)
        
        # O Frame principal onde futuramente colocaremos os inputs de Gasto/Ganho
        self.frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.label_arquivo_ativo = ctk.CTkLabel(self.frame_principal, text="", text_color="gray")


    # --- Funções de Lógica da Interface ---

    def selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o seu arquivo de finanças",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        if caminho:
            self.vincular_arquivo(caminho)

    def criar_arquivo(self):
        # 1. Pergunta ao usuário o local desejado
        resposta = messagebox.askyesnocancel(
            "Local do Arquivo", 
            "Deseja criar o arquivo 'financas.csv' na mesma pasta do programa?\n\n[Sim] = Pasta Atual\n[Não] = Escolher outra pasta"
        )

        caminho_novo = ""

        if resposta is True: 
            # Usuário clicou em SIM (Pasta do projeto)
            diretorio_atual = os.path.dirname(os.path.abspath(__file__))
            caminho_novo = os.path.join(diretorio_atual, "financas.csv")
            
            # Trava de segurança para não apagar um arquivo existente
            if os.path.exists(caminho_novo):
                messagebox.showwarning("Aviso", "O arquivo 'financas.csv' já existe nesta pasta!")
                return
                
        elif resposta is False: 
            # Usuário clicou em NÃO (Quer escolher a pasta)
            caminho_novo = filedialog.asksaveasfilename(
                title="Onde deseja salvar o novo arquivo?",
                defaultextension=".csv",
                initialfile="financas.csv",
                filetypes=[("Arquivos CSV", "*.csv")]
            )
            # Se o usuário fechar a janela sem salvar
            if not caminho_novo: 
                return
        else:
            # Usuário clicou em Cancelar ou fechou a caixinha
            return

        # 2. Chama a função do banco de dados para gerar o arquivo físico
        criar_csv_vazio(caminho_novo)
        
        # 3. Vincula o arquivo recém-criado ao sistema
        self.vincular_arquivo(caminho_novo)


    def vincular_arquivo(self, caminho):
        """Muda a interface assim que um arquivo é vinculado com sucesso."""
        self.caminho_arquivo_csv = caminho
        
        # 1. Esconde o menu inicial central
        self.frame_inicial.pack_forget()
        
        # 2. Posiciona o botão de alterar no canto superior direito
        # relx=0.98 e rely=0.02 significa 98% para a direita e 2% para baixo
        self.botao_alterar_arquivo.place(relx=0.98, rely=0.02, anchor="ne")
        
        # 3. Exibe o Frame Principal
        self.frame_principal.pack(expand=True, fill="both", padx=20, pady=50)
        self.label_arquivo_ativo.configure(text=f"Arquivo Ativo:\n{caminho}")
        self.label_arquivo_ativo.pack(pady=10)


    def voltar_tela_inicial(self):
        """Desfaz o vínculo e volta para a tela de seleção."""
        self.caminho_arquivo_csv = ""
        
        # Esconde os elementos da tela principal
        self.frame_principal.pack_forget()
        self.botao_alterar_arquivo.place_forget()
        
        # Mostra o menu central novamente
        self.frame_inicial.pack(expand=True)