import streamlit as st
import pandas as pd
import numpy as np

# Configuração da Página
st.set_page_config(
    page_title="Calculadora Gekko de Isenção",
    page_icon="💸",
    layout="centered"
)

# --- ESTILIZAÇÃO CSS (Para deixar mais 'pedagógico' e visual) ---
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .success-box {
        padding: 10px;
        background-color: #d4edda;
        color: #155724;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        padding: 10px;
        background-color: #fff3cd;
        color: #856404;
        border-radius: 5px;
        border: 1px solid #ffeeba;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TÍTULO E INTRODUÇÃO ---
st.title("💸 Calculadora de Equivalência Fiscal")
st.markdown("""
**Objetivo:** Comparar investimentos **Isentos de IR** (LCI, LCA, CRI, CRA, Debêntures Inc.) contra investimentos **Tributados** (CDB, LC, Tesouro, Debêntures Comuns), considerando a tabela regressiva de IR.
""")
st.divider()

# --- FUNÇÕES AUXILIARES ---

def get_ir_aliquot(days):
    """Retorna a alíquota de IR baseada no prazo em dias."""
    if days <= 180:
        return 0.225
    elif days <= 360:
        return 0.20
    elif days <= 720:
        return 0.175
    else:
        return 0.15

def format_percent(val):
    return f"{val:.2f}%"

# --- SIDEBAR DE NAVEGAÇÃO ---
st.sidebar.header("🛠️ Ferramentas")
mode = st.sidebar.radio(
    "O que você quer fazer?",
    [
        "1. Comparar dois papéis (Duelo)",
        "2. Converter Isento -> Bruto (Equivalência)",
        "3. Converter Bruto -> Isento (Equivalência)"
    ]
)

# --- LÓGICA DO APP ---

# TIPO DE TAXA (Comum a todas as telas)
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Parâmetros")
rate_type = st.sidebar.selectbox(
    "Tipo de Rentabilidade",
    ["Pós-Fixado (% do CDI)", "Pré-Fixado (% a.a.)", "IPCA+ (% a.a.)"]
)

if rate_type == "IPCA+ (% a.a.)":
    ipca_proj = st.sidebar.number_input(
        "IPCA Projetado (% a.a.) - Essencial para o cálculo correto",
        value=4.50, step=0.10, format="%.2f"
    ) / 100
else:
    ipca_proj = 0

# ==============================================================================
# MODO 1: DUELO (COMPARADOR)
# ==============================================================================
if mode == "1. Comparar dois papéis (Duelo)":
    st.header("🥊 Duelo de Investimentos")
    st.info("Insira os dados dos dois papéis para ver qual coloca mais dinheiro no bolso do cliente.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🛡️ Isento")
        st.caption("(LCI, LCA, CRI, CRA, etc.)")
        rate_exempt = st.number_input("Taxa Isenta", value=90.0 if rate_type == "Pós-Fixado (% do CDI)" else 6.0, step=0.1)
        
    with col2:
        st.subheader("🏛️ Tributado")
        st.caption("(CDB, Renda Fixa, Tesouro)")
        rate_gross = st.number_input("Taxa Bruta", value=110.0 if rate_type == "Pós-Fixado (% do CDI)" else 8.0, step=0.1)

    prazo_dias = st.slider("Prazo do Investimento (dias corridos)", min_value=30, max_value=1500, value=365, step=30)
    
    # Cálculos
    aliquota_ir = get_ir_aliquot(prazo_dias)
    
    # Normalização das taxas para cálculo decimal
    r_exempt = rate_exempt / 100
    r_gross = rate_gross / 100
    
    # Lógica de Rentabilidade Líquida
    if rate_type == "Pós-Fixado (% do CDI)":
        # Simples: Bruto * (1 - IR) vs Isento
        net_from_gross = r_gross * (1 - aliquota_ir)
        comparison_val_exempt = r_exempt
        unit = "% do CDI"
        
    elif rate_type == "Pré-Fixado (% a.a.)":
        # Simples: Bruto * (1 - IR) vs Isento
        net_from_gross = r_gross * (1 - aliquota_ir)
        comparison_val_exempt = r_exempt
        unit = "% a.a."
        
    else: # IPCA+
        # Complexo: O IR incide sobre (IPCA + Taxa)
        # Rentabilidade Bruta Total = (1 + IPCA) * (1 + Taxa) - 1
        gross_total_yield = (1 + ipca_proj) * (1 + r_gross) - 1
        net_total_yield = gross_total_yield * (1 - aliquota_ir)
        
        # Agora convertemos de volta para IPCA + X líquido
        # (1 + IPCA) * (1 + TaxaLiq) - 1 = Net Total Yield
        # (1 + TaxaLiq) = (Net Total Yield + 1) / (1 + IPCA)
        spread_net_from_gross = ((net_total_yield + 1) / (1 + ipca_proj)) - 1
        
        net_from_gross = spread_net_from_gross * 100 # Para display
        comparison_val_exempt = r_exempt # Já está em %
        unit = "% + IPCA"

    # Resultado Visual
    st.divider()
    st.markdown(f"### Resultado para {prazo_dias} dias (IR: {aliquota_ir*100:.1f}%)")
    
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.metric(label="Rentabilidade Líquida do Tributado", value=f"{net_from_gross*100 if rate_type != 'IPCA+ (% a.a.)' else net_from_gross:.2f}{unit}")
    
    with col_res2:
        st.metric(label="Rentabilidade do Isento", value=f"{rate_exempt:.2f}{unit}")
        
    diff = (comparison_val_exempt * 100 if rate_type != 'IPCA+ (% a.a.)' else comparison_val_exempt) - (net_from_gross * 100 if rate_type != 'IPCA+ (% a.a.)' else net_from_gross)
    
    if diff > 0:
        st.markdown(f"""
        <div class="success-box">
        <b>🏆 O ISENTO VENCEU!</b><br>
        O papel isento rende <b>{abs(diff):.2f} p.p.</b> a mais que o tributado líquido.
        </div>
        """, unsafe_allow_html=True)
    elif diff < 0:
        st.markdown(f"""
        <div class="warning-box">
        <b>⚠️ O TRIBUTADO VENCEU!</b><br>
        Mesmo pagando imposto, o papel tributado rende <b>{abs(diff):.2f} p.p.</b> a mais no bolso.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Empate técnico!")

# ==============================================================================
# MODO 2: ISENTO -> BRUTO
# ==============================================================================
elif mode == "2. Converter Isento -> Bruto (Equivalência)":
    st.header("🔄 De Isento para Bruto")
    st.markdown("Se eu tenho um **LCI/CRI** pagando **X**, quanto um **CDB** precisaria pagar para empatar?")
    
    val_exempt = st.number_input("Taxa do Papel Isento", value=90.0 if rate_type == "Pós-Fixado (% do CDI)" else 6.0, step=0.5)
    
    st.subheader("Tabela de Equivalência")
    st.text("Para empatar com esse papel isento, o CDB deve pagar pelo menos:")
    
    results = []
    brackets = [
        ("Até 6 meses", 22.5),
        ("6 a 12 meses", 20.0),
        ("1 a 2 anos", 17.5),
        ("Acima de 2 anos", 15.0)
    ]
    
    for prazo, ir in brackets:
        ir_dec = ir / 100
        r_ex = val_exempt / 100
        
        if rate_type == "Pós-Fixado (% do CDI)" or rate_type == "Pré-Fixado (% a.a.)":
            # Gross = Exempt / (1 - IR)
            equiv_gross = r_ex / (1 - ir_dec)
            display_val = equiv_gross * 100
        else: # IPCA
            # Eq: (1 + IPCA)*(1 + Exempt) - 1 = [(1 + IPCA)*(1 + Gross) - 1] * (1 - IR)
            # Isolando Gross:
            # NetTotal = (1 + IPCA)*(1 + Exempt) - 1
            # GrossTotal = NetTotal / (1 - IR)
            # (1 + IPCA)*(1 + Gross) = GrossTotal + 1
            # 1 + Gross = (GrossTotal + 1) / (1 + IPCA)
            
            net_total = (1 + ipca_proj)*(1 + r_ex) - 1
            gross_total = net_total / (1 - ir_dec)
            gross_spread = ((gross_total + 1) / (1 + ipca_proj)) - 1
            display_val = gross_spread * 100
            
        results.append({
            "Prazo": prazo,
            "IR (%)": f"{ir}%",
            f"Taxa Bruta Necessária ({rate_type})": f"{display_val:.2f}%"
        })
        
    df = pd.DataFrame(results)
    st.table(df)
    
    if rate_type == "IPCA+ (% a.a.)":
        st.caption(f"*Cálculo considerando IPCA projetado de {ipca_proj*100:.2f}% a.a. O IR morde a inflação também!")

# ==============================================================================
# MODO 3: BRUTO -> ISENTO
# ==============================================================================
elif mode == "3. Converter Bruto -> Isento (Equivalência)":
    st.header("🔄 De Bruto para Isento")
    st.markdown("Se eu tenho um **CDB** pagando **Y**, quanto um **LCI/CRI** precisaria pagar para empatar?")
    
    val_gross = st.number_input("Taxa do Papel Tributado", value=110.0 if rate_type == "Pós-Fixado (% do CDI)" else 8.0, step=0.5)
    
    st.subheader("Tabela de Equivalência")
    st.text("O ganho líquido desse CDB equivale a um papel isento de:")
    
    results = []
    brackets = [
        ("Até 6 meses", 22.5),
        ("6 a 12 meses", 20.0),
        ("1 a 2 anos", 17.5),
        ("Acima de 2 anos", 15.0)
    ]
    
    for prazo, ir in brackets:
        ir_dec = ir / 100
        r_gr = val_gross / 100
        
        if rate_type == "Pós-Fixado (% do CDI)" or rate_type == "Pré-Fixado (% a.a.)":
            # Exempt = Gross * (1 - IR)
            equiv_exempt = r_gr * (1 - ir_dec)
            display_val = equiv_exempt * 100
        else: # IPCA
            # NetTotal = [(1 + IPCA)*(1 + Gross) - 1] * (1 - IR)
            # ExemptSpread = [(NetTotal + 1) / (1 + IPCA)] - 1
            
            gross_total = (1 + ipca_proj)*(1 + r_gr) - 1
            net_total = gross_total * (1 - ir_dec)
            exempt_spread = ((net_total + 1) / (1 + ipca_proj)) - 1
            display_val = exempt_spread * 100
            
        results.append({
            "Prazo": prazo,
            "IR (%)": f"{ir}%",
            f"Taxa Isenta Equivalente ({rate_type})": f"{display_val:.2f}%"
        })
        
    df = pd.DataFrame(results)
    st.table(df)
    
    if rate_type == "IPCA+ (% a.a.)":
        st.caption(f"*Cálculo considerando IPCA projetado de {ipca_proj*100:.2f}% a.a.")
