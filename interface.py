import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
import datetime
import sys
from banco_de_dados import criar_csv_vazio, salvar_registro_csv

class OrganizadorFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Organizador Financeiro")
        self.geometry("1280x720")
        self.caminho_arquivo_csv = ""

        # Dicionário dinâmico de categorias
        self.categorias_opcoes = {
            "Gasto": ["Alimentação", "Moradia (Aluguel/Parcela)", "Transporte", "Saúde", "Educação", "Lazer/Hobbies", "Assinaturas/Serviços", "Impostos/Taxas", "Outros Gastos"],
            "Ganho": ["Salário", "Freelance/Serviços", "Rendimento de Negócio", "Vendas", "Restituição/Cashback", "Outros Ganhos"],
            "Investimento": ["Tesouro Direto", "CDB / LCI / LCA", "Ações (B3)", "Fundos Imobiliários (FIIs)", "Criptomoedas", "Renda Passiva (Dividendos)", "Reserva de Emergência"]
        }

        # --- Telas ---
        self.frame_inicial = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inicial.pack(expand=True)

        self.label_boas_vindas = ctk.CTkLabel(self.frame_inicial, text="Selecione ou crie um arquivo CSV para começar.", font=("Arial", 14))
        self.label_boas_vindas.pack(pady=10)

        self.botao_selecionar = ctk.CTkButton(self.frame_inicial, text="📁 Selecionar Arquivo", command=self.selecionar_arquivo)
        self.botao_selecionar.pack(pady=10)

        self.botao_criar = ctk.CTkButton(self.frame_inicial, text="➕ Criar Novo CSV", fg_color="green", hover_color="darkgreen", command=self.criar_arquivo)
        self.botao_criar.pack(pady=10)

        self.botao_alterar_arquivo = ctk.CTkButton(self, text="⚙️ Alterar CSV", width=100, height=30, fg_color="gray", command=self.voltar_tela_inicial)
        
        self.frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.label_arquivo_ativo = ctk.CTkLabel(self.frame_principal, text="", text_color="gray")

        self.construir_formulario()


    def construir_formulario(self):
        """Constrói os campos de entrada de dados usando widgets nativos do CTK."""
        
        self.titulo_form = ctk.CTkLabel(self.frame_principal, text="Novo Lançamento", font=("Arial", 20, "bold"))
        self.titulo_form.pack(pady=(20, 15))

        # 1. Tipo
        self.var_tipo = ctk.StringVar(value="Gasto")
        self.seletor_tipo = ctk.CTkSegmentedButton(
            self.frame_principal, 
            values=["Gasto", "Ganho", "Investimento"],
            variable=self.var_tipo,
            command=self.atualizar_categorias
        )
        self.seletor_tipo.pack(pady=10, fill="x")

        # --- SELETOR DE DATA (D/M/Y) ---
        self.label_data = ctk.CTkLabel(self.frame_principal, text="Data do Lançamento:", font=("Arial", 12, "bold"))
        self.label_data.pack(anchor="w", pady=(10, 0))

        self.frame_data = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        self.frame_data.pack(pady=5, fill="x")

        hoje = datetime.date.today()
        
        # Dias (01 a 31) - Aumentei a largura e mudei a estratégia de foco
        self.combo_dia = ctk.CTkComboBox(self.frame_data, values=[f"{i:02d}" for i in range(1, 32)], width=80)
        self.combo_dia.set(f"{hoje.day:02d}")
        self.combo_dia.pack(side="left", padx=(0, 5))

        # Meses (01 a 12)
        self.combo_mes = ctk.CTkComboBox(self.frame_data, values=[f"{i:02d}" for i in range(1, 13)], width=80)
        self.combo_mes.set(f"{hoje.month:02d}")
        self.combo_mes.pack(side="left", padx=5)

        # Anos (2020 a 2030)
        anos = [str(a) for a in range(2020, 2031)]
        self.combo_ano = ctk.CTkComboBox(self.frame_data, values=anos, width=100)
        self.combo_ano.set(str(hoje.year))
        self.combo_ano.pack(side="left", padx=5)

        # --- VALOR ---
        self.label_valor = ctk.CTkLabel(self.frame_principal, text="Valor (R$):", font=("Arial", 12, "bold"))
        self.label_valor.pack(anchor="w", pady=(10, 0))
        
        self.entrada_valor = ctk.CTkEntry(self.frame_principal, placeholder_text="Ex: 150.50", height=35)
        self.entrada_valor.pack(pady=5, fill="x")

        # --- CATEGORIA ---
        self.label_categoria = ctk.CTkLabel(self.frame_principal, text="Categoria:", font=("Arial", 12, "bold"))
        self.label_categoria.pack(anchor="w", pady=(10, 0))

        self.dropdown_categoria = ctk.CTkComboBox(
            self.frame_principal, 
            values=self.categorias_opcoes["Gasto"],
            width=300,
            height=35
        )
        self.dropdown_categoria.pack(pady=5, fill="x")

        # --- BOTÃO SALVAR ---
        self.botao_salvar = ctk.CTkButton(
            self.frame_principal, 
            text="💾 Adicionar Registro", 
            height=45,
            font=("Arial", 14, "bold"),
            command=self.coletar_dados_formulario
        )
        self.botao_salvar.pack(pady=30, fill="x")


    def atualizar_categorias(self, tipo_selecionado):
        novas_categorias = self.categorias_opcoes[tipo_selecionado]
        self.dropdown_categoria.configure(values=novas_categorias)
        self.dropdown_categoria.set(novas_categorias[0])


    def coletar_dados_formulario(self):
        tipo = self.var_tipo.get()
        # Constrói a data a partir dos combos
        data = f"{self.combo_dia.get()}/{self.combo_mes.get()}/{self.combo_ano.get()}"
        categoria = self.dropdown_categoria.get()
        valor = self.entrada_valor.get()

        if not valor:
            messagebox.showerror("Erro", "Por favor, insira um valor.")
            return

        try:
            valor_limpo = valor.replace(",", ".")
            float(valor_limpo) # Valida se é um número
        except ValueError:
            messagebox.showerror("Erro", "Valor inválido. Use apenas números e ponto/vírgula.")
            return

        salvar_registro_csv(self.caminho_arquivo_csv, data, tipo, categoria, valor_limpo)
        
        self.entrada_valor.delete(0, 'end')
        messagebox.showinfo("Sucesso", "Registro adicionado com sucesso!")


    def selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o seu arquivo de finanças",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        if caminho:
            self.vincular_arquivo(caminho)

    def criar_arquivo(self):
        resposta = messagebox.askyesnocancel(
            "Local do Arquivo", 
            "Deseja criar o arquivo 'financas.csv' na mesma pasta do programa?\n\n[Sim] = Pasta Atual\n[Não] = Escolher outra pasta"
        )

        caminho_novo = ""
        if resposta is True: 
            diretorio_atual = os.path.dirname(os.path.abspath(__file__))
            caminho_novo = os.path.join(diretorio_atual, "financas.csv")
            if os.path.exists(caminho_novo):
                messagebox.showwarning("Aviso", "O arquivo 'financas.csv' já existe nesta pasta!")
                return
        elif resposta is False: 
            caminho_novo = filedialog.asksaveasfilename(
                title="Onde deseja salvar o novo arquivo?",
                defaultextension=".csv",
                initialfile="financas.csv",
                filetypes=[("Arquivos CSV", "*.csv")]
            )
            if not caminho_novo: return
        else:
            return

        criar_csv_vazio(caminho_novo)
        self.vincular_arquivo(caminho_novo)


    def vincular_arquivo(self, caminho):
        self.caminho_arquivo_csv = caminho
        self.frame_inicial.pack_forget()
        self.botao_alterar_arquivo.place(relx=0.98, rely=0.02, anchor="ne")
        self.frame_principal.pack(expand=True, fill="both", padx=40, pady=50)
        self.label_arquivo_ativo.configure(text=f"Arquivo Ativo: {os.path.basename(caminho)}")
        self.label_arquivo_ativo.pack(pady=10)


    def voltar_tela_inicial(self):
        self.caminho_arquivo_csv = ""
        self.frame_principal.pack_forget()
        self.botao_alterar_arquivo.place_forget()
        self.frame_inicial.pack(expand=True)
