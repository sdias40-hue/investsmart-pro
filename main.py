st.markdown("""
    <style>
    /* 1. Fundo Preto Absoluto Blindado */
    .stApp, .main, header, .stSidebar, [data-testid="stHeader"] { 
        background-color: #000000 !important; 
    }
    
    /* 2. Fontes Brancas Master */
    h1, h2, h3, h4, p, span, label, div, .stMarkdown { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', sans-serif !important; 
    }
    
    /* 3. AJUSTE DA SETA: Minimalista e Profissional */
    [data-testid="collapsedControl"] {
        background-color: #00d4ff !important;
        border-radius: 0 12px 12px 0;
        width: 40px !important;
        height: 40px !important;
        top: 15px !important;
        left: 0 !important;
    }
    /* Substitui o texto 'keyboard_double' por uma seta real */
    [data-testid="collapsedControl"]::before {
        content: "〉" !important;
        color: #000000 !important;
        font-size: 20px !important;
        font-weight: bold;
        position: absolute;
        left: 12px;
        top: 6px;
    }
    /* Esconde o código de texto do sistema */
    [data-testid="collapsedControl"] span {
        display: none !important;
    }

    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; }
    .mentor-box { background-color: #0e1117; border-left: 6px solid #00d4ff; padding: 20px; border-radius: 8px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)
