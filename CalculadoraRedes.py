import streamlit as st
import ipaddress
import math
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Calculadora IPv4", page_icon="🌐", layout="centered")

# --- CSS PERSONALIZADO ---
st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 24px;
}
</style>
""", unsafe_allow_html=True)

st.title("Calculadora de Subnetting IPv4")
st.markdown("Ferramenta para cálculo de redes, planeamento VLSM e segmentação.")

# --- BARRA LATERAL (INPUTS) ---
st.sidebar.header("Configuração")

# 1. Input do IP
ip_input = st.sidebar.text_input("Endereço IP Base", value="192.168.0.0")

# 2. Escolha do Modo de Cálculo
modo = st.sidebar.radio(
    "Como queres calcular?",
    ("Por Máscara (CIDR)", "Por Quantidade de Hosts", "Por Quantidade de Redes")
)

cidr_final = 24 # Valor por defeito
qtd_a_listar = 8 # Padrão para a tabela

if modo == "Por Máscara (CIDR)":
    cidr_final = st.sidebar.slider("Máscara (CIDR /xx)", 1, 32, 24)
    qtd_a_listar = st.sidebar.number_input("Quantas redes vizinhas mostrar?", 1, 100, 8)

elif modo == "Por Quantidade de Hosts":
    target_hosts = st.sidebar.number_input("Quantos Hosts precisas?", min_value=1, value=50, step=1)
    qtd_a_listar = st.sidebar.number_input("Quantas redes vizinhas mostrar?", 1, 100, 8)
    
    if target_hosts > 0:
        needed_bits = math.ceil(math.log2(target_hosts + 2))
        if needed_bits < 2: needed_bits = 2 
        
        cidr_calculated = 32 - needed_bits
        
        if cidr_calculated < 0:
            st.sidebar.error("Impossível! Demasiados hosts.")
            cidr_final = None
        else:
            cidr_final = cidr_calculated
            st.sidebar.info(f"ℹ️ Para {target_hosts} hosts, precisas de uma **/{cidr_final}**")

else: 
    # --- NOVO MODO: POR QUANTIDADE DE REDES ---
    st.sidebar.markdown("---")
    st.sidebar.write("Vais dividir uma rede grande em pedaços mais pequenos.")
    
    # Precisamos saber o tamanho original para saber quantos bits roubar
    cidr_origem = st.sidebar.slider("Qual é a Máscara Original?", 1, 31, 24)
    target_subnets = st.sidebar.number_input("Quantas Sub-redes queres criar?", min_value=1, value=4)
    
    # 1. Calcular bits necessários (2^n >= subnets)
    # log2(4) = 2 bits. log2(5) = 2.32 -> ceil -> 3 bits
    bits_borrowed = math.ceil(math.log2(target_subnets))
    
    # 2. Nova máscara
    cidr_calculated = cidr_origem + bits_borrowed
    
    if cidr_calculated > 32:
        st.sidebar.error(f"Impossível dividir uma /{cidr_origem} em {target_subnets} pedaços (Falta espaço).")
        cidr_final = None
    else:
        cidr_final = cidr_calculated
        # Se o utilizador pediu 4 redes, mostramos 4 na tabela. Se pediu 50, mostramos 50.
        qtd_a_listar = target_subnets 
        
        st.sidebar.success(
            f"""
            ✅ **Cálculo de Segmentação:**
            - Bits emprestados: {bits_borrowed}
            - Nova Máscara: **/{cidr_final}**
            """
        )

# --- BOTÃO DE AÇÃO ---
if st.sidebar.button("Calcular Rede"):
    if cidr_final is None:
        st.error("Verifica os parâmetros na barra lateral.")
    else:
        try:
            network_str = f"{ip_input}/{cidr_final}"
            interface = ipaddress.IPv4Interface(network_str)
            network = interface.network 

            # --- RESULTADOS PRINCIPAIS ---
            st.success(f"Rede Calculada: `{network}`")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ID de Rede", str(network.network_address))
            with col2:
                st.metric("Broadcast", str(network.broadcast_address))
            with col3:
                st.metric("Máscara Decimal", str(network.netmask))

            # --- DETALHES ---
            with st.expander("Ver Detalhes Avançados", expanded=True):
                total_hosts = network.num_addresses - 2
                if total_hosts < 0: total_hosts = 0 
                st.write(f"**Hosts por Sub-rede:** `{total_hosts}`")

                if total_hosts > 0:
                    first_host = list(network.hosts())[0]
                    last_host = list(network.hosts())[-1]
                    st.write(f"**Intervalo:** `{first_host}` ➡ `{last_host}`")
                    
                    netmask_parts = str(network.netmask).split('.')
                    wildcard_parts = [str(255 - int(octet)) for octet in netmask_parts]
                    wildcard = ".".join(wildcard_parts)
                    st.code(f"Wildcard Mask: {wildcard}", language="text")

            st.divider()

            # --- TABELA DE REDES DINÂMICA ---
            # Agora usamos a variável 'qtd_a_listar' em vez do fixo 8
            st.subheader(f"Lista das Próximas {qtd_a_listar} Sub-redes")
            
            lista_redes = []
            current_net = network
            
            # Loop dinâmico
            for i in range(qtd_a_listar):
                lista_redes.append({
                    "Sub-rede": str(current_net),
                    "Primeiro IP": str(current_net.network_address + 1) if current_net.prefixlen < 31 else "N/A",
                    "Último IP": str(current_net.broadcast_address - 1) if current_net.prefixlen < 31 else "N/A",
                    "Broadcast": str(current_net.broadcast_address)
                })
                
                # Calcular a próxima
                next_net_int = int(current_net.network_address) + current_net.num_addresses
                if next_net_int > 4294967295: break
                next_net_addr = ipaddress.IPv4Address(next_net_int)
                current_net = ipaddress.IPv4Network(f"{next_net_addr}/{cidr_final}")

            st.dataframe(lista_redes, hide_index=True, use_container_width=True)

        except ValueError:
            st.error("❌ Endereço IP inválido.")
        except Exception as e:
            st.error(f"Erro: {e}")

st.markdown("---")
st.caption("Ferramenta de Estudo CCNA | Desenvolvido em Streamlit")

