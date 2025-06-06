import mysql.connector
import streamlit as st

# ➔ Function to connect to MySQL database
def get_connection():
    return mysql.connector.connect(
        host="br1158.hostgator.com.br",
        user="hgroot72_DomJhon",
        password="8iaYca6nV8Zaaud%",
        database="hgroot72_base_teste_prodo",
        port=3306  # or your actual port
    )

# Connect to DB
conn = get_connection()
cursor = conn.cursor()

st.title("Formulário de Pedido")

# --- DADOS DO CLIENTE --- #
st.markdown("## 🧑‍💼 Dados do Cliente")
st.markdown("---")
cursor.execute("SELECT nomeCliente FROM Cliente")
clientes = [row[0] for row in cursor.fetchall()]
nome_cliente = st.selectbox("### Nome do Cliente", clientes, key="cliente_select")

if nome_cliente:
    cursor.execute("SELECT idCliente, cpfCnpjCliente, endCliente, telCliente FROM Cliente WHERE nomeCliente = %s", (nome_cliente,))
    cliente_info = cursor.fetchone()
    if cliente_info:
        id_cliente, cpf, endereco, telefone = cliente_info
        st.markdown(f"**CPF/CNPJ:** {cpf}")
        st.markdown(f"**Endereço:** {endereco}")
        st.markdown(f"**Telefone:** {telefone}")

# --- NOME DO VENDEDOR --- #
st.markdown("## 🧑‍🔧 Dados do Vendedor")
st.markdown("---")
cursor.execute("SELECT nomeVendedor FROM Vendedor")
vendedores = [row[0] for row in cursor.fetchall()]
nome_vendedor = st.selectbox("### Nome do Vendedor", vendedores, key="vendedor_select")

if nome_vendedor:
    cursor.execute("SELECT idVendedor, localVendedor, telVendedor FROM Vendedor WHERE nomeVendedor = %s", (nome_vendedor,))
    vendedor_info = cursor.fetchone()
    if vendedor_info:
        id_vendedor, local, telefone_vend = vendedor_info
        st.markdown(f"**Local:** {local}")
        st.markdown(f"**Telefone:** {telefone_vend}")

# --- PRODUTOS --- #
st.markdown("## 📦 Produtos")
st.markdown("---")
quantidade_total = st.number_input("### Quantidade total de produtos", min_value=1, max_value=100, step=1)
mais_de_uma_marca = st.radio("Há mais de uma marca?", ["Não", "Sim"])

num_marcas = 1
if mais_de_uma_marca == "Sim":
    num_marcas = st.selectbox("Quantas marcas?", list(range(1, 17)), key="num_marcas_select")

cursor.execute("SELECT idMarca, descMarca FROM Marca")
marcas_opcoes = cursor.fetchall()

cursor.execute("SELECT idModelo, descModelo FROM Modelo")
modelos_opcoes = cursor.fetchall()

cursor.execute("SELECT idTamanho, descTamanho FROM Tamanho")
tamanhos_opcoes = cursor.fetchall()

cursor.execute("SELECT idDesenho, descDesenho FROM Desenho")
desenhos_opcoes = cursor.fetchall()
desenho_dict = {desc: id for id, desc in desenhos_opcoes}
desenho_escolhido = st.selectbox("Desenho", list(desenho_dict.keys()), key="desenho_select")

produtos = []
for i in range(num_marcas):
    with st.expander(f"Produto {i+1}"):
        marca_dict = {desc: id for id, desc in marcas_opcoes}
        modelo_dict = {desc: id for id, desc in modelos_opcoes}
        tamanho_dict = {desc: id for id, desc in tamanhos_opcoes}

        marca = st.selectbox(f"Marca {i+1}", list(marca_dict.keys()), key=f"marca_{i}")
        modelo = st.selectbox(f"Modelo {i+1}", list(modelo_dict.keys()), key=f"modelo_{i}")
        qtde = st.number_input(f"Qtde {i+1}", min_value=1, max_value=100, step=1, key=f"qtde_{i}")

        mais_de_um_tamanho = st.radio(f"Mais de um tamanho para {marca}?", ["Não", "Sim"], key=f"multi_tam_{i}")
        tamanhos_info = []

        if mais_de_um_tamanho == "Sim":
            num_tamanhos = st.selectbox(f"Quantos tamanhos para {marca}?", list(range(1, 17)), key=f"num_tam_{i}")
            for j in range(num_tamanhos):
                tam = st.selectbox(f"Tamanho {j+1} - {marca}", list(tamanho_dict.keys()), key=f"tam_{i}_{j}")
                qtde_tam = st.number_input(f"Qtde para tamanho {tam}", min_value=1, max_value=100, step=1, key=f"qtde_tam_{i}_{j}")
                tamanhos_info.append((tamanho_dict[tam], qtde_tam))
        else:
            tam = st.selectbox(f"Tamanho para {marca}", list(tamanho_dict.keys()), key=f"tam_{i}_unico")
            tamanhos_info.append((tamanho_dict[tam], qtde))

        produtos.append({
            "idMarca": marca_dict[marca],
            "idModelo": modelo_dict[modelo],
            "tamanhos": tamanhos_info,
            "qtde": qtde
        })

# --- CAMPOS OPCIONAIS --- #
st.markdown("## ⚙️ Campos Opcionais")
st.markdown("---")
dote = fogo = matricula = None
if st.checkbox("Ativar campo Dote"):
    dote = st.text_input("Dote", max_chars=70, key="dote_input")
if st.checkbox("Ativar campo Fogo"):
    fogo = st.text_input("Fogo", max_chars=70, key="fogo_input")
if st.checkbox("Ativar campo Matrícula"):
    matricula = st.text_input("Matrícula", max_chars=70, key="matricula_input")

# --- ENVIAR --- #
st.markdown("## ✅ Finalizar Pedido")
st.markdown("---")
if st.button("Enviar"):
    try:
        for produto in produtos:
            for id_tamanho, qtde_tam in produto["tamanhos"]:
                cursor.execute("""
                    INSERT INTO Pneu (IDMarcaPneu, IDmodeloPneu, IDtamanhoPneu, IDdesenhoPneu, dotePneu, fogoPneu, matPneu)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    produto["idMarca"],
                    produto["idModelo"],
                    id_tamanho,
                    desenho_dict[desenho_escolhido],
                    dote, fogo, matricula
                ))
                conn.commit()
                id_pneu = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO OS_Prodo (IDCliente, IDPneu, IDVendedor, quantidadeOS)
                    VALUES (%s, %s, %s, %s)
                """, (
                    id_cliente,
                    id_pneu,
                    id_vendedor,
                    qtde_tam
                ))
                conn.commit()

        st.success("Dados enviados com sucesso!")

    except Exception as e:
        st.error(f"Erro ao enviar: {e}")

    finally:
        cursor.close()
        conn.close()
