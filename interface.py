import customtkinter as ctk
import os
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry
import datetime
from banco_de_dados import criar_csv_vazio, salvar_registro_csv

class OrganizadorFinanceiro(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Organizador Financeiro")
        self.geometry("800x600")
        self.caminho_arquivo_csv = ""

        # Dicionário dinâmico de categorias baseadas em planilhas profissionais
        self.categorias_opcoes = {
            "Gasto": ["Alimentação", "Moradia (Aluguel/Parcela)", "Transporte", "Saúde", "Educação", "Lazer/Hobbies", "Assinaturas/Serviços", "Impostos/Taxas", "Outros Gastos"],
            "Ganho": ["Salário", "Freelance/Serviços", "Rendimento de Negócio", "Vendas", "Restituição/Cashback", "Outros Ganhos"],
            "Investimento": ["Tesouro Direto", "CDB / LCI / LCA", "Ações (B3)", "Fundos Imobiliários (FIIs)", "Criptomoedas", "Renda Passiva (Dividendos)", "Reserva de Emergência"]
        }

        # --- Telas (Mantendo a estrutura anterior) ---
        self.frame_inicial = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inicial.pack(expand=True)

        self.label_boas_vindas = ctk.CTkLabel(self.frame_inicial, text="Selecione ou crie um arquivo CSV para começar.", font=("Arial", 14))
        self.label_boas_vindas.pack(pady=10)

        self.botao_selecionar = ctk.CTkButton(self.frame_inicial, text="📁 Selecionar Arquivo", command=self.selecionar_arquivo)
        self.botao_selecionar.pack(pady=10)

        self.botao_criar = ctk.CTkButton(self.frame_inicial, text="➕ Criar Novo CSV", fg_color="green", hover_color="darkgreen", command=self.criar_arquivo)
        self.botao_criar.pack(pady=10)

        # Botão superior direito
        self.botao_alterar_arquivo = ctk.CTkButton(self, text="⚙️ Alterar CSV", width=100, height=30, fg_color="gray", command=self.voltar_tela_inicial)
        
        # Frame Principal (Onde vai o formulário)
        self.frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.label_arquivo_ativo = ctk.CTkLabel(self.frame_principal, text="", text_color="gray")

        # Chama a função que desenha o formulário
        self.construir_formulario()


    def construir_formulario(self):
        """Constrói os campos de entrada de dados dentro do frame principal."""
        
        # Título do Formulário
        self.titulo_form = ctk.CTkLabel(self.frame_principal, text="Novo Lançamento", font=("Arial", 20, "bold"))
        self.titulo_form.pack(pady=(20, 15))

        # 1. Tipo (Gasto, Ganho, Investimento) - Usando SegmentedButton para visual moderno
        self.var_tipo = ctk.StringVar(value="Gasto") # Gasto é o padrão
        self.seletor_tipo = ctk.CTkSegmentedButton(
            self.frame_principal, 
            values=["Gasto", "Ganho", "Investimento"],
            variable=self.var_tipo,
            command=self.atualizar_categorias # Muda as categorias ao clicar
        )
        self.seletor_tipo.pack(pady=10, fill="x")

        # Frame horizontal para organizar Data e Valor lado a lado
        self.frame_linha1 = ctk.CTkFrame(self.frame_principal, fg_color="transparent")
        self.frame_linha1.pack(pady=10, fill="x")

        # 2. Data Picker (usando tkcalendar adaptado)
        self.label_data = ctk.CTkLabel(self.frame_linha1, text="Data:")
        self.label_data.pack(side="left", padx=(0, 5))
        
        # Instanciando o DateEntry com estilo escuro/claro básico
        self.data_picker = DateEntry(
            self.frame_linha1, 
            width=12, 
            background='darkblue', 
            foreground='white', 
            borderwidth=2,
            date_pattern='dd/mm/yyyy' # Padrão brasileiro
        )
        self.data_picker.pack(side="left", padx=(0, 20))

        # 3. Valor
        self.label_valor = ctk.CTkLabel(self.frame_linha1, text="Valor (R$):")
        self.label_valor.pack(side="left", padx=(0, 5))
        
        self.entrada_valor = ctk.CTkEntry(self.frame_linha1, placeholder_text="0.00", width=120)
        self.entrada_valor.pack(side="left")

        # 4. Categoria (Dropdown com Scroll)
        self.label_categoria = ctk.CTkLabel(self.frame_principal, text="Categoria:")
        self.label_categoria.pack(anchor="w", pady=(10, 0))

        # CTKComboBox já possui scroll automático se houver muitos itens
        self.dropdown_categoria = ctk.CTkComboBox(
            self.frame_principal, 
            values=self.categorias_opcoes["Gasto"], # Inicia com os gastos
            width=300
        )
        self.dropdown_categoria.pack(pady=(5, 20), fill="x")

        # 5. Botão de Salvar
        self.botao_salvar = ctk.CTkButton(
            self.frame_principal, 
            text="💾 Adicionar Registro", 
            height=40,
            font=("Arial", 14, "bold"),
            command=self.coletar_dados_formulario
        )
        self.botao_salvar.pack(pady=10, fill="x")


    def atualizar_categorias(self, tipo_selecionado):
        """Atualiza a lista do Dropdown de acordo com o Tipo selecionado."""
        novas_categorias = self.categorias_opcoes[tipo_selecionado]
        
        # Atualiza as opções do menu
        self.dropdown_categoria.configure(values=novas_categorias)
        
        # Muda o texto visível para a primeira opção da nova lista
        self.dropdown_categoria.set(novas_categorias[0])


    def coletar_dados_formulario(self):
        """Pega os valores digitados para enviar ao banco de dados."""
        tipo = self.var_tipo.get()
        data = self.data_picker.get()
        categoria = self.dropdown_categoria.get()
        valor = self.entrada_valor.get()

        # Validação simples para evitar que o usuário salve sem digitar um valor
        if not valor:
            messagebox.showerror("Erro", "Por favor, insira um valor.")
            return

        # Substitui vírgula por ponto para o padrão numérico do Python/CSV
        valor = valor.replace(",", ".")

        print(f"Pronto para salvar -> Data: {data} | Tipo: {tipo} | Categ: {categoria} | Valor: {valor}")
        
        # Salva o registro no arquivo CSV vinculado
        salvar_registro_csv(self.caminho_arquivo_csv, data, tipo, categoria, valor)
        
        # Limpa o campo de valor após salvar
        self.entrada_valor.delete(0, 'end')
        messagebox.showinfo("Sucesso", "Registro adicionado com sucesso!")


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