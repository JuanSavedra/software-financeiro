import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
import datetime
import sys
from banco_de_dados import criar_csv_vazio, salvar_registro_csv, ler_registros_csv

class OrganizadorFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Organizador Financeiro")
        self.geometry("1280x720")
        self.caminho_arquivo_csv = ""
        self.tela_atual = 0  # 0: Inserção, 1: Visualização

        # Dicionário de categorias
        self.categorias_opcoes = {
            "Gasto": ["Alimentação", "Moradia (Aluguel/Parcela)", "Transporte", "Saúde", "Educação", "Lazer/Hobbies", "Assinaturas/Serviços", "Impostos/Taxas", "Outros Gastos"],
            "Ganho": ["Salário", "Freelance/Serviços", "Rendimento de Negócio", "Vendas", "Restituição/Cashback", "Outros Ganhos"],
            "Investimento": ["Tesouro Direto", "CDB / LCI / LCA", "Ações (B3)", "Fundos Imobiliários (FIIs)", "Criptomoedas", "Renda Passiva (Dividendos)", "Reserva de Emergência"]
        }

        # --- TELA INICIAL (Seleção de Arquivo) ---
        self.frame_inicial = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inicial.pack(expand=True)

        self.label_boas_vindas = ctk.CTkLabel(self.frame_inicial, text="Selecione ou crie um arquivo CSV para começar.", font=("Arial", 14))
        self.label_boas_vindas.pack(pady=10)

        self.botao_selecionar = ctk.CTkButton(self.frame_inicial, text="📁 Selecionar Arquivo", command=self.selecionar_arquivo)
        self.botao_selecionar.pack(pady=10)

        self.botao_criar = ctk.CTkButton(self.frame_inicial, text="➕ Criar Novo CSV", fg_color="green", hover_color="darkgreen", command=self.criar_arquivo)
        self.botao_criar.pack(pady=10)

        # --- NAVEGAÇÃO SUPERIOR ---
        self.frame_nav = ctk.CTkFrame(self, height=60)
        self.botao_seta_esq = ctk.CTkButton(self.frame_nav, text="◀ Lançamentos", width=150, command=lambda: self.mudar_tela(0))
        self.botao_seta_esq.pack(side="left", padx=20, pady=10)
        
        self.label_titulo_tela = ctk.CTkLabel(self.frame_nav, text="Lançamentos", font=("Arial", 18, "bold"))
        self.label_titulo_tela.pack(side="left", expand=True)

        self.botao_seta_dir = ctk.CTkButton(self.frame_nav, text="Visualização ▶", width=150, command=lambda: self.mudar_tela(1))
        self.botao_seta_dir.pack(side="right", padx=20, pady=10)

        self.botao_alterar_arquivo = ctk.CTkButton(self, text="⚙️ Config", width=80, height=30, fg_color="gray", command=self.voltar_tela_inicial)

        # --- TELA 1: FORMULÁRIO DE INSERÇÃO ---
        self.frame_insercao = ctk.CTkFrame(self, fg_color="transparent")
        self.construir_formulario()

        # --- TELA 2: VISUALIZAÇÃO DE DADOS ---
        self.frame_visualizacao = ctk.CTkFrame(self, fg_color="transparent")
        self.construir_visualizacao()


    def construir_formulario(self):
        """Constrói o formulário de entrada."""
        self.titulo_form = ctk.CTkLabel(self.frame_insercao, text="Novo Lançamento", font=("Arial", 24, "bold"))
        self.titulo_form.pack(pady=(20, 15))

        # Tipo
        self.var_tipo = ctk.StringVar(value="Gasto")
        self.seletor_tipo = ctk.CTkSegmentedButton(
            self.frame_insercao, values=["Gasto", "Ganho", "Investimento"],
            variable=self.var_tipo, command=self.atualizar_categorias, height=40
        )
        self.seletor_tipo.pack(pady=10, fill="x", padx=100)

        # Data
        self.label_data = ctk.CTkLabel(self.frame_insercao, text="Data:", font=("Arial", 14, "bold"))
        self.label_data.pack(anchor="w", pady=(20, 0), padx=100)
        self.frame_data = ctk.CTkFrame(self.frame_insercao, fg_color="transparent")
        self.frame_data.pack(pady=5, fill="x", padx=100)
        hoje = datetime.date.today()
        self.combo_dia = ctk.CTkComboBox(self.frame_data, values=[f"{i:02d}" for i in range(1, 32)], width=90)
        self.combo_dia.set(f"{hoje.day:02d}")
        self.combo_dia.pack(side="left", padx=(0, 10))
        self.combo_mes = ctk.CTkComboBox(self.frame_data, values=[f"{i:02d}" for i in range(1, 13)], width=90)
        self.combo_mes.set(f"{hoje.month:02d}")
        self.combo_mes.pack(side="left", padx=10)
        self.combo_ano = ctk.CTkComboBox(self.frame_data, values=[str(a) for a in range(2020, 2031)], width=110)
        self.combo_ano.set(str(hoje.year))
        self.combo_ano.pack(side="left", padx=10)

        # Valor
        self.label_valor = ctk.CTkLabel(self.frame_insercao, text="Valor (R$):", font=("Arial", 14, "bold"))
        self.label_valor.pack(anchor="w", pady=(20, 0), padx=100)
        self.entrada_valor = ctk.CTkEntry(self.frame_insercao, placeholder_text="0.00", height=40)
        self.entrada_valor.pack(pady=5, fill="x", padx=100)

        # Categoria
        self.label_categoria = ctk.CTkLabel(self.frame_insercao, text="Categoria:", font=("Arial", 14, "bold"))
        self.label_categoria.pack(anchor="w", pady=(20, 0), padx=100)
        self.dropdown_categoria = ctk.CTkComboBox(self.frame_insercao, values=self.categorias_opcoes["Gasto"], height=40)
        self.dropdown_categoria.pack(pady=5, fill="x", padx=100)

        # Botão Salvar
        self.botao_salvar = ctk.CTkButton(
            self.frame_insercao, text="💾 Adicionar Registro", height=50,
            font=("Arial", 16, "bold"), command=self.coletar_dados_formulario
        )
        self.botao_salvar.pack(pady=40, fill="x", padx=100)


    def construir_visualizacao(self):
        """Constrói a tela de listagem de dados."""
        self.titulo_vis = ctk.CTkLabel(self.frame_visualizacao, text="Histórico de Registros", font=("Arial", 24, "bold"))
        self.titulo_vis.pack(pady=(20, 10))

        # Frame com scroll para a tabela
        self.tabela_frame = ctk.CTkScrollableFrame(self.frame_visualizacao, width=1000, height=450)
        self.tabela_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Cabeçalhos da Tabela
        self.renderizar_cabecalho()


    def renderizar_cabecalho(self):
        header_bg = "#2b2b2b"
        self.head_data = ctk.CTkLabel(self.tabela_frame, text="DATA", font=("Arial", 12, "bold"), width=150, fg_color=header_bg)
        self.head_tipo = ctk.CTkLabel(self.tabela_frame, text="TIPO", font=("Arial", 12, "bold"), width=150, fg_color=header_bg)
        self.head_cat = ctk.CTkLabel(self.tabela_frame, text="CATEGORIA", font=("Arial", 12, "bold"), width=300, fg_color=header_bg)
        self.head_val = ctk.CTkLabel(self.tabela_frame, text="VALOR (R$)", font=("Arial", 12, "bold"), width=150, fg_color=header_bg)
        
        self.head_data.grid(row=0, column=0, padx=2, pady=5, sticky="nsew")
        self.head_tipo.grid(row=0, column=1, padx=2, pady=5, sticky="nsew")
        self.head_cat.grid(row=0, column=2, padx=2, pady=5, sticky="nsew")
        self.head_val.grid(row=0, column=3, padx=2, pady=5, sticky="nsew")


    def atualizar_tabela(self):
        """Lê o CSV e atualiza as linhas da visualização."""
        # Limpa as linhas anteriores (exceto cabeçalho)
        for widget in self.tabela_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        df = ler_registros_csv(self.caminho_arquivo_csv)
        
        for i, row in df.iterrows():
            # Alterna cores das linhas para facilitar leitura
            bg_color = "#333333" if i % 2 == 0 else "#242424"
            
            # Formatação de cores para o Tipo
            cor_tipo = "#ff4b4b" if row['Tipo'] == "Gasto" else "#4bff4b" if row['Tipo'] == "Ganho" else "#4b99ff"
            
            ctk.CTkLabel(self.tabela_frame, text=row['Data'], width=150, fg_color=bg_color).grid(row=i+1, column=0, padx=1, pady=1)
            ctk.CTkLabel(self.tabela_frame, text=row['Tipo'], width=150, fg_color=bg_color, text_color=cor_tipo).grid(row=i+1, column=1, padx=1, pady=1)
            ctk.CTkLabel(self.tabela_frame, text=row['Categoria'], width=300, fg_color=bg_color, anchor="w", padx=10).grid(row=i+1, column=2, padx=1, pady=1)
            ctk.CTkLabel(self.tabela_frame, text=f"{float(row['Valor']):.2f}", width=150, fg_color=bg_color, anchor="e", padx=10).grid(row=i+1, column=3, padx=1, pady=1)


    def mudar_tela(self, indice):
        self.tela_atual = indice
        
        # Esconde ambas as telas
        self.frame_insercao.pack_forget()
        self.frame_visualizacao.pack_forget()

        if indice == 0:
            self.label_titulo_tela.configure(text="Lançamentos")
            self.frame_insercao.pack(expand=True, fill="both", padx=50, pady=20)
            self.botao_seta_esq.configure(state="disabled")
            self.botao_seta_dir.configure(state="normal")
        else:
            self.label_titulo_tela.configure(text="Visualização de Dados")
            self.atualizar_tabela() # Atualiza antes de mostrar
            self.frame_visualizacao.pack(expand=True, fill="both", padx=50, pady=20)
            self.botao_seta_esq.configure(state="normal")
            self.botao_seta_dir.configure(state="disabled")


    def atualizar_categorias(self, tipo_selecionado):
        novas = self.categorias_opcoes[tipo_selecionado]
        self.dropdown_categoria.configure(values=novas)
        self.dropdown_categoria.set(novas[0])


    def coletar_dados_formulario(self):
        tipo = self.var_tipo.get()
        data = f"{self.combo_dia.get()}/{self.combo_mes.get()}/{self.combo_ano.get()}"
        categoria = self.dropdown_categoria.get()
        valor = self.entrada_valor.get().replace(",", ".")

        try:
            float(valor)
        except:
            messagebox.showerror("Erro", "Valor inválido!")
            return

        salvar_registro_csv(self.caminho_arquivo_csv, data, tipo, categoria, valor)
        self.entrada_valor.delete(0, 'end')
        messagebox.showinfo("Sucesso", "Registro salvo!")


    def selecionar_arquivo(self):
        c = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if c: self.vincular_arquivo(c)

    def criar_arquivo(self):
        c = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="financas.csv")
        if c:
            criar_csv_vazio(c)
            self.vincular_arquivo(c)

    def vincular_arquivo(self, caminho):
        self.caminho_arquivo_csv = caminho
        self.frame_inicial.pack_forget()
        self.frame_nav.pack(fill="x", side="top")
        self.botao_alterar_arquivo.place(relx=0.98, rely=0.02, anchor="ne")
        self.mudar_tela(0)

    def voltar_tela_inicial(self):
        self.caminho_arquivo_csv = ""
        self.frame_nav.pack_forget()
        self.frame_insercao.pack_forget()
        self.frame_visualizacao.pack_forget()
        self.botao_alterar_arquivo.place_forget()
        self.frame_inicial.pack(expand=True)
