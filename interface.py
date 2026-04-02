import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
import datetime
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from banco_de_dados import criar_csv_vazio, salvar_registro_csv, ler_registros_csv

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, compatível com PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class OrganizadorFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Organizador Financeiro")
        self.geometry("1280x720")
        self.caminho_arquivo_csv = ""
        
        # Listas para guardar referências e atualizar o tema dinamicamente
        self.lista_titulos = []
        self.lista_dropdowns = []
        self.lista_entries = []
        
        # Dados para comparação
        self.totais_comp = {
            "l": {"Gasto": 0, "Ganho": 0, "Investimento": 0},
            "r": {"Gasto": 0, "Ganho": 0, "Investimento": 0}
        }
        
        # Configuração do Tema Inicial (Rosa)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme(resource_path("pink_theme.json"))
        self.tema_atual = "rosa"

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

        self.lbl_inicial = ctk.CTkLabel(self.frame_inicial, text="Selecione ou crie um arquivo CSV para começar.", font=("Arial", 16))
        self.lbl_inicial.pack(pady=20)
        self.lista_titulos.append(self.lbl_inicial)
        
        self.btn_selecionar = ctk.CTkButton(self.frame_inicial, text="📁 Selecionar Arquivo", command=self.selecionar_arquivo, height=40)
        self.btn_selecionar.pack(pady=10)
        
        self.btn_criar = ctk.CTkButton(self.frame_inicial, text="➕ Criar Novo CSV", command=self.criar_arquivo, height=40)
        self.btn_criar.pack(pady=10)

        # --- ESTRUTURA PRINCIPAL ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.lbl_logo = ctk.CTkLabel(self.sidebar_frame, text="Organizador\nFinanceiro", font=("Arial", 20, "bold"))
        self.lbl_logo.pack(pady=(30, 30))

        self.btn_lancamentos = self.criar_botao_sidebar("Lançamentos", lambda: self.mudar_tela("lancamentos"))
        self.btn_visualizacao = self.criar_botao_sidebar("Visualização", lambda: self.mudar_tela("visualizacao"))
        self.btn_graficos = self.criar_botao_sidebar("Gráficos", lambda: self.mudar_tela("graficos"))
        self.btn_comparativo = self.criar_botao_sidebar("Comparativo", lambda: self.mudar_tela("comparativo"))

        # Botão de Tema
        self.btn_tema = ctk.CTkButton(self.sidebar_frame, text="Tema", command=self.alternar_tema)
        self.btn_tema.pack(side="bottom", pady=(10, 20), padx=20, fill="x")

        # Botão Substituir Arquivo
        self.btn_config = ctk.CTkButton(self.sidebar_frame, text="Substituir Arquivo", command=self.voltar_tela_inicial)
        self.btn_config.pack(side="bottom", pady=10, padx=20, fill="x")

        # CONTEÚDO
        self.container_principal = ctk.CTkFrame(self)
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

        # Aplica cores iniciais
        self.atualizar_estilo_botoes()

    def atualizar_estilo_botoes(self):
        if self.tema_atual == "rosa":
            cor_bg_app = ["#FCF0F5", "#1A1A1A"]
            cor_bg_sidebar = ["#F8D7E4", "#2B2B2B"]
            cor_base = ("#FF69B4", "#C71585")
            cor_hover = ("#FF1493", "#8B008B")
            cor_texto_side = ("#C71585", "#FFB6C1")
            cor_hover_side = ("#F8D7E4", "#3D3D3D")
            cor_titulo = ("#C71585", "#FFB6C1")
            cor_dropdown_bg = ["#FFFFFF", "#3D3D3D"]
            cor_dropdown_border = ["#FFB6C1", "#C71585"]
            cor_seg_bg = ["#FFB6C1", "gray29"]
            cor_seg_unselected = ["#FFB6C1", "gray29"]
        else:
            cor_bg_app = ["#FFFFFF", "#242424"] 
            cor_bg_sidebar = ["#F2F2F2", "#1e1e1e"]
            cor_base = ("#3b8ed0", "#1f6aa5")
            cor_hover = ("#367e96", "#144870")
            cor_texto_side = ("#1f6aa5", "#DCE4EE")
            cor_hover_side = ("#DBE9F4", "#2b2b2b")
            cor_titulo = ("#000000", "#FFFFFF")
            cor_dropdown_bg = ["#F9F9FA", "#343638"]
            cor_dropdown_border = ["#979797", "#565b5e"]
            cor_seg_bg = ["#dbdbdb", "gray29"]
            cor_seg_unselected = ["#dbdbdb", "gray29"]

        # 1. Backgrounds
        self.configure(fg_color=cor_bg_app)
        self.sidebar_frame.configure(fg_color=cor_bg_sidebar)
        self.container_principal.configure(fg_color=cor_bg_app)

        # 2. Sidebar e Logo
        self.btn_config.configure(fg_color=cor_base, hover_color=cor_hover)
        self.btn_tema.configure(fg_color=cor_base, hover_color=cor_hover)
        self.lbl_logo.configure(text_color=cor_titulo)
        for btn in [self.btn_lancamentos, self.btn_visualizacao, self.btn_graficos, self.btn_comparativo]:
            btn.configure(text_color=cor_texto_side, hover_color=cor_hover_side)

        # 3. Títulos e Labels
        for label in self.lista_titulos:
            label.configure(text_color=cor_titulo)

        # 4. Dropdowns e Inputs
        for combo in self.lista_dropdowns:
            combo.configure(fg_color=cor_dropdown_bg, border_color=cor_dropdown_border, button_color=cor_dropdown_border)
        for entry in self.lista_entries:
            entry.configure(fg_color=cor_dropdown_bg, border_color=cor_dropdown_border)

        # 5. Segmented Button
        if hasattr(self, 'seletor_tipo'):
            self.seletor_tipo.configure(
                fg_color=cor_seg_bg,
                selected_color=cor_base[1] if isinstance(cor_base, tuple) else cor_base,
                unselected_color=cor_seg_unselected,
                unselected_hover_color=cor_hover_side
            )

        # 6. Botões de Ação
        if hasattr(self, 'btn_adicionar'):
            self.btn_adicionar.configure(fg_color=cor_base, hover_color=cor_hover)
        if hasattr(self, 'btn_limpar_filtros'):
            self.btn_limpar_filtros.configure(fg_color=cor_seg_bg, hover_color=cor_hover)
        self.btn_selecionar.configure(fg_color=cor_base, hover_color=cor_hover)

        # Atualiza tela ativa
        for nome, frame in self.telas.items():
            if frame.winfo_ismapped():
                self.mudar_tela(nome)

    def alternar_tema(self):
        self.tema_atual = "blue" if self.tema_atual == "rosa" else "rosa"
        ctk.set_default_color_theme(resource_path(f"{self.tema_atual}_theme.json"))
        self.atualizar_estilo_botoes()
        if self.caminho_arquivo_csv:
            self.atualizar_tabela()
            self.atualizar_graficos()
            self.atualizar_comparativo("l")
            self.atualizar_comparativo("r")
        messagebox.showinfo("Tema Alterado", "O tema foi aplicado.")

    def criar_botao_sidebar(self, texto, comando):
        btn = ctk.CTkButton(self.sidebar_frame, text=texto, anchor="w", height=45, fg_color="transparent", command=comando)
        btn.pack(fill="x", padx=10, pady=5)
        return btn

    def construir_comparativo(self):
        frame = self.telas["comparativo"]
        frame.grid_columnconfigure((0, 2), weight=1)
        frame.grid_columnconfigure(1, weight=0)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0) 
        
        self.frame_comp_l = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_comp_l.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.cont_l = ctk.CTkFrame(self.frame_comp_l, fg_color="transparent")
        self.cont_l.pack(expand=True)
        filter_l = ctk.CTkFrame(self.cont_l)
        filter_l.pack(pady=(0, 5), padx=20, fill="x")
        
        lbl_m1 = ctk.CTkLabel(filter_l, text="Mês:", font=("Arial", 11, "bold"))
        lbl_m1.pack(side="left", padx=5)
        self.lista_titulos.append(lbl_m1)
        
        self.cl_mes = ctk.CTkComboBox(filter_l, values=["Todos"] + [f"{i:02d}" for i in range(1, 13)], width=80, height=28, command=lambda _: self.atualizar_comparativo("l"))
        self.cl_mes.set("Todos")
        self.cl_mes.pack(side="left", padx=5)
        self.lista_dropdowns.append(self.cl_mes)
        
        lbl_a1 = ctk.CTkLabel(filter_l, text="Ano:", font=("Arial", 11, "bold"))
        lbl_a1.pack(side="left", padx=5)
        self.lista_titulos.append(lbl_a1)
        
        self.cl_ano = ctk.CTkComboBox(filter_l, values=["Todos"] + [str(a) for a in range(2020, 2031)], width=90, height=28, command=lambda _: self.atualizar_comparativo("l"))
        self.cl_ano.set("Todos")
        self.cl_ano.pack(side="left", padx=5)
        self.lista_dropdowns.append(self.cl_ano)
        
        self.canvas_comp_l = ctk.CTkFrame(self.cont_l, fg_color="transparent")
        self.canvas_comp_l.pack(fill="both")
        
        divisor = ctk.CTkFrame(frame, width=2, fg_color="gray30")
        divisor.grid(row=0, column=1, sticky="ns", pady=50)
        
        self.frame_comp_r = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_comp_r.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self.cont_r = ctk.CTkFrame(self.frame_comp_r, fg_color="transparent")
        self.cont_r.pack(expand=True)
        filter_r = ctk.CTkFrame(self.cont_r)
        filter_r.pack(pady=(0, 5), padx=20, fill="x")
        
        lbl_m2 = ctk.CTkLabel(filter_r, text="Mês:", font=("Arial", 11, "bold"))
        lbl_m2.pack(side="left", padx=5)
        self.lista_titulos.append(lbl_m2)
        
        self.cr_mes = ctk.CTkComboBox(filter_r, values=["Todos"] + [f"{i:02d}" for i in range(1, 13)], width=80, height=28, command=lambda _: self.atualizar_comparativo("r"))
        self.cr_mes.set("Todos")
        self.cr_mes.pack(side="left", padx=5)
        self.lista_dropdowns.append(self.cr_mes)
        
        lbl_a2 = ctk.CTkLabel(filter_r, text="Ano:", font=("Arial", 11, "bold"))
        lbl_a2.pack(side="left", padx=5)
        self.lista_titulos.append(lbl_a2)
        
        self.cr_ano = ctk.CTkComboBox(filter_r, values=["Todos"] + [str(a) for a in range(2020, 2031)], width=90, height=28, command=lambda _: self.atualizar_comparativo("r"))
        self.cr_ano.set("Todos")
        self.cr_ano.pack(side="left", padx=5)
        self.lista_dropdowns.append(self.cr_ano)
        
        self.canvas_comp_r = ctk.CTkFrame(self.cont_r, fg_color="transparent")
        self.canvas_comp_r.pack(fill="both")
        
        self.frame_insights = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_insights.grid(row=1, column=0, columnspan=3, pady=(0, 40), sticky="ew")
        ctk.CTkFrame(self.frame_insights, height=2, fg_color="gray30").pack(fill="x", padx=200, pady=(0, 20))
        
        self.lbl_ins_invest = ctk.CTkLabel(self.frame_insights, text="", font=("Arial", 15, "bold"))
        self.lbl_ins_invest.pack(pady=2)
        self.lista_titulos.append(self.lbl_ins_invest)
        
        self.lbl_ins_gasto = ctk.CTkLabel(self.frame_insights, text="", font=("Arial", 15, "bold"))
        self.lbl_ins_gasto.pack(pady=2)
        self.lista_titulos.append(self.lbl_ins_gasto)
        
        self.lbl_ins_ganho = ctk.CTkLabel(self.frame_insights, text="", font=("Arial", 15, "bold"))
        self.lbl_ins_ganho.pack(pady=2)
        self.lista_titulos.append(self.lbl_ins_ganho)

    def atualizar_comparativo(self, lado):
        parent = self.canvas_comp_l if lado == "l" else self.canvas_comp_r
        mes_val, ano_val = (self.cl_mes.get(), self.cl_ano.get()) if lado == "l" else (self.cr_mes.get(), self.cr_ano.get())
        for widget in parent.winfo_children(): widget.destroy()
        
        self.totais_comp[lado] = {"Gasto": 0, "Ganho": 0, "Investimento": 0}
        df = ler_registros_csv(self.caminho_arquivo_csv)
        if df.empty:
            l = ctk.CTkLabel(parent, text="Sem dados.", font=("Arial", 14))
            l.pack(expand=True)
            self.lista_titulos.append(l)
            self.atualizar_insights()
            return
            
        if mes_val != "Todos": df = df[df['Data'].str.split('/').str[1] == mes_val]
        if ano_val != "Todos": df = df[df['Data'].str.split('/').str[2] == ano_val]
        
        if df.empty:
            l = ctk.CTkLabel(parent, text="Sem dados no período.", font=("Arial", 12))
            l.pack(expand=True)
            self.lista_titulos.append(l)
            self.atualizar_insights()
            return
            
        resumo = df.groupby('Tipo')['Valor'].sum()
        for t in resumo.index: self.totais_comp[lado][t] = resumo[t]
        
        labels, valores = resumo.index.tolist(), resumo.values.tolist()
        mapa_cores = {"Gasto": "#ff6b6b", "Ganho": "#51cf66", "Investimento": ("#FF69B4" if self.tema_atual == "rosa" else "#3b8ed0")}
        
        fig, ax = plt.subplots(figsize=(3.5, 3.5), facecolor='none')
        ax.pie(valores, autopct='%1.1f%%', startangle=140, colors=[mapa_cores[l] for l in labels], textprops={'color': "white", 'weight': 'bold', 'fontsize': 8}, wedgeprops={'edgecolor': 'none'})
        FigureCanvasTkAgg(fig, master=parent).get_tk_widget().pack(expand=True)
        plt.close(fig)
        
        leg_frame = ctk.CTkFrame(parent, fg_color="transparent")
        leg_frame.pack(pady=5)
        for l, c, v in zip(labels, [mapa_cores[l] for l in labels], valores):
            it = ctk.CTkFrame(leg_frame, fg_color="transparent")
            it.pack(pady=3, anchor="w")
            ctk.CTkFrame(it, width=15, height=15, fg_color=c, corner_radius=2).pack(side="left", padx=8)
            lbl = ctk.CTkLabel(it, text=f"{l}: R$ {v:,.2f}", font=("Arial", 14, "bold"))
            lbl.pack(side="left")
            self.lista_titulos.append(lbl)
        self.atualizar_insights()

    def atualizar_insights(self):
        def calc_diff(tipo): return abs(self.totais_comp["l"].get(tipo, 0) - self.totais_comp["r"].get(tipo, 0))
        self.lbl_ins_invest.configure(text=f"Você investiu mais R$ {calc_diff('Investimento'):,.2f} comparado ao outro mês/ano")
        self.lbl_ins_gasto.configure(text=f"Você gastou mais R$ {calc_diff('Gasto'):,.2f} comparado ao outro mês/ano")
        self.lbl_ins_ganho.configure(text=f"Você ganhou mais R$ {calc_diff('Ganho'):,.2f} comparado ao outro mês/ano")

    def construir_formulario(self):
        frame = self.telas["lancamentos"]
        tit = ctk.CTkLabel(frame, text="Novo Lançamento", font=("Arial", 28, "bold"))
        tit.pack(pady=(30, 20))
        self.lista_titulos.append(tit)
        
        self.var_tipo = ctk.StringVar(value="Gasto")
        self.seletor_tipo = ctk.CTkSegmentedButton(frame, values=["Gasto", "Ganho", "Investimento"], variable=self.var_tipo, command=self.atualizar_categorias_form, height=45)
        self.seletor_tipo.pack(pady=15, fill="x", padx=200)
        
        lbl_d = ctk.CTkLabel(frame, text="Data:", font=("Arial", 14, "bold"))
        lbl_d.pack(anchor="w", pady=(20, 0), padx=200)
        self.lista_titulos.append(lbl_d)
        
        self.frame_data = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_data.pack(pady=5, fill="x", padx=200)
        hoje = datetime.date.today()
        
        self.combo_dia = ctk.CTkComboBox(self.frame_data, values=[f"{i:02d}" for i in range(1, 32)], width=100)
        self.combo_dia.set(f"{hoje.day:02d}")
        self.combo_dia.pack(side="left", padx=10)
        self.lista_dropdowns.append(self.combo_dia)
        
        self.combo_mes = ctk.CTkComboBox(self.frame_data, values=[f"{i:02d}" for i in range(1, 13)], width=100)
        self.combo_mes.set(f"{hoje.month:02d}")
        self.combo_mes.pack(side="left", padx=10)
        self.lista_dropdowns.append(self.combo_mes)
        
        self.combo_ano = ctk.CTkComboBox(self.frame_data, values=[str(a) for a in range(2020, 2031)], width=120)
        self.combo_ano.set(str(hoje.year))
        self.combo_ano.pack(side="left", padx=10)
        self.lista_dropdowns.append(self.combo_ano)
        
        lbl_v = ctk.CTkLabel(frame, text="Valor (R$):", font=("Arial", 14, "bold"))
        lbl_v.pack(anchor="w", pady=(20, 0), padx=200)
        self.lista_titulos.append(lbl_v)
        
        self.entrada_valor = ctk.CTkEntry(frame, placeholder_text="0.00", height=45)
        self.entrada_valor.pack(pady=5, fill="x", padx=200)
        self.lista_entries.append(self.entrada_valor)
        
        lbl_c = ctk.CTkLabel(frame, text="Categoria:", font=("Arial", 14, "bold"))
        lbl_c.pack(anchor="w", pady=(20, 0), padx=200)
        self.lista_titulos.append(lbl_c)
        
        self.dropdown_categoria = ctk.CTkComboBox(frame, values=self.categorias_opcoes["Gasto"], height=45)
        self.dropdown_categoria.pack(pady=5, fill="x", padx=200)
        self.lista_dropdowns.append(self.dropdown_categoria)
        
        self.btn_adicionar = ctk.CTkButton(frame, text="Adicionar Registro", height=55, font=("Arial", 18, "bold"), command=self.coletar_dados_formulario)
        self.btn_adicionar.pack(pady=50, fill="x", padx=200)

    def construir_visualizacao(self):
        frame = self.telas["visualizacao"]
        self.filter_frame = ctk.CTkFrame(frame)
        self.filter_frame.pack(pady=(20, 10), padx=100, fill="x")
        self.filter_frame.grid_columnconfigure((0,1,2,3,4,5,6,7), weight=1)
        
        for i, (txt, vals) in enumerate(zip(["Mês:", "Ano:", "Tipo:", "Categoria:"], [["Todos"] + [f"{i:02d}" for i in range(1, 13)], ["Todos"] + [str(a) for a in range(2020, 2031)], ["Todos", "Gasto", "Ganho", "Investimento"], ["Todos"] + self.todas_categorias])):
            l = ctk.CTkLabel(self.filter_frame, text=txt, font=("Arial", 11, "bold"))
            l.grid(row=0, column=i*2, padx=5, pady=5, sticky="e")
            self.lista_titulos.append(l)
            c = ctk.CTkComboBox(self.filter_frame, values=vals, width=100 if i > 1 else 80, height=28, command=self.atualizar_categorias_filtro if i==2 else lambda _: self.atualizar_tabela())
            c.set("Todos")
            c.grid(row=0, column=i*2+1, padx=5, pady=5, sticky="w")
            self.lista_dropdowns.append(c)
            if i==0: self.f_mes = c
            elif i==1: self.f_ano = c
            elif i==2: self.f_tipo = c
            else: self.f_cat = c
            
        self.btn_limpar_filtros = ctk.CTkButton(self.filter_frame, text="Limpar Todos os Filtros", height=32, command=self.reset_filtros)
        self.btn_limpar_filtros.grid(row=1, column=0, columnspan=8, padx=10, pady=(5, 10), sticky="ew")
        
        self.tabela_frame = ctk.CTkScrollableFrame(frame, height=400)
        self.tabela_frame.pack(expand=True, fill="both", padx=100, pady=10)
        self.tabela_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.footer_frame = ctk.CTkFrame(frame, height=60, fg_color="transparent")
        self.footer_frame.pack(fill="x", padx=100, pady=(0, 20))
        
        self.label_saldo = ctk.CTkLabel(self.footer_frame, text="SALDO DO PERÍODO: R$ 0,00", font=("Arial", 20, "bold"))
        self.label_saldo.pack(side="right", padx=10)
        self.lista_titulos.append(self.label_saldo)

    def reset_filtros(self):
        self.f_mes.set("Todos")
        self.f_ano.set("Todos")
        self.f_tipo.set("Todos")
        self.atualizar_categorias_filtro("Todos")

    def construir_graficos(self):
        frame = self.telas["graficos"]
        self.filter_frame_graf = ctk.CTkFrame(frame)
        self.filter_frame_graf.pack(pady=(20, 10), padx=100, fill="x")
        self.filter_frame_graf.grid_columnconfigure((0,1,2,3), weight=1)
        
        for i, (txt, vals) in enumerate(zip(["Mês:", "Ano:"], [["Todos"] + [f"{i:02d}" for i in range(1, 13)], ["Todos"] + [str(a) for a in range(2020, 2031)]])):
            l = ctk.CTkLabel(self.filter_frame_graf, text=txt, font=("Arial", 12, "bold"))
            l.grid(row=0, column=i*2, padx=10, pady=10, sticky="e")
            self.lista_titulos.append(l)
            c = ctk.CTkComboBox(self.filter_frame_graf, values=vals, width=100 if i==0 else 110, command=lambda _: self.atualizar_graficos())
            c.set("Todos")
            c.grid(row=0, column=i*2+1, padx=10, pady=10, sticky="w")
            self.lista_dropdowns.append(c)
            if i==0: self.g_mes = c
            else: self.g_ano = c
        self.canvas_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.canvas_frame.pack(expand=True, fill="both", padx=100, pady=10)

    def atualizar_graficos(self):
        for widget in self.canvas_frame.winfo_children(): widget.destroy()
        df = ler_registros_csv(self.caminho_arquivo_csv)
        if df.empty: 
            l = ctk.CTkLabel(self.canvas_frame, text="Nenhum dado disponível.", font=("Arial", 16))
            l.pack(expand=True)
            self.lista_titulos.append(l)
            return
            
        if self.g_mes.get() != "Todos": df = df[df['Data'].str.split('/').str[1] == self.g_mes.get()]
        if self.g_ano.get() != "Todos": df = df[df['Data'].str.split('/').str[2] == self.g_ano.get()]
        if df.empty: 
            l = ctk.CTkLabel(self.canvas_frame, text="Nenhum dado encontrado.", font=("Arial", 16))
            l.pack(expand=True)
            self.lista_titulos.append(l)
            return
            
        resumo = df.groupby('Tipo')['Valor'].sum()
        labels, valores = resumo.index.tolist(), resumo.values.tolist()
        mapa_cores = {"Gasto": "#ff6b6b", "Ganho": "#51cf66", "Investimento": ("#FF69B4" if self.tema_atual == "rosa" else "#3b8ed0")}
        
        fig, ax = plt.subplots(figsize=(5, 5), facecolor='none')
        ax.pie(valores, autopct='%1.1f%%', startangle=140, colors=[mapa_cores[l] for l in labels], textprops={'color': "white", 'weight': 'bold', 'fontsize': 12}, wedgeprops={'edgecolor': 'none'})
        ax.set_title("Distribuição de Valores", color="white", fontdict={'fontsize': 18, 'weight': 'bold'}, pad=20)
        FigureCanvasTkAgg(fig, master=self.canvas_frame).get_tk_widget().pack(expand=True)
        plt.close(fig)
        
        leg_frame = ctk.CTkFrame(self.canvas_frame, fg_color="transparent")
        leg_frame.pack(pady=(0, 20))
        for l, c, v in zip(labels, [mapa_cores[l] for l in labels], valores):
            it = ctk.CTkFrame(leg_frame, fg_color="transparent")
            it.pack(side="left", padx=20)
            ctk.CTkFrame(it, width=15, height=15, fg_color=c, corner_radius=2).pack(side="left", padx=5)
            lbl = ctk.CTkLabel(it, text=f"{l}: R$ {v:,.2f}", font=("Arial", 13, "bold"))
            lbl.pack(side="left")
            self.lista_titulos.append(lbl)

    def renderizar_cabecalho(self):
        cor_cabecalho = ("#FF69B4", "#C71585") if self.tema_atual == "rosa" else ("#3b8ed0", "#1f6aa5")
        estilo = {"font": ("Arial", 13, "bold"), "height": 45, "text_color": "white", "fg_color": cor_cabecalho}
        for i, t in enumerate(["DATA", "TIPO", "CATEGORIA", "VALOR (R$)"]):
            ctk.CTkLabel(self.tabela_frame, text=t, **estilo).grid(row=0, column=i, padx=1, pady=(0, 2), sticky="nsew")

    def atualizar_tabela(self):
        for widget in self.tabela_frame.winfo_children(): widget.destroy()
        self.renderizar_cabecalho()
        df = ler_registros_csv(self.caminho_arquivo_csv)
        if df.empty:
            self.label_saldo.configure(text="SALDO DO PERÍODO: R$ 0,00", text_color="gray")
            return
            
        if self.f_mes.get() != "Todos": df = df[df['Data'].str.split('/').str[1] == self.f_mes.get()]
        if self.f_ano.get() != "Todos": df = df[df['Data'].str.split('/').str[2] == self.f_ano.get()]
        if self.f_tipo.get() != "Todos": df = df[df['Tipo'] == self.f_tipo.get()]
        if self.f_cat.get() != "Todos": df = df[df['Categoria'] == self.f_cat.get()]
        
        saldo = 0
        for i, row in df.reset_index().iterrows():
            cor_tipo = "#ff6b6b" if row['Tipo'] == "Gasto" else "#51cf66" if row['Tipo'] == "Ganho" else ("#FF69B4" if self.tema_atual == "rosa" else "#3b8ed0")
            saldo += float(row['Valor']) if row['Tipo'] == "Ganho" else -float(row['Valor'])
            ctk.CTkLabel(self.tabela_frame, text=row['Data'], height=40).grid(row=i+1, column=0, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=row['Tipo'].upper(), text_color=cor_tipo, font=("Arial", 11, "bold"), height=40).grid(row=i+1, column=1, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=row['Categoria'], anchor="center", height=40).grid(row=i+1, column=2, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(self.tabela_frame, text=f"R$ {float(row['Valor']):,.2f}", anchor="center", font=("Arial", 12, "bold"), height=40).grid(row=i+1, column=3, padx=1, pady=1, sticky="nsew")
        self.label_saldo.configure(text=f"SALDO DO PERÍODO: R$ {saldo:,.2f}", text_color=("#51cf66" if saldo >= 0 else "#ff6b6b"))

    def mudar_tela(self, nome):
        for f in self.telas.values(): f.pack_forget()
        if nome == "visualizacao": self.atualizar_tabela()
        elif nome == "graficos": self.atualizar_graficos()
        elif nome == "comparativo":
            self.atualizar_comparativo("l")
            self.atualizar_comparativo("r")
        self.telas[nome].pack(expand=True, fill="both")
        cor_ativa = ("#FFB6C1", "#C71585") if self.tema_atual == "rosa" else ("#dbdbdb", "#1f6aa5")
        for n, b in zip(["lancamentos", "visualizacao", "graficos", "comparativo"], [self.btn_lancamentos, self.btn_visualizacao, self.btn_graficos, self.btn_comparativo]):
            b.configure(fg_color=cor_ativa if n == nome else "transparent")

    def atualizar_categorias_filtro(self, tipo):
        self.f_cat.configure(values=["Todos"] + (self.todas_categorias if tipo == "Todos" else self.categorias_opcoes[tipo]))
        self.f_cat.set("Todos")
        self.atualizar_tabela()
        
    def atualizar_categorias_form(self, tipo):
        novas = self.categorias_opcoes[tipo]
        self.dropdown_categoria.configure(values=novas)
        self.dropdown_categoria.set(novas[0])
        
    def coletar_dados_formulario(self):
        tipo, valor, data = self.var_tipo.get(), self.entrada_valor.get().replace(",", "."), f"{self.combo_dia.get()}/{self.combo_mes.get()}/{self.combo_ano.get()}"
        try:
            if float(valor) <= 0: raise ValueError
        except:
            messagebox.showerror("Erro", "Valor inválido!")
            return
        salvar_registro_csv(self.caminho_arquivo_csv, data, tipo, self.dropdown_categoria.get(), valor)
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
