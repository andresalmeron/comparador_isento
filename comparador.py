import streamlit as st
import pandas as pd
import numpy as np
from datetime import date

# Configuração da Página
st.set_page_config(
    page_title="Comparador de Retorno - Isento vs Tributado",
    page_icon="📉",
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

# --- TÍTULO ---
st.title("💸 Calculadora de Equivalência Fiscal")
st.markdown("Compare **Isentos** (LCI, LCA, CRI, CRA) vs **Tributados** (CDB, LC, Tesouro).")
st.divider()

# --- SIDEBAR ---
st.sidebar.header("🛠️ Menu")
mode = st.sidebar.radio(
    "O que você quer fazer?",
    [
        "1. Comparar dois papéis (Duelo)",
        "2. Converter Isento -> Bruto",
        "3. Converter Bruto -> Isento"
    ]
)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configuração")
rate_type = st.sidebar.selectbox(
    "Tipo de Rentabilidade",
    ["Pós-Fixado (% do CDI)", "Pré-Fixado (% a.a.)", "IPCA+ (% a.a.)"]
)

if rate_type == "IPCA+ (% a.a.)":
    ipca_proj = st.sidebar.number_input(
        "IPCA Projetado (% a.a.)",
        value=4.50, step=0.10, format="%.2f",
        help="O IR incide sobre o retorno total (Taxa + IPCA), por isso a inflação importa."
    ) / 100
else:
    ipca_proj = 0

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
if mode == "1. Comparar dois papéis (Duelo)":
    st.header("🥊 Duelo de Investimentos")
    
    # Toggle para escolher o modo de datas
    tipo_input_duelo = st.radio(
        "Como definir os prazos?",
        ["Selecionar Alíquota de IR (Prazos Iguais/Simples)", "Inserir Datas Específicas (Avançado)"],
        horizontal=True
    )
    st.markdown("---")

    col1, col2 = st.columns(2)

    # --- COLUNA DO ISENTO ---
    with col1:
        st.subheader("🛡️ Isento")
        rate_exempt = st.number_input("Taxa Isenta", value=90.0 if rate_type == "Pós-Fixado (% do CDI)" else 6.0, step=0.1)
        
        if tipo_input_duelo == "Inserir Datas Específicas (Avançado)":
            st.caption("Datas do Papel Isento")
            # ADICIONADO: format="DD/MM/YYYY"
            dt_compra_ex = st.date_input("Compra (Isento)", date.today(), format="DD/MM/YYYY")
            dt_venc_ex = st.date_input("Vencimento (Isento)", date.today().replace(year=date.today().year + 1), format="DD/MM/YYYY")
            
            dias_ex = (dt_venc_ex - dt_compra_ex).days
            if dias_ex <= 0:
                st.error("Data de vencimento deve ser maior que compra.")
            else:
                st.markdown(f"**Prazo:** {dias_ex} dias corridos")

    # --- COLUNA DO TRIBUTADO ---
    with col2:
        st.subheader("🏛️ Tributado")
        rate_gross = st.number_input("Taxa Bruta", value=110.0 if rate_type == "Pós-Fixado (% do CDI)" else 8.0, step=0.1)

        aliquota_ir = 0.15 # Default
        texto_ir = ""

        if tipo_input_duelo == "Inserir Datas Específicas (Avançado)":
            st.caption("Datas do Papel Tributado")
            # ADICIONADO: format="DD/MM/YYYY"
            dt_compra_br = st.date_input("Compra (Tributado)", date.today(), format="DD/MM/YYYY")
            dt_venc_br = st.date_input("Vencimento (Tributado)", date.today().replace(year=date.today().year + 2), format="DD/MM/YYYY")
            
            dias_br = (dt_venc_br - dt_compra_br).days            
            if dias_br <= 0:
                st.error("Data de vencimento deve ser maior que compra.")
            else:
                aliquota_ir, texto_ir = calcular_aliquota_ir(dias_br)
                st.markdown(f"**Prazo:** {dias_br} dias corridos")
                st.markdown(f"**IR Aplicável:** `{texto_ir}`")
        
        else: # Modo Simples
            selected_ir_label = st.selectbox(
                "IR do Investimento Tributado:",
                list(ir_options.keys()),
                index=3
            )
            aliquota_ir = ir_options[selected_ir_label]

    # --- CÁLCULOS ---
    if (tipo_input_duelo == "Inserir Datas Específicas (Avançado)" and ('dias_br' not in locals() or dias_br <= 0)):
        st.warning("Por favor, corrija as datas para prosseguir.")
    else:
        r_exempt = rate_exempt / 100
        r_gross = rate_gross / 100
        
        # Determina a unidade e o cálculo
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

        # --- EXIBIÇÃO DO RESULTADO ---
        st.divider()
        
        val_tributado_liq = net_from_gross * 100 if rate_type != 'IPCA+ (% a.a.)' else net_from_gross
        val_isento = comparison_val_exempt * 100 if rate_type != 'IPCA+ (% a.a.)' else comparison_val_exempt
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(label="Tributado (Líquido)", value=f"{val_tributado_liq:.2f}{unit}")
        with col_res2:
            st.metric(label="Isento (Nominal)", value=f"{val_isento:.2f}{unit}")
            
        diff = val_isento - val_tributado_liq
        
        if diff > 0.01: 
            st.markdown(f"""
            <div class="success-box">
            <h3>🏆 O ISENTO VENCEU!</h3>
            O papel isento rende <b>{abs(diff):.2f} p.p.</b> a mais que este tributado.<br>
            </div>
            """, unsafe_allow_html=True)
        elif diff < -0.01:
            st.markdown(f"""
            <div class="warning-box">
            <h3>⚠️ O TRIBUTADO VENCEU!</h3>
            O papel tributado rende <b>{abs(diff):.2f} p.p.</b> a mais, já descontando IR.<br>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""<div class="info-box"><h3>🤝 EMPATE TÉCNICO</h3>Rentabilidade praticamente idêntica.</div>""", unsafe_allow_html=True)

# ==============================================================================
# MODO 2: ISENTO -> BRUTO
# ==============================================================================
elif mode == "2. Converter Isento -> Bruto":
    st.header("🔄 Tabela de Equivalência")
    st.markdown("Se o **LCI/CRI** paga **X**, quanto o CDB tem que pagar para empatar?")
    
    val_exempt = st.number_input("Taxa Isenta", value=90.0 if rate_type == "Pós-Fixado (% do CDI)" else 6.0, step=0.5)
    
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
            "IR / Prazo": label,
            f"Taxa Bruta Necessária ({rate_type})": f"{display_val:.2f}%"
        })
        
    st.table(pd.DataFrame(results))

# ==============================================================================
# MODO 3: BRUTO -> ISENTO
# ==============================================================================
elif mode == "3. Converter Bruto -> Isento":
    st.header("🔄 Tabela de Equivalência")
    st.markdown("Se o **CDB** paga **Y**, quanto o LCI/CRI tem que pagar para empatar?")
    
    val_gross = st.number_input("Taxa Bruta", value=110.0 if rate_type == "Pós-Fixado (% do CDI)" else 8.0, step=0.5)
    
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
            "IR / Prazo": label,
            f"Taxa Isenta Equivalente ({rate_type})": f"{display_val:.2f}%"
        })
        
    st.table(pd.DataFrame(results))

# --- RODAPÉ ---
st.markdown("---")
st.caption("⚠️ **Atenção:** Cálculos consideram títulos **Bullet**. Dias corridos são usados apenas para definição da alíquota de IR no modo avançado.")
