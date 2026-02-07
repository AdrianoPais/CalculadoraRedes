# Spider-Net Subnetting Calculator
Calculadora para Segmentação de Redes
Calculadora de Subnetting IPv4

#### Esta é uma ferramenta interativa desenvolvida em Python com a biblioteca Streamlit, desenhada para auxiliar no planeamento e segmentação de redes IPv4. A aplicação permite realizar cálculos baseados em máscaras CIDR, quantidade de hosts necessários ou número de sub-redes pretendidas.

## Funcionalidades

O projeto oferece três modos principais de operação:

- Cálculo por Máscara (CIDR): Introdução direta do prefixo para obter detalhes da rede;
- Cálculo por Quantidade de Hosts: Determina automaticamente a máscara ideal para acomodar um número específico de dispositivos;
- Cálculo por Quantidade de Redes: Divide uma rede principal (rede de origem) em várias sub-redes de tamanho igual.

## Cáculos realizados

Para cada consulta, a aplicação gera:

- Endereço de ID de Rede;
- Endereço de Broadcast;
- Máscara Decimal e Wildcard Mask;
- Intervalo de IPs utilizáveis (Primeiro e Último Host);
- Total de hosts disponíveis;
- Tabela dinâmica com a listagem das próximas sub-redes vizinhas.

## Tecnologias Utilizadas

- Python 3
- Streamlit: Interface web interativa.
- Biblioteca ipaddress: Manipulação e cálculos de endereços IP.
- Pandas: Estruturação e visualização de dados em tabelas.
- Math: Cálculos logarítmicos para determinação de bits de rede.

## Instalação e Execução

Para correr esta aplicação localmente, deves seguir os passos abaixo:

    Clonar o repositório:
    Bash

    git clone https://github.com/AdrianoPais/SpiderNet-Subnetting-Calculator.git
    cd SpiderNet-Subnetting-Calculator

    Instalar as dependências: Certifica-te de que tens o Python instalado e corre:
    Bash

    pip install streamlit pandas

    Executar a aplicação:
    Bash

    streamlit run main.py

## Interface e Usabilidade

A aplicação inclui uma barra lateral de configuração que permite:

    Carregar Exemplos Rápidos: Configurações automáticas para Classes A, B e C privadas.

    Inputs Dinâmicos: Atualização em tempo real conforme a seleção do utilizador.

    Visualização Clara: Uso de métricas e tabelas expansíveis para detalhamento técnico.

## Notas de Desenvolvimento

Este utilitário foi concebido com foco no estudo de redes (CCNA) e na automação de tarefas de administração de sistemas, garantindo precisão nos cálculos de VLSM e segmentação.
