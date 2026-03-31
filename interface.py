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

        # Configuração do Tema (Azul Padrão)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Dicionário de categorias
        self.categorias_opcoes = {
            "Gasto": ["Alimentação", "Moradia (Aluguel/Parcela)", "Transporte", "Saúde", "Educação", "Lazer/Hobbies", "Assinaturas/Serviços", "Impostos/Taxas", "Outros Gastos"],
            "Ganho": ["Salário", "Freelance/Serviços", "Rendimento de Negócio", "Vendas", "Restituição/Cashback", "Outros Ganhos"],
            "Investimento": ["Tesouro Direto", "CDB / LCI / LCA", "Ações (B3)", "Fundos Imobiliários (FIIs)", "Criptomoedas", "Renda Passiva (Dividendos)", "Reserva de Emergência"]
        }

        # --- TELA INICIAL ---
        self.frame_inicial = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inicial.pack(expand=True)

        self.label_boas_vindas = ctk.CTkLabel(self.frame_inicial, text="Selecione ou crie um arquivo CSV para começar.", font=("Arial", 16))
        self.label_boas_vindas.pack(pady=20)

        self.botao_selecionar = ctk.CTkButton(self.frame_inicial, text="📁 Selecionar Arquivo", command=self.selecionar_arquivo, height=40)
        self.botao_selecionar.pack(pady=10)

        self.botao_criar = ctk.CTkButton(self.frame_inicial, text="➕ Criar Novo CSV", fg_color="#28a745", hover_color="#218838", command=self.criar_arquivo, height=40)
        self.botao_criar.pack(pady=10)

        # --- NAVEGAÇÃO SUPERIOR ---
        self.frame_nav = ctk.CTkFrame(self, height=70)
        
        self.botao_seta_esq = ctk.CTkButton(self.frame_nav, text="◀ Lançamentos", width=160, height=40, command=lambda: self.mudar_tela(0))
        self.botao_seta_esq.pack(side="left", padx=20, pady=15)
        
        self.label_titulo_tela = ctk.CTkLabel(self.frame_nav, text="Lançamentos", font=("Arial", 20, "bold"))
        self.label_titulo_tela.pack(side="left", expand=True)

        self.botao_seta_dir = ctk.CTkButton(self.frame_nav, text="Visualização ▶", width=160, height=40, command=lambda: self.mudar_tela(1))
        self.botao_seta_dir.pack(side="right", padx=20, pady=15)

        # Botão Config no canto inferior
        self.botao_alterar_arquivo = ctk.CTkButton(self, text="⚙️ Config", width=100, height=35, fg_color="gray", command=self.voltar_tela_inicial)

        # --- TELA 1: FORMULÁRIO ---
        self.frame_insercao = ctk.CTkFrame(self, fg_color="transparent")
        self.construir_formulario()

        # --- TELA 2: VISUALIZAÇÃO ---
        self.frame_visualizacao = ctk.CTkFrame(self, fg_color="transparent")
        self.construir_visualizacao()


    def construir_formulario(self):
        self.titulo_form = ctk.CTkLabel(self.frame_insercao, text="Novo Lançamento", font=("Arial", 28, "bold"))
        self.titulo_form.pack(pady=(30, 20))

        self.var_tipo = ctk.StringVar(value="Gasto")
        self.seletor_tipo = ctk.CTkSegmentedButton(
            self.frame_insercao, values=["Gasto", "Ganho", "Investimento"],
            variable=self.var_tipo, command=self.atualizar_categorias, height=45
        )
        self.seletor_tipo.pack(pady=15, fill="x", padx=250)

        # Data
        self.label_data = ctk.CTkLabel(self.frame_insercao, text="Data:", font=("Arial", 14, "bold"))
        self.label_data.pack(anchor="w", pady=(20, 0), padx=250)
        self.frame_data = ctk.CTkFrame(self.frame_insercao, fg_color="transparent")
        self.frame_data.pack(pady=5, fill="x", padx=250)
        hoje = datetime.date.today()
        self.combo_dia = ctk.CTkComboBox(self.frame_data, values=[f"{i:02d}" for i in range(1, 32)], width=100)
        self.combo_dia.set(f"{hoje.day:02d}")
        self.combo_dia.pack(side="left", padx=(0, 10))
        self.combo_mes = ctk.CTkComboBox(self.frame_data, values=[f"{i:02d}" for i in range(1, 13)], width=100)
        self.combo_mes.set(f"{hoje.month:02d}")
        self.combo_mes.pack(side="left", padx=10)
        self.combo_ano = ctk.CTkComboBox(self.frame_data, values=[str(a) for a in range(2020, 2031)], width=120)
        self.combo_ano.set(str(hoje.year))
        self.combo_ano.pack(side="left", padx=10)

        # Valor
        self.label_valor = ctk.CTkLabel(self.frame_insercao, text="Valor (R$):", font=("Arial", 14, "bold"))
        self.label_valor.pack(anchor="w", pady=(20, 0), padx=250)
        self.entrada_valor = ctk.CTkEntry(self.frame_insercao, placeholder_text="0.00", height=45)
        self.entrada_valor.pack(pady=5, fill="x", padx=250)

        # Categoria
        self.label_categoria = ctk.CTkLabel(self.frame_insercao, text="Categoria:", font=("Arial", 14, "bold"))
        self.label_categoria.pack(anchor="w", pady=(20, 0), padx=250)
        self.dropdown_categoria = ctk.CTkComboBox(self.frame_insercao, values=self.categorias_opcoes["Gasto"], height=45)
        self.dropdown_categoria.pack(pady=5, fill="x", padx=250)

        # Botão Salvar
        self.botao_salvar = ctk.CTkButton(
            self.frame_insercao, text="💾 Adicionar Registro", height=55,
            font=("Arial", 18, "bold"), command=self.coletar_dados_formulario
        )
        self.botao_salvar.pack(pady=50, fill="x", padx=250)


    def construir_visualizacao(self):
        # Frame para conter Título e Filtro lado a lado
        self.header_vis_frame = ctk.CTkFrame(self.frame_visualizacao, fg_color="transparent")
        self.header_vis_frame.pack(pady=(30, 20))

        self.titulo_vis = ctk.CTkLabel(self.header_vis_frame, text="Histórico de Registros", font=("Arial", 28, "bold"))
        self.titulo_vis.pack(side="left", padx=20)

        self.botao_filtro = ctk.CTkButton(self.header_vis_frame, text="🔍 Filtros", width=120, height=40, command=lambda: None)
        self.botao_filtro.pack(side="left", padx=10)

        # Frame centralizador para a tabela
        self.container_tabela = ctk.CTkFrame(self.frame_visualizacao, fg_color="transparent")
        self.container_tabela.pack(expand=True, fill="both", padx=100, pady=10)

        self.tabela_frame = ctk.CTkScrollableFrame(self.container_tabela, height=450)
        self.tabela_frame.pack(expand=True, fill="both")
        
        self.tabela_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)


    def renderizar_cabecalho(self):
        # Usando azul oficial do CustomTkinter para o cabeçalho
        cor_azul_tema = ("#3B8ED0", "#1F6AA5")
        estilo_header = {"font": ("Arial", 13, "bold"), "height": 45, "text_color": "white", "fg_color": cor_azul_tema}
        
        ctk.CTkLabel(self.tabela_frame, text="DATA", **estilo_header).grid(row=0, column=0, padx=1, pady=(0, 2), sticky="nsew")
        ctk.CTkLabel(self.tabela_frame, text="TIPO", **estilo_header).grid(row=0, column=1, padx=1, pady=(0, 2), sticky="nsew")
        ctk.CTkLabel(self.tabela_frame, text="CATEGORIA", **estilo_header).grid(row=0, column=2, padx=1, pady=(0, 2), sticky="nsew")
        ctk.CTkLabel(self.tabela_frame, text="VALOR (R$)", **estilo_header).grid(row=0, column=3, padx=1, pady=(0, 2), sticky="nsew")


    def atualizar_tabela(self):
        for widget in self.tabela_frame.winfo_children():
            widget.destroy()

        self.renderizar_cabecalho()
        df = ler_registros_csv(self.caminho_arquivo_csv)
        
        for i, row in df.iterrows():
            # Cores dinâmicas para o Tipo
            cor_tipo = "#ff6b6b" if row['Tipo'] == "Gasto" else "#51cf66" if row['Tipo'] == "Ganho" else "#5c7cff"
            
            # Removido fg_color forçado das células para seguir o background do frame do tema
            estilo_celula = {"height": 40}
            
            ctk.CTkLabel(self.tabela_frame, text=row['Data'], **estilo_celula).grid(row=i+1, column=0, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=row['Tipo'].upper(), text_color=cor_tipo, font=("Arial", 11, "bold"), **estilo_celula).grid(row=i+1, column=1, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=row['Categoria'], anchor="center", **estilo_celula).grid(row=i+1, column=2, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=f"R$ {float(row['Valor']):,.2f}", anchor="center", font=("Arial", 12, "bold"), **estilo_celula).grid(row=i+1, column=3, padx=1, pady=1, sticky="nsew")


    def mudar_tela(self, indice):
        self.tela_atual = indice
        self.frame_insercao.pack_forget()
        self.frame_visualizacao.pack_forget()

        if indice == 0:
            self.label_titulo_tela.configure(text="Lançamentos")
            self.frame_insercao.pack(expand=True, fill="both")
            self.botao_seta_esq.configure(state="disabled")
            self.botao_seta_dir.configure(state="normal")
        else:
            self.label_titulo_tela.configure(text="Visualização de Dados")
            self.atualizar_tabela()
            self.frame_visualizacao.pack(expand=True, fill="both")
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
            v = float(valor)
            if v <= 0: raise ValueError
        except:
            messagebox.showerror("Erro", "Insira um valor numérico positivo!")
            return

        salvar_registro_csv(self.caminho_arquivo_csv, data, tipo, categoria, valor)
        self.entrada_valor.delete(0, 'end')
        messagebox.showinfo("Sucesso", "Registro salvo com sucesso!")


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
        self.botao_alterar_arquivo.place(relx=0.98, rely=0.98, anchor="se")
        self.mudar_tela(0)

    def voltar_tela_inicial(self):
        self.caminho_arquivo_csv = ""
        self.frame_nav.pack_forget()
        self.frame_insercao.pack_forget()
        self.frame_visualizacao.pack_forget()
        self.botao_alterar_arquivo.place_forget()
        self.frame_inicial.pack(expand=True)

if __name__ == "__main__":
    app = OrganizadorFinanceiro()
    app.mainloop()
