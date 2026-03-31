import customtkinter as ctk
from interface import OrganizadorFinanceiro

# 1. Configuração do Tema
# Pode ser "System" (segue o Windows), "Dark" ou "Light"
ctk.set_appearance_mode("System") 

# Pode ser "blue" (padrão), "green" ou "dark-blue"
ctk.set_default_color_theme("blue") 

if __name__ == "__main__":
    # Instancia a interface criada no outro arquivo
    app = OrganizadorFinanceiro()
    
    # Inicia o software
    app.mainloop()