import customtkinter as ctk
import os
import sys
from interface import OrganizadorFinanceiro

def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, compatível com PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 1. Configuração do Tema
ctk.set_appearance_mode("System") 
ctk.set_default_color_theme(resource_path("pink_theme.json")) 

if __name__ == "__main__":
    # Instancia a interface criada no outro arquivo
    app = OrganizadorFinanceiro()
    
    # Inicia o software
    app.mainloop()