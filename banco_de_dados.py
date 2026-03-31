import pandas as pd
import os

def criar_csv_vazio(caminho_completo):
    """Cria um arquivo CSV vazio com as colunas base do projeto."""
    
    # Colunas que usaremos para organizar o financeiro
    colunas = ["Data", "Tipo", "Categoria", "Valor"]
    
    # Cria o DataFrame vazio e salva no caminho escolhido
    df = pd.DataFrame(columns=colunas)
    df.to_csv(caminho_completo, index=False)