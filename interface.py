import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
import datetime
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from banco_de_dados import criar_csv_vazio, salvar_registro_csv, ler_registros_csv

class OrganizadorFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Organizador Financeiro")
        self.geometry("1280x720")
        self.caminho_arquivo_csv = ""
        
        # Dados para comparação
        self.totais_comp = {
            "l": {"Gasto": 0, "Ganho": 0, "Investimento": 0},
            "r": {"Gasto": 0, "Ganho": 0, "Investimento": 0}
        }
        
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
        ctk.CTkLabel(self.sidebar_frame, text="Organizador\nFinanceiro", font=("Arial", 20, "bold")).pack(pady=(30, 30))

        self.btn_lancamentos = self.criar_botao_sidebar("Lançamentos", lambda: self.mudar_tela("lancamentos"))
        self.btn_visualizacao = self.criar_botao_sidebar("Visualização", lambda: self.mudar_tela("visualizacao"))
        self.btn_graficos = self.criar_botao_sidebar("Gráficos", lambda: self.mudar_tela("graficos"))
        self.btn_comparativo = self.criar_botao_sidebar("Comparativo", lambda: self.mudar_tela("comparativo"))

        self.btn_config = ctk.CTkButton(self.sidebar_frame, text="⚙️ Configurações", 
                                        fg_color=("#3B8ED0", "#1F6AA5"), 
                                        hover_color=("#3279B0", "#185382"), 
                                        command=self.voltar_tela_inicial)
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
        self.construir_graficos()
        self.construir_comparativo()

    def criar_botao_sidebar(self, texto, comando):
        btn = ctk.CTkButton(self.sidebar_frame, text=texto, anchor="w", height=45, fg_color="transparent", hover_color=("gray70", "gray30"), text_color=("gray10", "gray90"), command=comando)
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    def construir_comparativo(self):
        frame = self.telas["comparativo"]
        
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0) # Linha para insights

        # --- COLUNA ESQUERDA ---
        self.frame_comp_l = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_comp_l.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.cont_l = ctk.CTkFrame(self.frame_comp_l, fg_color="transparent")
        self.cont_l.pack(expand=True)
        filter_l = ctk.CTkFrame(self.cont_l)
        filter_l.pack(pady=(0, 5), padx=20, fill="x")
        ctk.CTkLabel(filter_l, text="Mês:", font=("Arial", 11, "bold")).pack(side="left", padx=5)
        self.cl_mes = ctk.CTkComboBox(filter_l, values=["Todos"] + [f"{i:02d}" for i in range(1, 13)], width=80, height=28, command=lambda _: self.atualizar_comparativo("l"))
        self.cl_mes.set("Todos"); self.cl_mes.pack(side="left", padx=5)
        ctk.CTkLabel(filter_l, text="Ano:", font=("Arial", 11, "bold")).pack(side="left", padx=5)
        self.cl_ano = ctk.CTkComboBox(filter_l, values=["Todos"] + [str(a) for a in range(2020, 2031)], width=90, height=28, command=lambda _: self.atualizar_comparativo("l"))
        self.cl_ano.set("Todos"); self.cl_ano.pack(side="left", padx=5)
        self.canvas_comp_l = ctk.CTkFrame(self.cont_l, fg_color="transparent")
        self.canvas_comp_l.pack(fill="both")

        # --- DIVISOR CENTRAL ---
        divisor = ctk.CTkFrame(frame, width=2, fg_color="gray30")
        divisor.grid(row=0, column=1, sticky="ns", pady=50)

        # --- COLUNA DIREITA ---
        self.frame_comp_r = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_comp_r.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self.cont_r = ctk.CTkFrame(self.frame_comp_r, fg_color="transparent")
        self.cont_r.pack(expand=True)
        filter_r = ctk.CTkFrame(self.cont_r)
        filter_r.pack(pady=(0, 5), padx=20, fill="x")
        ctk.CTkLabel(filter_r, text="Mês:", font=("Arial", 11, "bold")).pack(side="left", padx=5)
        self.cr_mes = ctk.CTkComboBox(filter_r, values=["Todos"] + [f"{i:02d}" for i in range(1, 13)], width=80, height=28, command=lambda _: self.atualizar_comparativo("r"))
        self.cr_mes.set("Todos"); self.cr_mes.pack(side="left", padx=5)
        ctk.CTkLabel(filter_r, text="Ano:", font=("Arial", 11, "bold")).pack(side="left", padx=5)
        self.cr_ano = ctk.CTkComboBox(filter_r, values=["Todos"] + [str(a) for a in range(2020, 2031)], width=90, height=28, command=lambda _: self.atualizar_comparativo("r"))
        self.cr_ano.set("Todos"); self.cr_ano.pack(side="left", padx=5)
        self.canvas_comp_r = ctk.CTkFrame(self.cont_r, fg_color="transparent")
        self.canvas_comp_r.pack(fill="both")

        # --- SEÇÃO DE INSIGHTS (RODAPÉ) ---
        self.frame_insights = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_insights.grid(row=1, column=0, columnspan=3, pady=(0, 40), sticky="ew")
        
        # Traçado horizontal
        ctk.CTkFrame(self.frame_insights, height=2, fg_color="gray30").pack(fill="x", padx=200, pady=(0, 20))
        
        # Labels de Insight
        self.lbl_ins_invest = ctk.CTkLabel(self.frame_insights, text="", font=("Arial", 15, "bold"))
        self.lbl_ins_invest.pack(pady=2)
        self.lbl_ins_gasto = ctk.CTkLabel(self.frame_insights, text="", font=("Arial", 15, "bold"))
        self.lbl_ins_gasto.pack(pady=2)
        self.lbl_ins_ganho = ctk.CTkLabel(self.frame_insights, text="", font=("Arial", 15, "bold"))
        self.lbl_ins_ganho.pack(pady=2)

    def atualizar_comparativo(self, lado):
        parent = self.canvas_comp_l if lado == "l" else self.canvas_comp_r
        mes_val = self.cl_mes.get() if lado == "l" else self.cr_mes.get()
        ano_val = self.cl_ano.get() if lado == "l" else self.cr_ano.get()

        for widget in parent.winfo_children(): widget.destroy()
        
        # Reseta totais do lado antes de calcular
        self.totais_comp[lado] = {"Gasto": 0, "Ganho": 0, "Investimento": 0}

        df = ler_registros_csv(self.caminho_arquivo_csv)
        if df.empty:
            ctk.CTkLabel(parent, text="Sem dados.", font=("Arial", 14)).pack(expand=True)
            self.atualizar_insights(); return

        if mes_val != "Todos": df = df[df['Data'].str.split('/').str[1] == mes_val]
        if ano_val != "Todos": df = df[df['Data'].str.split('/').str[2] == ano_val]

        if df.empty:
            ctk.CTkLabel(parent, text="Sem dados no período.", font=("Arial", 12)).pack(expand=True)
            self.atualizar_insights(); return

        resumo = df.groupby('Tipo')['Valor'].sum()
        for t in resumo.index: self.totais_comp[lado][t] = resumo[t]

        labels, valores = resumo.index.tolist(), resumo.values.tolist()
        mapa_cores = {"Gasto": "#ff6b6b", "Ganho": "#51cf66", "Investimento": "#5c7cff"}
        cores = [mapa_cores[l] for l in labels]

        fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor='none')
        ax.pie(valores, autopct='%1.1f%%', startangle=140, colors=cores, 
               textprops={'color': "white", 'weight': 'bold', 'fontsize': 8}, wedgeprops={'edgecolor': 'none'})
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw(); canvas.get_tk_widget().pack(expand=True); plt.close(fig)

        leg_frame = ctk.CTkFrame(parent, fg_color="transparent")
        leg_frame.pack(pady=5)
        for l, c, v in zip(labels, cores, valores):
            it = ctk.CTkFrame(leg_frame, fg_color="transparent")
            it.pack(pady=3, anchor="w")
            ctk.CTkFrame(it, width=15, height=15, fg_color=c, corner_radius=2).pack(side="left", padx=8)
            ctk.CTkLabel(it, text=f"{l}: R$ {v:,.2f}", font=("Arial", 14, "bold")).pack(side="left")
        
        self.atualizar_insights()

    def atualizar_insights(self):
        def calc_diff(tipo):
            val_l = self.totais_comp["l"].get(tipo, 0)
            val_r = self.totais_comp["r"].get(tipo, 0)
            return abs(val_l - val_r)

        diff_inv = calc_diff("Investimento")
        diff_gas = calc_diff("Gasto")
        diff_gan = calc_diff("Ganho")

        self.lbl_ins_invest.configure(text=f"Você investiu mais R$ {diff_inv:,.2f} comparado ao outro mês/ano")
        self.lbl_ins_gasto.configure(text=f"Você gastou mais R$ {diff_gas:,.2f} comparado ao outro mês/ano")
        self.lbl_ins_ganho.configure(text=f"Você ganhou mais R$ {diff_gan:,.2f} comparado ao outro mês/ano")

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
        ctk.CTkButton(frame, text="Adicionar Registro", height=55, font=("Arial", 18, "bold"), command=self.coletar_dados_formulario).pack(pady=50, fill="x", padx=200)

    def construir_visualizacao(self):
        frame = self.telas["visualizacao"]
        self.filter_frame = ctk.CTkFrame(frame)
        self.filter_frame.pack(pady=(20, 10), padx=100, fill="x")
        self.filter_frame.grid_columnconfigure((0,1,2,3,4,5,6,7), weight=1)
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
        ctk.CTkButton(self.filter_frame, text="Limpar Todos os Filtros", height=32, fg_color="gray30", hover_color="gray40", command=self.reset_filtros).grid(row=1, column=0, columnspan=8, padx=10, pady=(5, 10), sticky="ew")
        self.tabela_frame = ctk.CTkScrollableFrame(frame, height=400)
        self.tabela_frame.pack(expand=True, fill="both", padx=100, pady=10)
        self.tabela_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.footer_frame = ctk.CTkFrame(frame, height=60, fg_color="transparent")
        self.footer_frame.pack(fill="x", padx=100, pady=(0, 20))
        self.label_saldo = ctk.CTkLabel(self.footer_frame, text="SALDO DO PERÍODO: R$ 0,00", font=("Arial", 20, "bold"))
        self.label_saldo.pack(side="right", padx=10)

    def construir_graficos(self):
        frame = self.telas["graficos"]
        self.filter_frame_graf = ctk.CTkFrame(frame)
        self.filter_frame_graf.pack(pady=(20, 10), padx=100, fill="x")
        self.filter_frame_graf.grid_columnconfigure((0,1,2,3), weight=1)
        ctk.CTkLabel(self.filter_frame_graf, text="Mês:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.g_mes = ctk.CTkComboBox(self.filter_frame_graf, values=["Todos"] + [f"{i:02d}" for i in range(1, 13)], width=100, command=lambda _: self.atualizar_graficos())
        self.g_mes.set("Todos"); self.g_mes.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(self.filter_frame_graf, text="Ano:", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.g_ano = ctk.CTkComboBox(self.filter_frame_graf, values=["Todos"] + [str(a) for a in range(2020, 2031)], width=110, command=lambda _: self.atualizar_graficos())
        self.g_ano.set("Todos"); self.g_ano.grid(row=0, column=3, padx=10, pady=10, sticky="w")
        self.canvas_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.canvas_frame.pack(expand=True, fill="both", padx=100, pady=10)

    def atualizar_graficos(self):
        for widget in self.canvas_frame.winfo_children(): widget.destroy()
        df = ler_registros_csv(self.caminho_arquivo_csv)
        if df.empty:
            ctk.CTkLabel(self.canvas_frame, text="Nenhum dado disponível.", font=("Arial", 16)).pack(expand=True); return
        if self.g_mes.get() != "Todos": df = df[df['Data'].str.split('/').str[1] == self.g_mes.get()]
        if self.g_ano.get() != "Todos": df = df[df['Data'].str.split('/').str[2] == self.g_ano.get()]
        if df.empty:
            ctk.CTkLabel(self.canvas_frame, text="Nenhum dado encontrado.", font=("Arial", 16)).pack(expand=True); return
        resumo = df.groupby('Tipo')['Valor'].sum()
        labels, valores = resumo.index.tolist(), resumo.values.tolist()
        mapa_cores = {"Gasto": "#ff6b6b", "Ganho": "#51cf66", "Investimento": "#5c7cff"}
        cores = [mapa_cores[l] for l in labels]
        fig, ax = plt.subplots(figsize=(5, 5), facecolor='none')
        ax.pie(valores, autopct='%1.1f%%', startangle=140, colors=cores, 
               textprops={'color': "white", 'weight': 'bold', 'fontsize': 12}, wedgeprops={'edgecolor': 'none'})
        ax.set_title("Distribuição de Valores", color="white", fontdict={'fontsize': 18, 'weight': 'bold'}, pad=20)
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw(); canvas.get_tk_widget().pack(expand=True); plt.close(fig)
        leg_frame = ctk.CTkFrame(self.canvas_frame, fg_color="transparent")
        leg_frame.pack(pady=(0, 20))
        for l, c, v in zip(labels, cores, valores):
            it = ctk.CTkFrame(leg_frame, fg_color="transparent")
            it.pack(side="left", padx=20)
            ctk.CTkFrame(it, width=15, height=15, fg_color=c, corner_radius=2).pack(side="left", padx=5)
            ctk.CTkLabel(it, text=f"{l}: R$ {v:,.2f}", font=("Arial", 13, "bold")).pack(side="left")

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
            self.label_saldo.configure(text="SALDO DO PERÍODO: R$ 0,00", text_color="gray"); return
        if self.f_mes.get() != "Todos": df = df[df['Data'].str.split('/').str[1] == self.f_mes.get()]
        if self.f_ano.get() != "Todos": df = df[df['Data'].str.split('/').str[2] == self.f_ano.get()]
        if self.f_tipo.get() != "Todos": df = df[df['Tipo'] == self.f_tipo.get()]
        if self.f_cat.get() != "Todos": df = df[df['Categoria'] == self.f_cat.get()]
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
        if nome == "graficos": self.atualizar_graficos()
        if nome == "comparativo": self.atualizar_comparativo("l"); self.atualizar_comparativo("r")
        self.telas[nome].pack(expand=True, fill="both")
        for n, b in zip(["lancamentos", "visualizacao", "graficos", "comparativo"], [self.btn_lancamentos, self.btn_visual_sidebar, self.btn_graficos, self.btn_comparativo]):
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
