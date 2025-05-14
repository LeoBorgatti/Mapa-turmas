from streamlit_plotly_events import plotly_events
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import pickle
import numpy as np
from functools import lru_cache

# 1. Cache para funções pesadas
@st.cache_data
def load_turmas():
    if os.path.exists("turmas.pkl"):
        with open("turmas.pkl", "rb") as f:
            return pickle.load(f)
    return None

# 2. Constantes globais
DEFAULT_COLUMNS = {
    "Aluno": [],
    "Fileira": [],
    "Carteira": [],
    "Categoria": [],
    "Laudo": [],
    "Cor": [],
    "nota": [],
    "estrelas": []
}

COLOR_MAP = {
    "Participativo": "#00CC96",
    "Reservado": "#636EFA",
    "Necessita Apoio": "#EF553B"
}

# 3. Configuração inicial otimizada
def initialize_app():
    if "turmas" not in st.session_state:
        turmas_loaded = load_turmas()
        if turmas_loaded:
            st.session_state.turmas = turmas_loaded
            # Garantir estrutura correta
            for turma_name, turma in st.session_state.turmas.items():
                for col in DEFAULT_COLUMNS:
                    if col not in turma.columns:
                        turma[col] = DEFAULT_COLUMNS[col]
                turma['estrelas'] = pd.to_numeric(turma['estrelas'], errors='coerce').fillna(3).astype(int)
        else:
            st.session_state.turmas = {
                "Turma 1": pd.DataFrame({
                    "Aluno": ["João", "Maria"],
                    "Fileira": [1, 1],
                    "Carteira": [1, 2],
                    "Categoria": ["Participativo", "Reservado"],
                    "Laudo": ["TDAH", "Nenhum"],
                    "Cor": ["#4285F4", "#EA4335"],
                    "nota": [0, 0],
                    "estrelas": [3, 4]
                })
            }
        
        st.session_state.turma_atual = "Turma 1"
        st.session_state.last_update = time.time()

# 4. Função de desenho da sala otimizada (sem fotos)
@st.cache_data(ttl=1, show_spinner=False)  # Cache mais agressivo
def desenhar_sala(turma, num_carteiras, num_fileiras):
    fig = go.Figure()
    
    # Grade de carteiras (desenho único)
    fig.add_shape(
        type="rect",
        x0=0.5, y0=0.5,
        x1=num_fileiras+0.5, y1=num_carteiras+0.5,
        fillcolor="#EEEEEE",
        layer="below",
        line=dict(color="#CCCCCC", width=2)
    )
    
    # Ícones de carteira (vetorizado)
    fig.add_trace(go.Scatter(
        x=np.repeat(np.arange(1, num_fileiras+1)), 
        y=np.tile(np.arange(1, num_carteiras+1)),
        mode="markers+text",
        marker=dict(size=0.1, opacity=0),
        text="🪑",
        textfont=dict(size=14),
        textposition="middle center",
        showlegend=False
    ))
    
    # Filtrar alunos visíveis
    alunos_visiveis = turma[
        (turma["Fileira"] <= num_fileiras) & 
        (turma["Carteira"] <= num_carteiras)
    ].copy()
    
    if not alunos_visiveis.empty:
        # Processamento vetorizado
        alunos_visiveis['estrelas'] = alunos_visiveis['estrelas'].clip(1, 5)
        alunos_visiveis['cor'] = alunos_visiveis['Categoria'].map(COLOR_MAP)
        
        # Marcadores de fundo (todos juntos)
        fig.add_trace(go.Scatter(
            x=alunos_visiveis["Fileira"]-0.1,
            y=alunos_visiveis["Carteira"],
            mode="markers",
            marker=dict(
                size=70,
                color=alunos_visiveis['cor'],
                symbol="line-ew",
                line=dict(width=24, color=alunos_visiveis['cor'])
            ),
            hovertext=alunos_visiveis["Aluno"] + 
                    " (F" + alunos_visiveis["Fileira"].astype(str) + 
                    " C" + alunos_visiveis["Carteira"].astype(str) + ")",
            hoverinfo="text",
            showlegend=False
        ))
        
        # Nomes dos alunos (todos juntos)
        fig.add_trace(go.Scatter(
            x=alunos_visiveis["Fileira"],
            y=alunos_visiveis["Carteira"],
            mode="text",
            text=alunos_visiveis["Aluno"],
            textposition="middle left",
            textfont=dict(color="white", size=12),
            showlegend=False
        ))
        
        # Estrelas (todos juntos)
        fig.add_trace(go.Scatter(
            x=alunos_visiveis["Fileira"],
            y=alunos_visiveis["Carteira"]-0.15,
            mode="text",
            text=["★"*e + "☆"*(5-e) for e in alunos_visiveis['estrelas']],
            textposition="bottom left",
            textfont=dict(color="gold", size=10),
            showlegend=False
        ))
    
    # Layout otimizado
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        title=f"<b>Mapa da Sala: {num_fileiras}x{num_carteiras}</b>",
        yaxis=dict(
            title="Carteiras",
            tickvals=list(range(1, num_carteiras+1))),
        xaxis=dict(
            title="Fileiras",
            tickvals=list(range(1, num_fileiras+1))),
        height=max(400, 70 * num_carteiras),  # Altura dinâmica
        plot_bgcolor="white",
        showlegend=False
    )
    
    return fig

# 5. Função principal otimizada
def main():
    initialize_app()
    st.set_page_config(layout="wide")
    st.title("✏️ Mapa da Sala - Versão Otimizada")
    
    # Controles superiores
    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            nova_turma = st.text_input("Nome da nova turma", key="new_class")
            if st.button("➕ Criar Turma") and nova_turma:
                if nova_turma not in st.session_state.turmas:
                    st.session_state.turmas[nova_turma] = pd.DataFrame(DEFAULT_COLUMNS)
                    st.session_state.turma_atual = nova_turma
                    st.rerun()
        
        with col2:
            turma_selecionada = st.selectbox(
                "Turma Atual",
                options=list(st.session_state.turmas.keys()),
                index=list(st.session_state.turmas.keys()).index(st.session_state.turma_atual))
            
            if turma_selecionada != st.session_state.turma_atual:
                st.session_state.turma_atual = turma_selecionada
                st.rerun()
    
    # Configuração da sala na sidebar
    with st.sidebar:
        st.header("Configuração da Sala")
        num_fileiras = st.slider("Fileiras", 1, 10, 5)
        num_carteiras = st.slider("Carteiras por Fileira", 1, 10, 6)
        
        if st.button("🔁 Resetar Turma", help="Remove todos os alunos"):
            st.session_state.turmas[st.session_state.turma_atual] = pd.DataFrame(DEFAULT_COLUMNS)
            st.rerun()
    
    # Editor de turma
    with st.expander("📝 Editor de Turma", expanded=True):
        tab1, tab2 = st.tabs(["Adicionar Aluno", "Editar Turma"])
        
        with tab1:
            with st.form("add_student_form"):
                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome do Aluno")
                    categoria = st.selectbox("Categoria", list(COLOR_MAP.keys()))
                with col2:
                    fileira = st.number_input("Fileira", 1, num_fileiras, 1)
                    carteira = st.number_input("Carteira", 1, num_carteiras, 1)
                
                col3, col4 = st.columns(2)
                with col3:
                    laudo = st.selectbox("Laudo", ["Nenhum", "TEA", "TDAH", "Outros"])
                with col4:
                    estrelas = st.slider("Estrelas", 1, 5, 3)
                
                if st.form_submit_button("✅ Adicionar"):
                    novo_aluno = {
                        "Aluno": nome,
                        "Fileira": fileira,
                        "Carteira": carteira,
                        "Categoria": categoria,
                        "Laudo": laudo,
                        "Cor": COLOR_MAP[categoria],
                        "nota": 0,
                        "estrelas": estrelas
                    }
                    st.session_state.turmas[st.session_state.turma_atual] = pd.concat([
                        st.session_state.turmas[st.session_state.turma_atual],
                        pd.DataFrame([novo_aluno])
                    ], ignore_index=True)
                    st.rerun()
        
        with tab2:
            edited_df = st.data_editor(
                st.session_state.turmas[st.session_state.turma_atual],
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "Cor": st.column_config.ColorColumn("Cor"),
                    "Categoria": st.column_config.SelectboxColumn(
                        "Categoria", options=list(COLOR_MAP.keys())),
                    "estrelas": st.column_config.NumberColumn("Estrelas", 1, 5)
                },
                key=f"editor_{st.session_state.turma_atual}"
            )
            
            if st.button("💾 Salvar Alterações"):
                st.session_state.turmas[st.session_state.turma_atual] = edited_df
                st.rerun()
    
    # Mapa da sala
    st.subheader(f"Visualização: {st.session_state.turma_atual}")
    with st.spinner("Gerando mapa..."):
        fig = desenhar_sala(
            st.session_state.turmas[st.session_state.turma_atual],
            num_carteiras,
            num_fileiras
        )
        selected_points = plotly_events(fig, click_event=True)
    
    # Salvar dados automaticamente
    with open("turmas.pkl", "wb") as f:
        pickle.dump(st.session_state.turmas, f)

if __name__ == "__main__":
    main()