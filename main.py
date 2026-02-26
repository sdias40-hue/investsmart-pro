st.markdown("""
    <style>
    /* Fundo Preto Absoluto Blindado */
    .stApp, .main, header, .stSidebar, [data-testid="stHeader"] { 
        background-color: #000000 !important; 
    }
    
    /* Fontes Brancas e Segoe UI para nitidez */
    h1, h2, h3, h4, p, span, label, div, .stMarkdown { 
        color: #ffffff !important; 
        font-family: 'Segoe UI', sans-serif !important; 
    }
    
    /* AJUSTE DA SETA: Pequena, azul e discreta no celular */
    [data-testid="collapsedControl"] {
        background-color: #00d4ff !important;
        border-radius: 0 10px 10px 0;
        width: 35px !important;
        height: 35px !important;
        top: 10px !important;
    }
    /* Substitui o texto 'keyboard...' por uma seta real */
    [data-testid="collapsedControl"]::before {
        content: "〉" !important;
        color: #000000 !important;
        font-weight: bold;
        padding-left: 10px;
    }
    /* Esconde o texto grande do sistema */
    [data-testid="collapsedControl"] span {
        display: none !important;
    }

    .neon-blue { color: #00d4ff !important; font-weight: bold; }
    
    /* Cards de Métricas e Mentor */
    .stMetric { background-color: #0a0a0a !important; border: 1px solid #00d4ff !important; border-radius: 8px; }
    .mentor-box { background-color: #0e1117; border-left: 6px solid #00d4ff; padding: 20px; border-radius: 8px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)
