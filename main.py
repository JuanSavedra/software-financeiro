import customtkinter as ctk

# 1. Configuração do Tema
# Pode ser "System" (segue o Windows), "Dark" ou "Light"
ctk.set_appearance_mode("System") 

# Pode ser "blue" (padrão), "green" ou "dark-blue"
ctk.set_default_color_theme("blue") 

# 2. Criação da Janela Principal
app = ctk.CTk()

# 3. Configurações da Janela
app.title("Organizador Financeiro")
app.geometry("600x400") # Largura x Altura

# 4. Loop Principal (Mantém a janela aberta)
app.mainloop()