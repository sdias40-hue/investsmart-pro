# --- PASSO ATUAL: AJUSTE DO GRÁFICO ---
        st.markdown("<h4 class='neon-blue'>📈 Histórico de Preços</h4>", unsafe_allow_html=True)
        
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name="Preços"
        )])
        
        # Linha de tendência Azul Neon estável
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['Close'].rolling(7).mean(), 
            name="Tendência", 
            line=dict(color='#00d4ff', width=2)
        ))
        
        # Layout forçado para visibilidade no monitor do PC
        fig.update_layout(
            template="plotly_dark", 
            height=550, 
            margin=dict(l=5, r=5, t=10, b=10), 
            xaxis_rangeslider_visible=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
