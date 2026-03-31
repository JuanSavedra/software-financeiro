import pandas as pd
import os

def criar_csv_vazio(caminho_completo):
    """Cria um arquivo CSV vazio com as colunas base do projeto."""
    
    # Colunas que usaremos para organizar o financeiro
    colunas = ["Data", "Tipo", "Categoria", "Valor"]
    
    # Cria o DataFrame vazio e salva no caminho escolhido
    df = pd.DataFrame(columns=colunas)
    df.to_csv(caminho_completo, index=False)

def salvar_registro_csv(caminho_csv, data, tipo, categoria, valor):
    """Adiciona uma nova linha de registro ao arquivo CSV existente."""
    
    novo_registro = {
        "Data": [data],
        "Tipo": [tipo],
        "Categoria": [categoria],
        "Valor": [float(valor)]
    }
    
    df_novo = pd.DataFrame(novo_registro)
    
    # Verifica se o arquivo está vazio para decidir se escreve o cabeçalho
    arquivo_vazio = not os.path.exists(caminho_csv) or os.stat(caminho_csv).st_size == 0
    
    # Salva anexando (append mode) ao final do arquivo
    df_novo.to_csv(caminho_csv, mode='a', index=False, header=arquivo_vazio)