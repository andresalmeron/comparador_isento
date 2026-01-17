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
st.markdown("### Simulador de Rentabilidade Líquida (Isento vs Tributado)")
st.divider()

# --- SIDEBAR ---
st.sidebar.header("🛠️ Menu")
mode = st.sidebar.radio(
    "O que você deseja fazer?",
    [
        "1. Comparar em Reais (R$)",
        "2. Comparar em Taxas (%)",
        "3. Quanto um CDB precisa pagar para empatar?",
        "4. Qual o rendimento 'limpo' deste CDB?"
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
    # A projeção do CDI só aparece se estivermos no Modo 1 (Cálculo Financeiro)
    if mode == "1. Comparar em Reais (R$)":
        cdi_proj = st.sidebar.number_input(
            "CDI Médio Projetado (% a.a.)",
            value=11.25, step=0.10, format="%.2f",
            help="Necessário para calcular o valor financeiro final."
        ) / 100
    else:
        cdi_proj = 0.0 # Não relevante para comparação de taxas puras

# Dicionário de Alíquotas para modo simples
ir_options = {
    "Até 6 meses (22,5%)": 0.225,
    "De 6 meses a 1 ano (20,0%)": 0.20,
    "De 1 a 2 anos (17,5%)": 0.175,
    "Acima de 2 anos (15,0%)": 0.15
}

# ==============================================================================
# MODO 1: COMPARAR EM REAIS (R$)
# ==============================================================================
if mode == "1. Comparar em Reais (R$)":
    st.header("💵 Duelo Financeiro")
    st.info("Simule o resultado final na conta do cliente.")
    
    valor_investido = st.number_input("Valor do Investimento (R$)", value=100000.0, step=1000.0, format="%.2f")
    st.markdown("---")
    
    tipo_input_duelo = st.radio(
        "Definição de Prazo:",
        ["Modo Simples (Selecionar Meses/IR)", "Modo Avançado (Datas Exatas)"],
        horizontal=True,
        key="radio_reais"
    )
    
    time_years = 1.0 
    aliquota_ir = 0.15
    
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🛡️ Isento")
        label_isento = "Taxa (% do CDI)" if rate_type == "Pós-Fixado (% do CDI)" else "Taxa (% a.a.)"
        rate_exempt = st.number_input(label_isento, value=90.0 if rate_type == "Pós-Fixado (% do CDI)" else 6.0, step=0.1, key="rate_ex_reais")
        
        if tipo_input_duelo == "Modo Avançado (Datas Exatas)":
            dt_compra_ex = st.date_input("Compra (Isento)", date.today(), format="DD/MM/YYYY", key="dt_c_ex_reais")
            dt_venc_ex = st.date_input("Vencimento (Isento)", date.today().replace(year=date.today().year + 1), format="DD/MM/YYYY", key="dt_v_ex_reais")
            dias_ex = (dt_venc_ex - dt_compra_ex).days
            if dias_ex > 0: st.caption(f"Prazo: {dias_ex} dias")

    with col2:
        st.subheader("🏛️ Tributado")
        label_bruto = "Taxa (% do CDI)" if rate_type == "Pós-Fixado (% do CDI)" else "Taxa (% a.a.)"
        rate_gross = st.number_input(label_bruto, value=110.0 if rate_type == "Pós-Fixado (% do CDI)" else 8.0, step=0.1, key="rate_br_reais")

        if tipo_input_duelo == "Modo Avançado (Datas Exatas)":
            dt_compra_br = st.date_input("Compra (Tributado)", date.today(), format="DD/MM/YYYY", key="dt_c_br_reais")
            dt_venc_br = st.date_input("Vencimento (Tributado)", date.today().replace(year=date.today().year + 2), format="DD/MM/YYYY", key="dt_v_br_reais")
            dias_br = (dt_venc_br - dt_compra_br).days
            if dias_br <= 0:
                st.error("Vencimento deve ser maior que compra.")
            else:
                aliquota_ir, texto_ir = calcular_aliquota_ir(dias_br)
                time_years = dias_br / 365.0
                st.markdown(f"**IR Aplicável:** `{texto_ir}`")
        else:
            prazo_meses = st.number_input("Prazo (Meses)", min_value=1, value=24, step=1, key="prazo_reais")
            time_years = prazo_meses / 12.0
            dias_estimados = prazo_meses * 30
            aliquota_ir, texto_ir = calcular_aliquota_ir(dias_estimados)
            st.caption(f"IR Estimado: {texto_ir}")

    # Cálculos Financeiros
    if time_years > 0:
        r_exempt = rate_exempt / 100
        r_gross = rate_gross / 100
        
        if rate_type == "Pós-Fixado (% do CDI)":
            annual_gross = (1 + cdi_proj * r_gross) - 1
            annual_exempt = (1 + cdi_proj * r_exempt) - 1
        elif rate_type == "Pré-Fixado (% a.a.)":
            annual_gross = r_gross
            annual_exempt = r_exempt
        else: # IPCA+
            annual_gross = (1 + ipca_proj) * (1 + r_gross) - 1
            annual_exempt = (1 + ipca_proj) * (1 + r_exempt) - 1

        final_gross_tributado = valor_investido * ((1 + annual_gross) ** time_years)
        final_gross_isento = valor_investido * ((1 + annual_exempt) ** time_years)
        
        profit_gross_tributado = final_gross_tributado - valor_investido
        ir_tributado = profit_gross_tributado * aliquota_ir
        
        final_net_tributado = final_gross_tributado - ir_tributado
        final_net_isento = final_gross_isento # Isento

        st.divider()
        st.subheader("Projeção de Resgate Líquido")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.markdown(f"### 🛡️ Isento: {format_currency(final_net_isento)}")
        with col_res2:
            st.markdown(f"### 🏛️ Tributado: {format_currency(final_net_tributado)}")
            st.caption(f"(Já descontando {format_currency(ir_tributado)} de IR)")

        diff = final_net_isento - final_net_tributado
        if diff > 1.0:
            st.markdown(f"""<div class="success-box"><h3>🏆 O ISENTO VENCEU!</h3>Lucro extra de <b>{format_currency(diff)}</b> no bolso.</div>""", unsafe_allow_html=True)
        elif diff < -1.0:
            st.markdown(f"""<div class="warning-box"><h3>⚠️ O TRIBUTADO VENCEU!</h3>Lucro extra de <b>{format_currency(abs(diff))}</b> no bolso.</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="info-box"><h3>🤝 EMPATE FINANCEIRO</h3></div>""", unsafe_allow_html=True)

# ==============================================================================
# MODO 2: COMPARAR EM TAXAS (%)
# ==============================================================================
elif mode == "2. Comparar em Taxas (%)":
    st.header("📊 Duelo de Taxas")
    st.info("Compare a eficiência dos ativos percentualmente (Rentabilidade Líquida).")
    
    tipo_input_duelo = st.radio(
        "Definição de IR:",
        ["Selecionar Faixa de IR", "Calcular por Datas"],
        horizontal=True,
        key="radio_taxas"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛡️ Isento")
        rate_exempt = st.number_input("Taxa Nominal", value=90.0 if rate_type == "Pós-Fixado (% do CDI)" else 6.0, step=0.1, key="rate_ex_taxas")
        
        if tipo_input_duelo == "Calcular por Datas":
            dt_compra_ex = st.date_input("Compra", date.today(), format="DD/MM/YYYY", key="dt_c_ex_taxas")
            dt_venc_ex = st.date_input("Vencimento", date.today().replace(year=date.today().year + 1), format="DD/MM/YYYY", key="dt_v_ex_taxas")
            dias_ex = (dt_venc_ex - dt_compra_ex).days
            if dias_ex > 0: st.caption(f"Prazo: {dias_ex} dias")
            else: st.error("Data inválida")
    
    with col2:
        st.subheader("🏛️ Tributado")
        rate_gross = st.number_input("Taxa Bruta", value=110.0 if rate_type == "Pós-Fixado (% do CDI)" else 8.0, step=0.1, key="rate_br_taxas")
        
        if tipo_input_duelo == "Calcular por Datas":
            dt_compra_br = st.date_input("Compra", date.today(), format="DD/MM/YYYY", key="dt_c_taxas")
            dt_venc_br = st.date_input("Vencimento", date.today().replace(year=date.today().year + 2), format="DD/MM/YYYY", key="dt_v_taxas")
            dias_br = (dt_venc_br - dt_compra_br).days
            if dias_br <= 0: st.error("Data inválida")
            else:
                aliquota_ir, texto_ir = calcular_aliquota_ir(dias_br)
                st.markdown(f"**IR:** `{texto_ir}`")
        else:
            selected_ir_label = st.selectbox("Faixa de IR:", list(ir_options.keys()), index=3, key="sel_ir_taxas")
            aliquota_ir = ir_options[selected_ir_label]

    # Cálculos de Taxa
    r_exempt = rate_exempt / 100
    r_gross = rate_gross / 100
    unit = ""
    
    if rate_type == "Pós-Fixado (% do CDI)":
        net_from_gross = r_gross * (1 - aliquota_ir)
        comparison_val_exempt = r_exempt
        unit = "% do CDI"
    elif rate_type == "Pré-Fixado (% a.a.)":
        net_from_gross = r_gross * (1 - aliquota_ir)
        comparison_val_exempt = r_exempt
        unit = "% a.a."
    else: # IPCA+
        gross_total_yield = (1 + ipca_proj) * (1 + r_gross) - 1
        net_total_yield = gross_total_yield * (1 - aliquota_ir)
        spread_net_from_gross = ((net_total_yield + 1) / (1 + ipca_proj)) - 1
        net_from_gross = spread_net_from_gross * 100 
        comparison_val_exempt = r_exempt 
        unit = "% + IPCA"
        rate_gross = rate_gross # Ajuste apenas para display se necessario, mas logica esta acima

    st.divider()
    val_tributado_liq = net_from_gross * 100 if rate_type != 'IPCA+ (% a.a.)' else net_from_gross
    val_isento = comparison_val_exempt * 100 if rate_type != 'IPCA+ (% a.a.)' else comparison_val_exempt
    
    c1, c2 = st.columns(2)
    c1.metric("Isento (Nominal)", f"{val_isento:.2f}{unit}")
    c2.metric("Tributado (Líquido)", f"{val_tributado_liq:.2f}{unit}")
    
    diff = val_isento - val_tributado_liq
    if diff > 0.01:
        st.markdown(f"""<div class="success-box"><h3>🏆 O ISENTO VENCEU!</h3>Vantagem de <b>{abs(diff):.2f} p.p.</b> em rentabilidade.</div>""", unsafe_allow_html=True)
    elif diff < -0.01:
        st.markdown(f"""<div class="warning-box"><h3>⚠️ O TRIBUTADO VENCEU!</h3>Vantagem de <b>{abs(diff):.2f} p.p.</b> líquidos.</div>""", unsafe_allow_html=True)
    else:
        st.info("Empate Técnico na taxa.")

# ==============================================================================
# MODO 3: ISENTO -> BRUTO
# ==============================================================================
elif mode == "3. Quanto um CDB precisa pagar para empatar?":
    st.header("🔄 Tabela de Equivalência")
    val_exempt = st.number_input("Quanto o Isento paga?", value=90.0 if rate_type == "Pós-Fixado (% do CDI)" else 6.0, step=0.5, key="eq_isent")
    
    results = []
    for label, ir in ir_options.items():
        r_ex = val_exempt / 100
        if rate_type == "Pós-Fixado (% do CDI)" or rate_type == "Pré-Fixado (% a.a.)":
            equiv_gross = r_ex / (1 - ir)
            display_val = equiv_gross * 100
        else: 
            net_total = (1 + ipca_proj)*(1 + r_ex) - 1
            gross_total = net_total / (1 - ir)
            gross_spread = ((gross_total + 1) / (1 + ipca_proj)) - 1
            display_val = gross_spread * 100
        results.append({"Prazo / IR": label, f"Taxa Bruta Necessária ({rate_type})": f"{display_val:.2f}%"})
    st.table(pd.DataFrame(results))

# ==============================================================================
# MODO 4: BRUTO -> ISENTO
# ==============================================================================
elif mode == "4. Qual o rendimento 'limpo' deste CDB?":
    st.header("🔄 Tabela de Equivalência")
    val_gross = st.number_input("Quanto o CDB paga?", value=110.0 if rate_type == "Pós-Fixado (% do CDI)" else 8.0, step=0.5, key="eq_bruto")
    
    results = []
    for label, ir in ir_options.items():
        r_gr = val_gross / 100
        if rate_type == "Pós-Fixado (% do CDI)" or rate_type == "Pré-Fixado (% a.a.)":
            equiv_exempt = r_gr * (1 - ir)
            display_val = equiv_exempt * 100
        else: 
            gross_total = (1 + ipca_proj)*(1 + r_gr) - 1
            net_total = gross_total * (1 - ir)
            exempt_spread = ((net_total + 1) / (1 + ipca_proj)) - 1
            display_val = exempt_spread * 100
        results.append({"Prazo / IR": label, f"Taxa Isenta Equivalente ({rate_type})": f"{display_val:.2f}%"})
    st.table(pd.DataFrame(results))

# --- RODAPÉ ---
st.markdown("---")
st.caption("⚠️ **Aviso:** Cálculos consideram títulos **Bullet** (sem cupom periódico). Em títulos IPCA+, a tributação incide sobre o retorno total (IPCA + Juros).")
