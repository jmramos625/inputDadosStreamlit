import streamlit as st
import sqlite3
import MySQLdb as mdb

mydb = mdb.connect(
                    host = "brXXXX.hostgator.com.br",
                    user = "XXXX_DomJhon",
                    password = "XXXXXXX",
                    database = "XXXXXXX",
                    port=3306
                )
mycursor = mydb.cursor()

st.markdown("""
    <style>
    /* Estilo geral do container */
    .main {
        background-color: #f5f7fa;
        padding: 20px;
        border-radius: 12px;
        font-family: 'Segoe UI', sans-serif;
        color: #333;
    }

    h1, h2, h3 {
        color: #2c3e50;
    }

    label, .stTextInput label, .stSelectbox label, .stNumberInput label {
        font-weight: bold;
        color: #34495e;
    }

    .stButton > button {
        background-color: #2ecc71;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        transition: background-color 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #27ae60;
    }

    .stSelectbox, .stTextInput, .stNumberInput {
        padding-bottom: 15px;
    }

    .stCheckbox > div {
        margin-top: 10px;
    }

    .stSuccess {
        font-size: 16px;
        font-weight: bold;
        color: #27ae60;
    }

    .block-title {
        margin-top: 25px;
        padding-bottom: 8px;
        border-bottom: 2px solid #3498db;
        font-size: 20px;
    }

    </style>
""", unsafe_allow_html=True)


# Simulando dados vindos do banco de dados
dados_clientes = {
    "João Silva": {"CPF": "123.456.789-00", "Endereço": "Rua A, 123"},
    "Maria Souza": {"CPF": "987.654.321-00", "Endereço": "Av. B, 456"}
}

marcas_disponiveis = ["Marca A", "Marca B", "Marca C"]
modelos_disponiveis = ["Modelo X", "Modelo Y", "Modelo Z"]
tamanhos_disponiveis = ["P", "M", "G", "GG"]
desenhos_disponiveis = ["Desenho 1", "Desenho 2", "Desenho 3"]

tipos_tamanho_disponiveis = {
    "P": "Adulto",
    "M": "Adulto",
    "G": "Adulto",
    "GG": "Adulto",
    "1": "Infantil",
    "2": "Infantil"
}

# --- DADOS DO CLIENTE ---
st.title("Formulário de Pedido")

cliente_nome = st.selectbox("Nome do Cliente", list(dados_clientes.keys()))
cliente_cpf = dados_clientes[cliente_nome]["CPF"]
cliente_endereco = dados_clientes[cliente_nome]["Endereço"]

st.write(f"**CPF:** {cliente_cpf}")
st.write(f"**Endereço:** {cliente_endereco}")

# --- NOME DO VENDEDOR ---
vendedor_nome = st.text_input("Nome do Vendedor *", placeholder="Digite o nome do vendedor")

# --- PRODUTOS ---
st.subheader("Informações do Produto")
quantidade_total = st.number_input("Quantidade total de produtos", min_value=1, max_value=100, step=1)

mais_de_uma_marca = st.radio("Há mais de uma marca?", ["Não", "Sim"])

num_marcas = 1
if mais_de_uma_marca == "Sim":
    num_marcas = st.selectbox("Quantas marcas?", list(range(1, 17)))

produtos = []

for i in range(num_marcas):
    st.markdown(f"### Marca {i+1}")
    marca = st.selectbox(f"Marca {i+1}", marcas_disponiveis, key=f"marca_{i}")
    modelo = st.selectbox(f"Modelo {i+1}", modelos_disponiveis, key=f"modelo_{i}")
    qtde_geral = st.number_input(f"Quantidade total da Marca {i+1}", min_value=1, key=f"qtde_{i}")
    
    mais_de_um_tamanho = st.radio(f"Mais de um tamanho para Marca {i+1}?", ["Não", "Sim"], key=f"multi_tam_{i}")
    
    tamanhos_detalhados = []

    if mais_de_um_tamanho == "Sim":
        num_tamanhos = st.selectbox(f"Quantos tamanhos para Marca {i+1}?", list(range(1, 17)), key=f"tam_count_{i}")
        
        for j in range(num_tamanhos):
            tamanho = st.selectbox(f"Tamanho {j+1} da Marca {i+1}", tamanhos_disponiveis, key=f"tamanho_{i}_{j}")
            tipo_tamanho = tipos_tamanho_disponiveis.get(tamanho, "Desconhecido")
            qtde_tamanho = st.number_input(
                f"Quantidade para Tamanho {tamanho} ({tipo_tamanho})", min_value=1, key=f"qtde_tam_{i}_{j}"
            )
            
            tamanhos_detalhados.append({
                "tamanho": tamanho,
                "tipo": tipo_tamanho,
                "quantidade": qtde_tamanho
            })
    
    else:
        tamanho_unico = st.selectbox(f"Tamanho da Marca {i+1}", tamanhos_disponiveis, key=f"tamanho_unico_{i}")
        tipo_tamanho = tipos_tamanho_disponiveis.get(tamanho_unico, "Desconhecido")
        tamanhos_detalhados.append({
            "tamanho": tamanho_unico,
            "tipo": tipo_tamanho,
            "quantidade": qtde_geral  # Usa a quantidade total da marca
        })

    produtos.append({
        "marca": marca,
        "modelo": modelo,
        "quantidade_total": qtde_geral,
        "tamanhos": tamanhos_detalhados
    })

# --- DESENHO ---
desenho = st.selectbox("Desenho", desenhos_disponiveis)

# --- CAMPOS OPCIONAIS COM CHECKBOX ---
st.subheader("Informações Adicionais")

ativar_dote = st.checkbox("Tem Dote?")
dote = st.text_input("Dote", disabled=not ativar_dote)

ativar_fogo = st.checkbox("Tem Fogo?")
fogo = st.text_input("Fogo", disabled=not ativar_fogo)

ativar_matricula = st.checkbox("Tem Matrícula?")
matricula = st.text_input("Matrícula", disabled=not ativar_matricula)

# Simulação do último ID no banco:
last_id_from_db = 34

# --- BOTÃO DE ENVIO ---
if st.button("Enviar"):
    novo_id = last_id_from_db
    linhas_para_salvar = []

    for produto in produtos:
        novo_id += 1  # Incrementa ID para cada marca

        linha = {
            "id": novo_id,
            "marca": produto["marca"],
            "modelo": produto["modelo"],
            "quantidade_total": produto["quantidade_total"],
            "tamanhos": produto["tamanhos"]
        }

        linhas_para_salvar.append(linha)

        # Aqui você faria o insert no banco de dados:
        # inserir_linha_no_banco(linha)

    st.success(f"{len(linhas_para_salvar)} linhas foram enviadas com sucesso ao banco de dados.")
    st.json(linhas_para_salvar)  # Apenas para debug visual

