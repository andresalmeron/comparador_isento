import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

# Configuração da Página
st.set_page_config(
    page_title="Simulador de Rentabilidade Real",
    page_icon="💰",
    layout="centered"
)

# --- ESTILIZAÇÃO CSS ---
st.markdown("""
    <style>
    .big-font { font-size:20px !important; font-weight: bold; }
    .success-box {
        padding: 15px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        text-align: center;
    }
    .warning-box {
        padding: 15px;
        background-color: #fff3cd;
        color: #856404;
        border-radius: 8px;
        border: 1px solid #ffeeba;
        text-align: center;
    }
    .info-box {
        padding: 15px;
        background-color: #d1ecf1;
        color: #0c5460;
        border-radius: 8px;
        border: 1px solid #bee5eb;
        text-align: center;
    }
    .metric-label {
        font-size: 14px;
        color: #555;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def calcular_aliquota_ir(dias):
    """Retorna a alíquota decimal e o texto da faixa."""
    if dias <= 180:
        return 0.225, "22,5% (Até 6 meses)"
    elif dias <= 360:
        return 0.20, "20,0% (6 a 12 meses)"
    elif dias <= 720:
        return 0.175, "17,5% (1 a 2 anos)"
    else:
        return 0.15, "15,0% (Acima de 2 anos)"

def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- TÍTULO ---
st.title("💰 Onde seu dinheiro rende mais?")
st.markdown("### Descubra qual investimento coloca mais grana no seu bolso, já descontando o imposto.")
st.divider()

# --- SIDEBAR ---
st.sidebar.header("🛠️ Menu")
mode = st.sidebar.radio(
    "O que você deseja fazer?",
    [
        "1. Comparar dois investimentos (Duelo)",
        "2. Quanto um CDB precisa pagar para empatar?",
        "3. Qual o rendimento 'limpo' deste CDB?"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuração de Mercado")

rate_type = st.sidebar.selectbox(
    "Tipo de Rentabilidade",
    ["Pós-Fixado (% do CDI)", "Pré-Fixado (% a.a.)", "IPCA+ (% a.a.)"]
)

# Configurações globais de projeção
ipca_proj = 0.0
cdi_proj = 0.0

if rate_type == "IPCA+ (% a.a.)":
    ipca_proj = st.sidebar.number_input(
        "IPCA Projetado (% a.a.)",
        value=4.50, step=0.10, format="%.2f",
        help="Essencial para calcular o IR sobre a inflação."
    ) / 100
elif rate_type == "Pós-Fixado (% do CDI)":
    cdi_proj = st.sidebar.number_input(
        "CDI Médio Projetado (% a.a.)",
        value=11.25, step=0.10, format="%.2f",
        help="Necessário para calcular o valor financeiro final em Reais."
    ) / 100

# Dicionário de Alíquotas para o modo simples
ir_options = {
    "Até 6 meses (22,5%)": 0.225,
    "De 6 meses a 1 ano (20,0%)": 0.20,
    "De 1 a 2 anos (17,5%)": 0.175,
    "Acima de 2 anos (15,0%)": 0.15
}

# ==============================================================================
# MODO 1: DUELO (COMPARADOR)
# ==============================================================================
if mode == "1. Comparar dois investimentos (Duelo)":
    st.header("🥊 Quem paga mais no final?")
    st.info("Compare dois papéis e veja qual deles realmente engorda sua conta.")
    
    # --- INPUT DO VALOR FINANCEIRO ---
    valor_investido = st.number_input("Valor do Investimento (R$)", value=100000.0, step=1000.0, format="%.2f")
    st.markdown("---")
    
    # Toggle para escolher o modo de datas
    tipo_input_duelo = st.radio(
        "Como definir os prazos?",
        ["Modo Simples (Definir Meses/IR)", "Modo Avançado (Datas Exatas)"],
        horizontal=True
    )
    
    # Variáveis de controle de tempo (Anos decimais para cálculo de juros compostos)
    time_years = 1.0 
    aliquota_ir = 0.15
    
    col1, col2 = st.columns(2)

    # --- COLUNA DO ISENTO ---
    with col1:
        st.subheader("🛡️ Isento")
        label_isento = "Quanto o Isento paga? (% do CDI)" if rate_type == "Pós-Fixado (% do CDI)" else "Quanto o Isento paga? (% a.a.)"
        rate_exempt = st.number_input(label_isento, value=90.0 if rate_type == "Pós-Fixado (% do CDI)" else 6.0, step=0.1)
        
        if tipo_input_duelo == "Modo Avançado (Datas Exatas)":
            dt_compra_ex = st.date_input("Compra (Isento)", date.today(), format="DD/MM/YYYY")
            dt_venc_ex = st.date_input("Vencimento (Isento)", date.today().replace(year=date.today().year + 1), format="DD/MM/YYYY")
            dias_ex = (dt_venc_ex - dt_compra_ex).days
            if dias_ex > 0:
                st.caption(f"Prazo: {dias_ex} dias")

    # --- COLUNA DO TRIBUTADO ---
    with col2:
        st.subheader("🏛️ Tributado")
        label_bruto = "Quanto o CDB paga? (% do CDI)" if rate_type == "Pós-Fixado (% do CDI)" else "Quanto o CDB paga? (% a.a.)"
        rate_gross = st.number_input(label_bruto, value=110.0 if rate_type == "Pós-Fixado (% do CDI)" else 8.0, step=0.1)

        if tipo_input_duelo == "Modo Avançado (Datas Exatas)":
            dt_compra_br = st.date_input("Compra (Tributado)", date.today(), format="DD/MM/YYYY")
            dt_venc_br = st.date_input("Vencimento (Tributado)", date.today().replace(year=date.today().year + 2), format="DD/MM/YYYY")
            dias_br = (dt_venc_br - dt_compra_br).days
            
            if dias_br <= 0:
                st.error("Vencimento deve ser maior que compra.")
            else:
                aliquota_ir, texto_ir = calcular_aliquota_ir(dias_br)
                time_years = dias_br / 365.0
                st.markdown(f"**IR Aplicável:** `{texto_ir}`")
        
        else: # Modo Simples
            prazo_meses = st.number_input("Prazo da Aplicação (Meses)", min_value=1, value=24, step=1)
            time_years = prazo_meses / 12.0
            dias_estimados = prazo_meses * 30
            aliquota_ir, texto_ir = calcular_aliquota_ir(dias_estimados)
            st.caption(f"IR Estimado: {texto_ir}")

    # --- CÁLCULOS FINANCEIROS ---
    if time_years > 0:
        r_exempt = rate_exempt / 100
        r_gross = rate_gross / 100
        
        # 1. Definir Taxa Anual Efetiva Bruta
        if rate_type == "Pós-Fixado (% do CDI)":
            # Taxa Anual = (1 + CDI*Percent)^1 - 1
            annual_gross = (1 + cdi_proj * r_gross) - 1
            annual_exempt = (1 + cdi_proj * r_exempt) - 1
            
        elif rate_type == "Pré-Fixado (% a.a.)":
            annual_gross = r_gross
            annual_exempt = r_exempt
            
        else: # IPCA+
            # Taxa Anual = (1 + IPCA) * (1 + TaxaFixa) - 1
            annual_gross = (1 + ipca_proj) * (1 + r_gross) - 1
            annual_exempt = (1 + ipca_proj) * (1 + r_exempt) - 1

        # 2. Calcular Montante Final Bruto (Compound Interest)
        # FV = PV * (1 + i)^n
        final_gross_tributado = valor_investido * ((1 + annual_gross) ** time_years)
        final_gross_isento = valor_investido * ((1 + annual_exempt) ** time_years)
        
        # 3. Calcular Rendimento Bruto
        profit_gross_tributado = final_gross_tributado - valor_investido
        profit_gross_isento = final_gross_isento - valor_investido
        
        # 4. Calcular IR
        ir_tributado = profit_gross_tributado * aliquota_ir
        ir_isento = 0.0 # Isento
        
        # 5. Calcular Líquido Final
        net_tributado = profit_gross_tributado - ir_tributado
        net_isento = profit_gross_isento
        
        final_net_tributado = valor_investido + net_tributado
        final_net_isento = valor_investido + net_isento

        # --- EXIBIÇÃO DO RESULTADO ---
        st.divider()
        st.subheader("💵 Resultado Financeiro (Projeção)")
        
        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.markdown("### 🛡️ ISENTO")
            st.markdown(f"**Resgate Final:** `{format_currency(final_net_isento)}`")
            st.markdown(f"Rendimento Líquido: {format_currency(net_isento)}")
            st.markdown(f"IR Pago: R$ 0,00")
            
        with res_col2:
            st.markdown("### 🏛️ TRIBUTADO")
            st.markdown(f"**Resgate Líquido:** `{format_currency(final_net_tributado)}`")
            st.markdown(f"Rendimento Líquido: {format_currency(net_tributado)}")
            st.markdown(f"IR Pago: {format_currency(ir_tributado)}")

        st.divider()
        diff = final_net_isento - final_net_tributado
        
        if diff > 1.0: 
            st.markdown(f"""
            <div class="success-box">
            <h3>🏆 O ISENTO É MELHOR!</h3>
            Você coloca <b>{format_currency(diff)}</b> a mais no bolso com o isento.
            </div>
            """, unsafe_allow_html=True)
        elif diff < -1.0:
            st.markdown(f"""
            <div class="warning-box">
            <h3>⚠️ O TRIBUTADO VALE MAIS!</h3>
            Mesmo pagando <b>{format_currency(ir_tributado)}</b> de imposto, <br>
            o tributado ainda te dá <b>{format_currency(abs(diff))}</b> a mais de lucro.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""<div class="info-box"><h3>🤝 EMPATE TÉCNICO</h3>O resultado financeiro é praticamente idêntico.</div>""", unsafe_allow_html=True)

# ==============================================================================
# MODO 2: ISENTO -> BRUTO (Mantido similar, focado em taxa)
# ==============================================================================
elif mode == "2. Quanto um CDB precisa pagar para empatar?":
    st.header("🔄 Tabela de Equivalência")
    st.markdown("Se o **LCI/CRI** paga **X**, quanto o CDB tem que pagar para empatar?")
    
    val_exempt = st.number_input("Quanto o Isento paga?", value=90.0 if rate_type == "Pós-Fixado (% do CDI)" else 6.0, step=0.5)
    
    results = []
    
    for label, ir in ir_options.items():
        r_ex = val_exempt / 100
        
        if rate_type == "Pós-Fixado (% do CDI)" or rate_type == "Pré-Fixado (% a.a.)":
            equiv_gross = r_ex / (1 - ir)
            display_val = equiv_gross * 100
        else: # IPCA
            net_total = (1 + ipca_proj)*(1 + r_ex) - 1
            gross_total = net_total / (1 - ir)
            gross_spread = ((gross_total + 1) / (1 + ipca_proj)) - 1
            display_val = gross_spread * 100
            
        results.append({
            "Prazo / IR": label,
            f"Taxa Bruta Necessária ({rate_type})": f"{display_val:.2f}%"
        })
        
    st.table(pd.DataFrame(results))

# ==============================================================================
# MODO 3: BRUTO -> ISENTO
# ==============================================================================
elif mode == "3. Qual o rendimento 'limpo' deste CDB?":
    st.header("🔄 Tabela de Equivalência")
    st.markdown("Se o **CDB** paga **Y**, quanto o LCI/CRI tem que pagar para empatar?")
    
    val_gross = st.number_input("Quanto o CDB paga?", value=110.0 if rate_type == "Pós-Fixado (% do CDI)" else 8.0, step=0.5)
    
    results = []
    
    for label, ir in ir_options.items():
        r_gr = val_gross / 100
        
        if rate_type == "Pós-Fixado (% do CDI)" or rate_type == "Pré-Fixado (% a.a.)":
            equiv_exempt = r_gr * (1 - ir)
            display_val = equiv_exempt * 100
        else: # IPCA
            gross_total = (1 + ipca_proj)*(1 + r_gr) - 1
            net_total = gross_total * (1 - ir)
            exempt_spread = ((net_total + 1) / (1 + ipca_proj)) - 1
            display_val = exempt_spread * 100
            
        results.append({
            "Prazo / IR": label,
            f"Taxa Isenta Equivalente ({rate_type})": f"{display_val:.2f}%"
        })
        
    st.table(pd.DataFrame(results))
