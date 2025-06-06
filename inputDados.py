import MySQLdb
import streamlit as st

# ➔ Function to connect to MySQL database
def get_connection():
    return MySQLdb.connect(
        host="br1158.hostgator.com.br",
        user="hgroot72_DomJhon",
        passwd="8iaYca6nV8Zaaud%",
        db="hgroot72_base_teste_prodo",
        port=3306
    )

# Connect to DB
conn = get_connection()
cursor = conn.cursor()

st.title("Formulário de Pedido")

# --- DADOS DO CLIENTE --- #
cursor.execute("SELECT nomeCliente FROM Cliente")
clientes = [row[0] for row in cursor.fetchall()]
nome_cliente = st.selectbox("Nome do Cliente", clientes)

# Mostrar dados adicionais do cliente selecionado
if nome_cliente:
    cursor.execute("SELECT cpfCnpjCliente, endCliente, telCliente FROM Cliente WHERE nomeCliente = %s", (nome_cliente,))
    cliente_info = cursor.fetchone()
    if cliente_info:
        cpf, endereco, telefone = cliente_info
        st.markdown(f"**CPF/CNPJ:** {cpf}")
        st.markdown(f"**Endereço:** {endereco}")
        st.markdown(f"**Telefone:** {telefone}")

# Required check (apenas como controle visual)
if not nome_cliente:
    st.warning("Campo 'Nome do Cliente' é obrigatório")

# --- NOME DO VENDEDOR --- #
cursor.execute("SELECT nomeVendedor FROM Vendedor")
vendedores = [row[0] for row in cursor.fetchall()]
nome_vendedor = st.selectbox("Nome do Vendedor", vendedores)

# Mostrar dados adicionais do vendedor selecionado
if nome_vendedor:
    cursor.execute("SELECT localVendedor, telVendedor FROM Vendedor WHERE nomeVendedor = %s", (nome_vendedor,))
    vendedor_info = cursor.fetchone()
    if vendedor_info:
        local, telefone = vendedor_info
        st.markdown(f"**Local:** {local}")
        st.markdown(f"**Telefone:** {telefone}")

# --- PRODUTO --- #
quantidade_total = st.number_input("Quantidade total de produtos", min_value=1, max_value=100, step=1)
mais_de_uma_marca = st.radio("Há mais de uma marca?", ["Não", "Sim"])

num_marcas = 1
if mais_de_uma_marca == "Sim":
    num_marcas = st.selectbox("Quantas marcas?", list(range(1, 17)))

marcas = []
modelos = []
qtdes = []
tamanhos = []
tamanho_quantidades = []
tipos_tamanho = []

cursor.execute("SELECT descMarca FROM Marca")
opcoes_marca = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT descModelo FROM Modelo")
opcoes_modelo = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT descTamanho FROM Tamanho")
opcoes_tamanho = [row[0] for row in cursor.fetchall()]

for i in range(num_marcas):
    st.markdown(f"**Produto {i+1}**")
    marca = st.selectbox(f"Marca {i+1}", opcoes_marca, key=f"marca_{i}")
    modelo = st.selectbox(f"Modelo {i+1}", opcoes_modelo, key=f"modelo_{i}")
    qtde = st.number_input(f"Qtde {i+1}", min_value=1, max_value=100, step=1, key=f"qtde_{i}")
    marcas.append(marca)
    modelos.append(modelo)
    qtdes.append(qtde)

    mais_de_um_tamanho = st.radio(f"Mais de um tamanho para {marca}?", ["Não", "Sim"], key=f"multi_tam_{i}")
    tamanhos_selecionados = []
    quantidades_por_tamanho = []

    if mais_de_um_tamanho == "Sim":
        num_tamanhos = st.selectbox(f"Quantos tamanhos para {marca}?", list(range(1, 17)), key=f"num_tam_{i}")
        for j in range(num_tamanhos):
            tamanho = st.selectbox(f"Tamanho {j+1} - {marca}", opcoes_tamanho, key=f"tam_{i}_{j}")
            qtde_tam = st.number_input(f"Qtde para tamanho {tamanho}", min_value=1, max_value=100, step=1, key=f"qtde_tam_{i}_{j}")
            tamanhos_selecionados.append(tamanho)
            quantidades_por_tamanho.append(qtde_tam)
    else:
        tamanho = st.selectbox(f"Tamanho para {marca}", opcoes_tamanho, key=f"tam_{i}_unico")
        tamanhos_selecionados.append(tamanho)

    tamanhos.append(tamanhos_selecionados)
    tamanho_quantidades.append(quantidades_por_tamanho)

# --- DESENHO --- #
cursor.execute("SELECT descDesenho FROM Desenho")
desenhos = [row[0] for row in cursor.fetchall()]
desenho_escolhido = st.selectbox("Desenho", desenhos)

# --- DOTE, FOGO, MATRÍCULA --- #
dote = fogo = matricula = ""

if st.checkbox("Tem Dote?"):
    dote = st.text_input("Dote")

if st.checkbox("Tem Fogo?"):
    fogo = st.text_input("Fogo")

if st.checkbox("Tem Matrícula?"):
    matricula = st.text_input("Matrícula")

# --- ENVIAR --- #
if st.button("Enviar"):
    try:
        cursor.execute("SELECT MAX(idPedido) FROM Pedido")
        last_id = cursor.fetchone()[0] or 0

        for i in range(num_marcas):
            novo_id = last_id + 1 + i
            st.success(f"Registrado produto {i+1} com ID {novo_id}")
            # Exemplo: fazer INSERT no banco
            # cursor.execute("INSERT INTO Pedido (idPedido, cliente, vendedor, ...) VALUES (%s, %s, ...)", (...))

        conn.commit()
        st.success("Dados enviados com sucesso!")
    except Exception as e:
        st.error(f"Erro ao enviar: {e}")
    finally:
        cursor.close()
        conn.close()
