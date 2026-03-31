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
        
        # Configuração do Tema
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Dicionário de categorias
        self.categorias_opcoes = {
            "Gasto": ["Alimentação", "Moradia (Aluguel/Parcela)", "Transporte", "Saúde", "Educação", "Lazer/Hobbies", "Assinaturas/Serviços", "Impostos/Taxas", "Outros Gastos"],
            "Ganho": ["Salário", "Freelance/Serviços", "Rendimento de Negócio", "Vendas", "Restituição/Cashback", "Outros Ganhos"],
            "Investimento": ["Tesouro Direto", "CDB / LCI / LCA", "Ações (B3)", "Fundos Imobiliários (FIIs)", "Criptomoedas", "Renda Passiva (Dividendos)", "Reserva de Emergência"]
        }

        # --- TELA INICIAL (Seleção de Arquivo) ---
        self.frame_inicial = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inicial.pack(expand=True)

        self.label_boas_vindas = ctk.CTkLabel(self.frame_inicial, text="Selecione ou crie um arquivo CSV para começar.", font=("Arial", 16))
        self.label_boas_vindas.pack(pady=20)

        self.botao_selecionar_init = ctk.CTkButton(self.frame_inicial, text="📁 Selecionar Arquivo", command=self.selecionar_arquivo, height=40)
        self.botao_selecionar_init.pack(pady=10)

        self.botao_criar_init = ctk.CTkButton(self.frame_inicial, text="➕ Criar Novo CSV", fg_color="#28a745", hover_color="#218838", command=self.criar_arquivo, height=40)
        self.botao_criar_init.pack(pady=10)

        # --- ESTRUTURA PRINCIPAL (SIDEBAR + CONTEÚDO) ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. SIDEBAR
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        
        self.label_logo = ctk.CTkLabel(self.sidebar_frame, text="Organizador Financeiro", font=("Arial", 20, "bold"))
        self.label_logo.pack(pady=(30, 30))

        # Botões da Sidebar
        self.btn_lancamentos = self.criar_botao_sidebar("📝 Lançamentos", lambda: self.mudar_tela("lancamentos"))
        self.btn_visualizacao = self.criar_botao_sidebar("📊 Visualização", lambda: self.mudar_tela("visualizacao"))
        self.btn_graficos = self.criar_botao_sidebar("📈 Gráficos", lambda: self.mudar_tela("graficos"))
        self.btn_comparativo = self.criar_botao_sidebar("⚖️ Comparativo", lambda: self.mudar_tela("comparativo"))

        # Botão Configurações no rodapé da Sidebar
        self.btn_config = ctk.CTkButton(self.sidebar_frame, text="⚙️ Configurações", fg_color="transparent", 
                                        border_width=1, command=self.voltar_tela_inicial)
        self.btn_config.pack(side="bottom", pady=20, padx=20, fill="x")

        # 2. ÁREA DE CONTEÚDO
        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
        
        # Frames das Telas
        self.telas = {
            "lancamentos": ctk.CTkFrame(self.container_principal, fg_color="transparent"),
            "visualizacao": ctk.CTkFrame(self.container_principal, fg_color="transparent"),
            "graficos": ctk.CTkFrame(self.container_principal, fg_color="transparent"),
            "comparativo": ctk.CTkFrame(self.container_principal, fg_color="transparent")
        }

        self.construir_formulario()
        self.construir_visualizacao()
        self.construir_telas_vazias()


    def criar_botao_sidebar(self, texto, comando):
        btn = ctk.CTkButton(self.sidebar_frame, text=texto, anchor="w", height=45, 
                            fg_color="transparent", hover_color=("gray70", "gray30"), 
                            text_color=("gray10", "gray90"), command=comando)
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    def construir_telas_vazias(self):
        """Cria labels para as telas que ainda não possuem conteúdo."""
        for nome in ["graficos", "comparativo"]:
            label = ctk.CTkLabel(self.telas[nome], text=f"Tela de {nome.capitalize()}\n(Em desenvolvimento)", 
                                 font=("Arial", 24, "bold"), text_color="gray")
            label.pack(expand=True)

    def construir_formulario(self):
        frame = self.telas["lancamentos"]
        ctk.CTkLabel(frame, text="Novo Lançamento", font=("Arial", 28, "bold")).pack(pady=(30, 20))

        self.var_tipo = ctk.StringVar(value="Gasto")
        self.seletor_tipo = ctk.CTkSegmentedButton(frame, values=["Gasto", "Ganho", "Investimento"],
                                                  variable=self.var_tipo, command=self.atualizar_categorias, height=45)
        self.seletor_tipo.pack(pady=15, fill="x", padx=200)

        # Campos
        self.label_data = ctk.CTkLabel(frame, text="Data:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 0), padx=200)
        self.frame_data = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_data.pack(pady=5, fill="x", padx=200)
        hoje = datetime.date.today()
        self.combo_dia = ctk.CTkComboBox(self.frame_data, values=[f"{i:02d}" for i in range(1, 32)], width=100)
        self.combo_dia.set(f"{hoje.day:02d}"); self.combo_dia.pack(side="left", padx=(0, 10))
        self.combo_mes = ctk.CTkComboBox(self.frame_data, values=[f"{i:02d}" for i in range(1, 13)], width=100)
        self.combo_mes.set(f"{hoje.month:02d}"); self.combo_mes.pack(side="left", padx=10)
        self.combo_ano = ctk.CTkComboBox(self.frame_data, values=[str(a) for a in range(2020, 2031)], width=120)
        self.combo_ano.set(str(hoje.year)); self.combo_ano.pack(side="left", padx=10)

        ctk.CTkLabel(frame, text="Valor (R$):", font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 0), padx=200)
        self.entrada_valor = ctk.CTkEntry(frame, placeholder_text="0.00", height=45)
        self.entrada_valor.pack(pady=5, fill="x", padx=200)

        ctk.CTkLabel(frame, text="Categoria:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 0), padx=200)
        self.dropdown_categoria = ctk.CTkComboBox(frame, values=self.categorias_opcoes["Gasto"], height=45)
        self.dropdown_categoria.pack(pady=5, fill="x", padx=200)

        self.botao_salvar = ctk.CTkButton(frame, text="💾 Adicionar Registro", height=55, font=("Arial", 18, "bold"), command=self.coletar_dados_formulario)
        self.botao_salvar.pack(pady=50, fill="x", padx=200)


    def construir_visualizacao(self):
        frame = self.telas["visualizacao"]
        
        # Header com Título e Filtro
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(pady=(30, 20), fill="x", padx=100)
        
        ctk.CTkLabel(header_frame, text="Histórico de Registros", font=("Arial", 28, "bold")).pack(side="left")
        self.botao_filtro = ctk.CTkButton(header_frame, text="🔍 Filtros", width=120, height=40, command=lambda: None)
        self.botao_filtro.pack(side="right")

        # Tabela
        self.container_tabela = ctk.CTkFrame(frame, fg_color="transparent")
        self.container_tabela.pack(expand=True, fill="both", padx=100, pady=10)
        self.tabela_frame = ctk.CTkScrollableFrame(self.container_tabela, height=450)
        self.tabela_frame.pack(expand=True, fill="both")
        self.tabela_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)


    def renderizar_cabecalho(self):
        cor_azul_tema = ("#3B8ED0", "#1F6AA5")
        estilo = {"font": ("Arial", 13, "bold"), "height": 45, "text_color": "white", "fg_color": cor_azul_tema}
        ctk.CTkLabel(self.tabela_frame, text="DATA", **estilo).grid(row=0, column=0, padx=1, pady=(0, 2), sticky="nsew")
        ctk.CTkLabel(self.tabela_frame, text="TIPO", **estilo).grid(row=0, column=1, padx=1, pady=(0, 2), sticky="nsew")
        ctk.CTkLabel(self.tabela_frame, text="CATEGORIA", **estilo).grid(row=0, column=2, padx=1, pady=(0, 2), sticky="nsew")
        ctk.CTkLabel(self.tabela_frame, text="VALOR (R$)", **estilo).grid(row=0, column=3, padx=1, pady=(0, 2), sticky="nsew")

    def atualizar_tabela(self):
        for widget in self.tabela_frame.winfo_children(): widget.destroy()
        self.renderizar_cabecalho()
        df = ler_registros_csv(self.caminho_arquivo_csv)
        for i, row in df.iterrows():
            cor_tipo = "#ff6b6b" if row['Tipo'] == "Gasto" else "#51cf66" if row['Tipo'] == "Ganho" else "#5c7cff"
            estilo = {"height": 40}
            ctk.CTkLabel(self.tabela_frame, text=row['Data'], **estilo).grid(row=i+1, column=0, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=row['Tipo'].upper(), text_color=cor_tipo, font=("Arial", 11, "bold"), **estilo).grid(row=i+1, column=1, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=row['Categoria'], anchor="center", **estilo).grid(row=i+1, column=2, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=f"R$ {float(row['Valor']):,.2f}", anchor="center", font=("Arial", 12, "bold"), **estilo).grid(row=i+1, column=3, padx=1, pady=1, sticky="nsew")


    def mudar_tela(self, nome):
        # Esconde todas
        for f in self.telas.values(): f.pack_forget()
        
        # Atualiza se for visualização
        if nome == "visualizacao": self.atualizar_tabela()
        
        # Mostra a selecionada
        self.telas[nome].pack(expand=True, fill="both")
        
        # Estilo dos botões (Highlight no selecionado)
        for n, b in zip(["lancamentos", "visualizacao", "graficos", "comparativo"], 
                         [self.btn_lancamentos, self.btn_visualizacao, self.btn_graficos, self.btn_comparativo]):
            b.configure(fg_color=("gray75", "gray25") if n == nome else "transparent")


    def atualizar_categorias(self, tipo_selecionado):
        novas = self.categorias_opcoes[tipo_selecionado]
        self.dropdown_categoria.configure(values=novas); self.dropdown_categoria.set(novas[0])

    def coletar_dados_formulario(self):
        tipo = self.var_tipo.get()
        data = f"{self.combo_dia.get()}/{self.combo_mes.get()}/{self.combo_ano.get()}"
        categoria = self.dropdown_categoria.get()
        valor = self.entrada_valor.get().replace(",", ".")
        try:
            v = float(valor)
            if v <= 0: raise ValueError
        except:
            messagebox.showerror("Erro", "Valor inválido!"); return
        salvar_registro_csv(self.caminho_arquivo_csv, data, tipo, categoria, valor)
        self.entrada_valor.delete(0, 'end'); messagebox.showinfo("Sucesso", "Registro salvo!")

    def selecionar_arquivo(self):
        c = filedialog.askopenfilename(filetypes=[("Arquivos CSV", "*.csv")])
        if c: self.vincular_arquivo(c)

    def criar_arquivo(self):
        c = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="financas.csv")
        if c: criar_csv_vazio(c); self.vincular_arquivo(c)

    def vincular_arquivo(self, caminho):
        self.caminho_arquivo_csv = caminho
        self.frame_inicial.pack_forget()
        self.sidebar_frame.pack(side="left", fill="y")
        self.container_principal.pack(side="right", expand=True, fill="both")
        self.mudar_tela("lancamentos")

    def voltar_tela_inicial(self):
        self.caminho_arquivo_csv = ""
        self.sidebar_frame.pack_forget()
        self.container_principal.pack_forget()
        self.frame_inicial.pack(expand=True)

if __name__ == "__main__":
    app = OrganizadorFinanceiro()
    app.mainloop()
