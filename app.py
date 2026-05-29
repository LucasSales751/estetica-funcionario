import streamlit as st
import datetime

st.set_page_config(page_title="Estética Automotiva • Funcionário", page_icon="🚗", layout="centered")

# CSS customizado para visual escuro premium e botões grandes (estilo app de celular)
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #FFFFFF; }
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="number-input"] { 
        background-color: #1E293B !important; 
    }
    input { color: #FFFFFF !important; }
    .stButton>button { 
        background-color: #38BDF8 !important; color: #0F172A !important; 
        font-weight: bold; width: 100%; height: 50px; font-size: 16px;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
    }
    .stExpander { background-color: #1E293B !important; border-radius: 8px; border: 1px solid #334155; }
    </style>
""", unsafe_allow_html=True)

# Conecta ao banco de dados em nuvem global compartilhado
conn = st.connection("postgresql", type="sql")

# ----------------------------------------------------
# MENU EXPLICATIVO DE COMISSÕES (TRANSPARÊNCIA DA EQUIPE)
# ----------------------------------------------------
st.markdown("# 🚗 Portal do Funcionário")
with st.expander("📋 VER TABELA DE PREÇOS E COMISSÕES (DÚVIDAS)"):
    st.markdown("""
    ### 🚿 1. Ducha (Água e Sabão)
    * **Carro Padrão:** Valor: `R$ 10,00` | Sua Comissão: **`R$ 2,50`**
    * **Carro Grande:** Valor: `R$ 20,00` | Sua Comissão: **`R$ 5,00`**
    
    ### 🧽 2. Lavagem Completa (Apenas por Fora)
    * **Carro Padrão:** Valor: `R$ 20,00` | Sua Comissão: **`R$ 5,00`**
    
    ### 🚪 3. Lavagem Apenas Interna
    * **Carro Padrão:** Valor: `R$ 20,00` | Sua Comissão: **`R$ 5,00`**
    
    ### 💎 4. Lavagem Completa (Dentro e Fora)
    * **Carro Padrão:** Valor: `R$ 30,00` | Sua Comissão: **`R$ 10,00`**
    * **Carro Grande (Varia de R$ 40 a R$ 60):**
        * Se o valor cobrado for *até R$ 50,00* $\rightarrow$ Sua Comissão: **`R$ 10,00`**
        * Se o valor cobrado for *maior que R$ 50,00* $\rightarrow$ Sua Comissão: **`R$ 15,00`**
    
    ---
    *Nota: Todos os lançamentos passam pela checagem das câmeras antes de irem para o seu saldo oficial.*
    """)

st.markdown("---")
st.markdown("### 📝 Registrar Novo Serviço")

# ----------------------------------------------------
# FORMULÁRIO DE ENTRADA OPERACIONAL
# ----------------------------------------------------
atendente = st.text_input("Seu Nome:", placeholder="Quem realizou o serviço?").strip()
placa = st.text_input("Placa do Veículo:", placeholder="Ex: ABC1D23 ou ABC1234").strip().upper()

servico_selecionado = st.selectbox(
    "Selecione o Serviço Realizado:",
    [
        "Ducha (Água e Sabão)",
        "Lavagem Completa (Apenas por Fora)",
        "Lavagem Apenas Interna",
        "Lavagem Completa (Dentro e Fora)"
    ]
)

# Lógica de variação por tamanho do veículo e cálculo de valores/comissões
valor_cliente = 0.0
comissao_funcionario = 0.0

if servico_selecionado == "Ducha (Água e Sabão)":
    porte = st.radio("Porte do Veículo:", ["Padrão / Pequeno", "Grande / Maior"], horizontal=True)
    if porte == "Padrão / Pequeno":
        valor_cliente = 10.00
        comissao_funcionario = 2.50
    else:
        valor_cliente = 20.00
        comissao_funcionario = 5.00
        
elif servico_selecionado == "Lavagem Completa (Apenas por Fora)":
    valor_cliente = 20.00
    comissao_funcionario = 5.00
    st.info("ℹ️ Serviço com preço único padrão: R$ 20,00")

elif servico_selecionado == "Lavagem Apenas Interna":
    valor_cliente = 20.00
    comissao_funcionario = 5.00
    st.info("ℹ️ Serviço com preço único padrão: R$ 20,00")

elif servico_selecionado == "Lavagem Completa (Dentro e Fora)":
    porte = st.radio("Porte do Veículo:", ["Padrão / Pequeno", "Grande / Maior"], horizontal=True)
    if porte == "Padrão / Pequeno":
        valor_cliente = 30.00
        comissao_funcionario = 10.00
    else:
        # Libera para digitar o valor combinado (Regra: R$ 40 a R$ 60)
        valor_cliente = st.number_input("Digite o valor cobrado do cliente (R$):", min_value=40.00, max_value=60.00, value=40.00, step=5.00)
        # Regra de comissão baseada na faixa de preço do carro grande
        if valor_cliente > 50.00:
            comissao_funcionario = 15.00
        else:
            comissao_funcionario = 10.00

st.markdown("---")
# Amostragem prévia para o funcionário ver antes de enviar
st.markdown(f"💰 **Valor do Serviço:** `R$ {valor_cliente:.2f}`")
st.markdown(f"📈 **Sua Comissão Estimada:** `R$ {comissao_funcionario:.2f}`")

if st.button("🚀 Enviar para Validação do Patrão"):
    if not atendente or not placa:
        st.error("❌ Erro: Você precisa digitar o seu nome e a placa do veículo para enviar!")
    else:
        agora = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%d/%m/%Y %H:%M")
        
        # Envia os dados estruturados para a tabela de pendentes na nuvem
        with conn.session as session:
            session.execute("""
                INSERT INTO servicos_pendentes (data_hora, atendente, servico, placa, valor, comissao)
                VALUES (:data_hora, :atendente, :servico, :placa, :valor, :comissao);
            """, {
                "data_hora": agora, 
                "atendente": atendente, 
                "servico": f"{servico_selecionado} ({porte if 'porte' in locals() else 'Padrão'})", 
                "placa": placa, 
                "valor": valor_cliente,
                "comissao": comissao_funcionario
            })
            session.commit()
            
        st.success(f"✅ Sucesso! O serviço do veículo {placa} foi para a fila. O patrão vai checar as câmeras para liberar.")
