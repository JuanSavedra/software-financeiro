# Contexto do Projeto: Controle de Finanças Python

Este projeto é uma aplicação desktop simples para controle de finanças pessoais, escrita em Python. Ele utiliza uma interface gráfica moderna e armazena os dados em arquivos CSV locais.

## Visão Geral do Projeto

- **Objetivo:** Registrar receitas, despesas e investimentos em uma planilha CSV.
- **Tecnologias Principais:**
  - **Python 3.x**
  - **CustomTkinter:** Para a interface gráfica moderna (UI).
  - **Pandas:** Para manipulação de dados e arquivos CSV.
  - **tkcalendar:** Para seleção de datas na interface.
- **Arquitetura:**
  - `main.py`: Ponto de entrada da aplicação. Configura o tema e inicia o loop da interface.
  - `interface.py`: Contém a lógica da interface gráfica (`OrganizadorFinanceiro`), incluindo formulários de entrada e gerenciamento de estados de tela.
  - `banco_de_dados.py`: Responsável pela criação e estruturação do arquivo CSV.
  - `graficos.py`: (Em desenvolvimento) Destinado à visualização de dados.

## Comandos Úteis

### Instalação de Dependências
Como não há um arquivo `requirements.txt` explícito, as dependências identificadas são:
```bash
pip install customtkinter pandas tkcalendar
```

### Execução do Projeto
Para iniciar a aplicação:
```bash
python main.py
```

## Convenções de Desenvolvimento

- **Interface:** O projeto utiliza o `customtkinter` com o tema do sistema por padrão.
- **Dados:** O arquivo CSV padrão é o `financas.csv`, mas o usuário pode selecionar ou criar outros. Os arquivos CSV estão ignorados no `.git` para segurança dos dados.
- **Estilo de Código:** Segue o padrão PEP 8 para nomes de funções e variáveis (snake_case). A interface é organizada em classes.

## Próximos Passos
- Implementar a função `salvar_registro_csv` em `banco_de_dados.py`.
- Desenvolver as visualizações gráficas em `graficos.py`.
- Adicionar validações de entrada mais robustas.
