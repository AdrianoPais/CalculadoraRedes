import streamlit as st
import ipaddress
import math
import pandas as pd # Opcional, mas ajuda a fazer tabelas bonitas

# Configuração da Página
st.set_page_config(page_title="Calculadora IPv4", page_icon="", layout="centered")

# --- CSS PERSONALIZADO PARA REDUZIR MÉTRICAS ---
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

# 1. Input do IP (Comum aos dois modos)
ip_input = st.sidebar.text_input("Endereço IP Base", value="192.168.0.0")

# 2. Escolha do Modo de Cálculo
modo = st.sidebar.radio(
    "Como queres calcular?",
    ("Por Máscara (CIDR)", "Por Quantidade de Hosts")
)

cidr_final = 24 # Valor por defeito

if modo == "Por Máscara (CIDR)":
    # Modo Original: Escolhe a /24, /30, etc.
    cidr_final = st.sidebar.slider("Máscara (CIDR /xx)", 1, 32, 24)

else:
    # Novo Modo: Escolhe quantos PCs quer
    target_hosts = st.sidebar.number_input("Quantos Hosts precisas?", min_value=1, value=50, step=1)
    
    if target_hosts > 0:
        # 1. Descobrir quantos bits de host (H) precisamos: 2^H - 2 >= hosts
        needed_bits = math.ceil(math.log2(target_hosts + 2))
        
        if needed_bits < 2: 
            needed_bits = 2 # Mínimo para /30
            
        # 2. Calcular o CIDR: 32 - H
        cidr_calculated = 32 - needed_bits
        
        if cidr_calculated < 0:
            st.sidebar.error("Impossível! Demasiados hosts para IPv4.")
            cidr_final = None
        else:
            cidr_final = cidr_calculated
            
            st.sidebar.info(
                f"""
                ℹ️ **Cálculo Automático:**
                Necessários: {target_hosts} hosts
                Bits de Host (H): {needed_bits}
                Máscara Sugerida: **/{cidr_final}**
                """
            )

# --- BOTÃO DE AÇÃO ---
if st.sidebar.button("Calcular Rede"):
    if cidr_final is None:
        st.error("Por favor ajusta o número de hosts.")
    else:
        try:
            # Cria a rede baseada no IP e no CIDR
            network_str = f"{ip_input}/{cidr_final}"
            interface = ipaddress.IPv4Interface(network_str)
            network = interface.network 

            # --- RESULTADOS PRINCIPAIS ---
            st.success(f"Rede Principal: `{network}`")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("ID de Rede", str(network.network_address))
            with col2:
                st.metric("Broadcast", str(network.broadcast_address))
            with col3:
                st.metric("Máscara Decimal", str(network.netmask))

            # --- DETALHES ---
            with st.expander("Ver Detalhes Avançados (Primeiro/Último IP)", expanded=True):
                total_hosts = network.num_addresses - 2
                if total_hosts < 0: total_hosts = 0 

                st.write(f"**Capacidade Real:** `{total_hosts}` hosts utilizáveis")
                
                if modo == "Por Quantidade de Hosts":
                    desperdicio = total_hosts - target_hosts
                    st.write(f"**Desperdício:** `{desperdicio}` IPs não usados.")

                if total_hosts > 0:
                    first_host = list(network.hosts())[0]
                    last_host = list(network.hosts())[-1]
                    st.write(f"**Intervalo:** `{first_host}`  ➡  `{last_host}`")
                    
                    # Wildcard Mask
                    netmask_parts = str(network.netmask).split('.')
                    wildcard_parts = [str(255 - int(octet)) for octet in netmask_parts]
                    wildcard = ".".join(wildcard_parts)
                    st.code(f"Wildcard Mask (para ACLs): {wildcard}", language="text")

            st.divider()

            # --- NOVIDADE: TABELA DAS PRÓXIMAS 8 REDES ---
            st.subheader("Planeamento de Sub-redes (Sequência)")
            st.markdown(f"Se continuares a dividir a rede em blocos de **/{cidr_final}**, estas são as próximas:")

            lista_redes = []
            current_net = network
            
            # Gerar as próximas 8
            for i in range(8):
                # Guarda os dados desta rede
                lista_redes.append({
                    "Sub-rede": str(current_net),
                    "Primeiro IP": str(current_net.network_address + 1) if current_net.prefixlen < 31 else "N/A",
                    "Último IP": str(current_net.broadcast_address - 1) if current_net.prefixlen < 31 else "N/A",
                    "Broadcast": str(current_net.broadcast_address)
                })
                
                # Calcular a próxima rede matematicamente
                # Converte IP da rede em inteiro, soma o total de IPs da sub-rede, reconverte para IP
                next_net_int = int(current_net.network_address) + current_net.num_addresses
                
                # Proteção contra sair do limite do IPv4 (255.255.255.255)
                if next_net_int > 4294967295:
                    break
                    
                next_net_addr = ipaddress.IPv4Address(next_net_int)
                current_net = ipaddress.IPv4Network(f"{next_net_addr}/{cidr_final}")

            # Mostrar como tabela interativa
            st.dataframe(lista_redes, hide_index=True, use_container_width=True)

        except ValueError:
            st.error("❌ Endereço IP inválido. Verifica o formato (ex: 192.168.1.0).")
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")

# --- Rodapé ---
st.markdown("---")
st.caption("Ferramenta de Estudo CCNA | Desenvolvido em Streamlit")