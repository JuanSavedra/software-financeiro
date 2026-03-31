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

        # Categorias
        self.categorias_opcoes = {
            "Gasto": ["Alimentação", "Moradia (Aluguel/Parcela)", "Transporte", "Saúde", "Educação", "Lazer/Hobbies", "Assinaturas/Serviços", "Impostos/Taxas", "Outros Gastos"],
            "Ganho": ["Salário", "Freelance/Serviços", "Rendimento de Negócio", "Vendas", "Restituição/Cashback", "Outros Ganhos"],
            "Investimento": ["Tesouro Direto", "CDB / LCI / LCA", "Ações (B3)", "Fundos Imobiliários (FIIs)", "Criptomoedas", "Renda Passiva (Dividendos)", "Reserva de Emergência"]
        }
        self.todas_categorias = sorted(list(set(sum(self.categorias_opcoes.values(), []))))

        # --- TELA INICIAL ---
        self.frame_inicial = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inicial.pack(expand=True)

        ctk.CTkLabel(self.frame_inicial, text="Selecione ou crie um arquivo CSV para começar.", font=("Arial", 16)).pack(pady=20)
        ctk.CTkButton(self.frame_inicial, text="📁 Selecionar Arquivo", command=self.selecionar_arquivo, height=40).pack(pady=10)
        ctk.CTkButton(self.frame_inicial, text="➕ Criar Novo CSV", fg_color="#28a745", hover_color="#218838", command=self.criar_arquivo, height=40).pack(pady=10)

        # --- ESTRUTURA PRINCIPAL ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        ctk.CTkLabel(self.sidebar_frame, text="Organizador Financeiro", font=("Arial", 20, "bold")).pack(pady=(30, 30))

        self.btn_lancamentos = self.criar_botao_sidebar("📝 Lançamentos", lambda: self.mudar_tela("lancamentos"))
        self.btn_visualizacao = self.criar_botao_sidebar("📊 Visualização", lambda: self.mudar_tela("visualizacao"))
        self.btn_graficos = self.criar_botao_sidebar("📈 Gráficos", lambda: self.mudar_tela("graficos"))
        self.btn_comparativo = self.criar_botao_sidebar("⚖️ Comparativo", lambda: self.mudar_tela("comparativo"))

        self.btn_config = ctk.CTkButton(self.sidebar_frame, text="⚙️ Configurações", fg_color="transparent", border_width=1, command=self.voltar_tela_inicial)
        self.btn_config.pack(side="bottom", pady=20, padx=20, fill="x")

        # CONTEÚDO
        self.container_principal = ctk.CTkFrame(self, fg_color="transparent")
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
        btn = ctk.CTkButton(self.sidebar_frame, text=texto, anchor="w", height=45, fg_color="transparent", hover_color=("gray70", "gray30"), text_color=("gray10", "gray90"), command=comando)
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    def construir_telas_vazias(self):
        for nome in ["graficos", "comparativo"]:
            ctk.CTkLabel(self.telas[nome], text=f"Tela de {nome.capitalize()}\n(Em desenvolvimento)", font=("Arial", 24, "bold"), text_color="gray").pack(expand=True)

    def construir_formulario(self):
        frame = self.telas["lancamentos"]
        ctk.CTkLabel(frame, text="Novo Lançamento", font=("Arial", 28, "bold")).pack(pady=(30, 20))

        self.var_tipo = ctk.StringVar(value="Gasto")
        self.seletor_tipo = ctk.CTkSegmentedButton(frame, values=["Gasto", "Ganho", "Investimento"], variable=self.var_tipo, command=self.atualizar_categorias_form, height=45)
        self.seletor_tipo.pack(pady=15, fill="x", padx=200)

        ctk.CTkLabel(frame, text="Data:", font=("Arial", 14, "bold")).pack(anchor="w", pady=(20, 0), padx=200)
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

        ctk.CTkButton(frame, text="💾 Adicionar Registro", height=55, font=("Arial", 18, "bold"), command=self.coletar_dados_formulario).pack(pady=50, fill="x", padx=200)

    def construir_visualizacao(self):
        frame = self.telas["visualizacao"]
        
        # --- ÁREA DE FILTROS ---
        self.filter_frame = ctk.CTkFrame(frame)
        self.filter_frame.pack(pady=(20, 10), padx=100, fill="x")
        self.filter_frame.grid_columnconfigure((0,1,2,3,4,5,6,7), weight=1)

        # Linha 1: Mês, Ano, Tipo, Categoria
        ctk.CTkLabel(self.filter_frame, text="Mês:", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.f_mes = ctk.CTkComboBox(self.filter_frame, values=["Todos"] + [f"{i:02d}" for i in range(1, 13)], width=80, height=28, command=lambda _: self.atualizar_tabela())
        self.f_mes.set("Todos"); self.f_mes.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.filter_frame, text="Ano:", font=("Arial", 11, "bold")).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.f_ano = ctk.CTkComboBox(self.filter_frame, values=["Todos"] + [str(a) for a in range(2020, 2031)], width=90, height=28, command=lambda _: self.atualizar_tabela())
        self.f_ano.set("Todos"); self.f_ano.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.filter_frame, text="Tipo:", font=("Arial", 11, "bold")).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.f_tipo = ctk.CTkComboBox(self.filter_frame, values=["Todos", "Gasto", "Ganho", "Investimento"], width=110, height=28, command=lambda _: self.atualizar_tabela())
        self.f_tipo.set("Todos"); self.f_tipo.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.filter_frame, text="Categoria:", font=("Arial", 11, "bold")).grid(row=0, column=6, padx=5, pady=5, sticky="e")
        self.f_cat = ctk.CTkComboBox(self.filter_frame, values=["Todos"] + self.todas_categorias, width=140, height=28, command=lambda _: self.atualizar_tabela())
        self.f_cat.set("Todos"); self.f_cat.grid(row=0, column=7, padx=5, pady=5, sticky="w")

        # Linha 2: Botão Reset ocupando a linha inteira
        self.btn_reset = ctk.CTkButton(self.filter_frame, text="Limpar Todos os Filtros", height=32, fg_color="gray30", hover_color="gray40", command=self.reset_filtros)
        self.btn_reset.grid(row=1, column=0, columnspan=8, padx=10, pady=(5, 10), sticky="ew")

        # --- TABELA ---
        self.tabela_frame = ctk.CTkScrollableFrame(frame, height=400)
        self.tabela_frame.pack(expand=True, fill="both", padx=100, pady=10)
        self.tabela_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # --- RODAPÉ DE SALDO ---
        self.footer_frame = ctk.CTkFrame(frame, height=60, fg_color="transparent")
        self.footer_frame.pack(fill="x", padx=100, pady=(0, 20))
        self.label_saldo = ctk.CTkLabel(self.footer_frame, text="SALDO DO PERÍODO: R$ 0,00", font=("Arial", 20, "bold"))
        self.label_saldo.pack(side="right", padx=10)

    def reset_filtros(self):
        self.f_mes.set("Todos"); self.f_ano.set("Todos"); self.f_tipo.set("Todos"); self.f_cat.set("Todos")
        self.atualizar_tabela()

    def renderizar_cabecalho(self):
        cor_azul = ("#3B8ED0", "#1F6AA5")
        estilo = {"font": ("Arial", 13, "bold"), "height": 45, "text_color": "white", "fg_color": cor_azul}
        ctk.CTkLabel(self.tabela_frame, text="DATA", **estilo).grid(row=0, column=0, padx=1, pady=(0, 2), sticky="nsew")
        ctk.CTkLabel(self.tabela_frame, text="TIPO", **estilo).grid(row=0, column=1, padx=1, pady=(0, 2), sticky="nsew")
        ctk.CTkLabel(self.tabela_frame, text="CATEGORIA", **estilo).grid(row=0, column=2, padx=1, pady=(0, 2), sticky="nsew")
        ctk.CTkLabel(self.tabela_frame, text="VALOR (R$)", **estilo).grid(row=0, column=3, padx=1, pady=(0, 2), sticky="nsew")

    def atualizar_tabela(self):
        for widget in self.tabela_frame.winfo_children(): widget.destroy()
        self.renderizar_cabecalho()
        
        df = ler_registros_csv(self.caminho_arquivo_csv)
        if df.empty: 
            self.label_saldo.configure(text="SALDO DO PERÍODO: R$ 0,00", text_color="gray")
            return

        # Aplicar Filtros
        if self.f_mes.get() != "Todos":
            df = df[df['Data'].str.split('/').str[1] == self.f_mes.get()]
        if self.f_ano.get() != "Todos":
            df = df[df['Data'].str.split('/').str[2] == self.f_ano.get()]
        if self.f_tipo.get() != "Todos":
            df = df[df['Tipo'] == self.f_tipo.get()]
        if self.f_cat.get() != "Todos":
            df = df[df['Categoria'] == self.f_cat.get()]
        
        # Renderizar e Calcular Saldo
        saldo = 0
        for i, row in df.reset_index().iterrows():
            cor_tipo = "#ff6b6b" if row['Tipo'] == "Gasto" else "#51cf66" if row['Tipo'] == "Ganho" else "#5c7cff"
            valor = float(row['Valor'])
            if row['Tipo'] == "Ganho": saldo += valor
            else: saldo -= valor

            ctk.CTkLabel(self.tabela_frame, text=row['Data'], height=40).grid(row=i+1, column=0, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=row['Tipo'].upper(), text_color=cor_tipo, font=("Arial", 11, "bold"), height=40).grid(row=i+1, column=1, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=row['Categoria'], anchor="center", height=40).grid(row=i+1, column=2, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=f"R$ {valor:,.2f}", anchor="center", font=("Arial", 12, "bold"), height=40).grid(row=i+1, column=3, padx=1, pady=1, sticky="nsew")

        cor_saldo = "#51cf66" if saldo >= 0 else "#ff6b6b"
        self.label_saldo.configure(text=f"SALDO DO PERÍODO: R$ {saldo:,.2f}", text_color=cor_saldo)

    def mudar_tela(self, nome):
        for f in self.telas.values(): f.pack_forget()
        if nome == "visualizacao": self.atualizar_tabela()
        self.telas[nome].pack(expand=True, fill="both")
        for n, b in zip(["lancamentos", "visualizacao", "graficos", "comparativo"], [self.btn_lancamentos, self.btn_visualizacao, self.btn_graficos, self.btn_comparativo]):
            b.configure(fg_color=("gray75", "gray25") if n == nome else "transparent")

    def atualizar_categorias_form(self, tipo):
        novas = self.categorias_opcoes[tipo]
        self.dropdown_categoria.configure(values=novas); self.dropdown_categoria.set(novas[0])

    def coletar_dados_formulario(self):
        tipo, valor = self.var_tipo.get(), self.entrada_valor.get().replace(",", ".")
        data = f"{self.combo_dia.get()}/{self.combo_mes.get()}/{self.combo_ano.get()}"
        try:
            if float(valor) <= 0: raise ValueError
        except:
            messagebox.showerror("Erro", "Valor inválido!"); return
        salvar_registro_csv(self.caminho_arquivo_csv, data, tipo, self.dropdown_categoria.get(), valor)
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
        self.sidebar_frame.pack_forget(); self.container_principal.pack_forget()
        self.frame_inicial.pack(expand=True)

if __name__ == "__main__":
    app = OrganizadorFinanceiro()
    app.mainloop()
