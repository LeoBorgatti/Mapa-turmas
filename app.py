from streamlit_plotly_events import plotly_events
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import pickle
import sys
import time

# Fix para PyInstaller + Streamlit
if getattr(sys, 'frozen', False):
    os.environ['STREAMLIT_RUNNING_IN_PYINSTALLER'] = '1'
    import importlib_metadata
    sys.modules['importlib.metadata'] = importlib_metadata

# Configuração do app
if "turmas" not in st.session_state:
    if os.path.exists("turmas.pkl"):
        with open("turmas.pkl", "rb") as f:
            st.session_state.turmas = pickle.load(f)
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

st.set_page_config(layout="wide")
st.title("✏️ Mapa da Sala Customizável")

# Controle de turmas
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    nova_turma = st.text_input("Nome da nova turma")
    if st.button("➕ Criar turma") and nova_turma:
        if nova_turma not in st.session_state.turmas:
            st.session_state.turmas[nova_turma] = pd.DataFrame(columns=[
                "Aluno", "Fileira", "Carteira", "Categoria", "Laudo", "Cor", "estrelas", "nota"
            ])
            st.session_state.turma_atual = nova_turma
            st.session_state.last_update = time.time()
            st.rerun()

with col2:
    turma_selecionada = st.selectbox(
        "Selecione a turma",
        options=list(st.session_state.turmas.keys()),
        index=list(st.session_state.turmas.keys()).index(st.session_state.turma_atual),
        key="seletor_turma"
    )
    
    if turma_selecionada != st.session_state.turma_atual:
        st.session_state.turma_atual = turma_selecionada
        st.session_state.last_update = time.time()
        st.rerun()

with col3:
    if st.button("🗑️ Excluir turma atual"):
        if len(st.session_state.turmas) > 1:
            del st.session_state.turmas[st.session_state.turma_atual]
            st.session_state.turma_atual = list(st.session_state.turmas.keys())[0]
            st.session_state.last_update = time.time()
            st.rerun()
        else:
            st.warning("Não é possível excluir a única turma existente")

# Atualiza a turma atual para uso no resto do código
st.session_state.turma = st.session_state.turmas[st.session_state.turma_atual]

# Controles para definir o tamanho da sala
col1, col2 = st.columns(2)
with col1:
    num_carteiras = st.number_input("Número de Carteiras por Fileira", min_value=1, max_value=10, value=6)
with col2:
    num_fileiras = st.number_input("Número de Fileiras", min_value=1, max_value=10, value=5)

# ========== CONFIGURAÇÕES DE CORES ==========
COLOR_MAP = {
    "Participativo": "#00CC96",  # Verde
    "Reservado": "#636EFA",      # Azul
    "Necessita Apoio": "#EF553B" # Vermelho
}

def criar_estrelas(num_estrelas):
    estrelas_cheias = "★" * num_estrelas
    estrelas_vazias = "☆" * (5 - num_estrelas)
    return f"<span style='color:gold;font-size:12px;'>{estrelas_cheias}{estrelas_vazias}</span>"

# ========== EDITOR DE TURMA ==========
with st.expander("📝 Gerenciar Turma", expanded=True):
    tab1, tab2 = st.tabs(["Adicionar Aluno", "Editar Turma"])
    
    with tab1:
        categoria = st.selectbox(
            "Categoria", 
            ["Participativo", "Reservado", "Necessita Apoio"],
            key="categoria_aluno"
        )
        laudo = st.selectbox(
            "Laudo do Aluno",
            ["Nenhum", "TEA", "Altas habilidades", "Distúrbio de aprendizagem", 
             "TDAH", "Baixa visão", "Surdez", "Outros"],
            key="laudo_aluno"
        )
        col1, col2 = st.columns(2)
        with col1:
            novo_aluno = st.text_input("Nome do Aluno")
       
        col1, col2 = st.columns(2)
        with col1:
            fileira = st.number_input("Fileira", 1, num_fileiras, 1)
        with col2:
            carteira = st.number_input("Carteira", 1, num_carteiras, 1)
        with col1:
            nota = st.number_input("Nota")
        with col2:
            estrelas = st.number_input("Estrelas (1-5)", min_value=1, max_value=5, value=3)
        
        if st.button("✅ Adicionar Aluno"):
            novo_registro = pd.DataFrame({
                "Aluno": [novo_aluno],
                "Fileira": [int(fileira)],
                "Carteira": [int(carteira)],
                "Categoria": [categoria],
                "Laudo": [laudo],
                "Cor": [COLOR_MAP[categoria]],
                "estrelas": [int(estrelas)],
                "nota": [float(nota)]
            })
            st.session_state.turmas[st.session_state.turma_atual] = pd.concat([
                st.session_state.turmas[st.session_state.turma_atual], 
                novo_registro
            ], ignore_index=True)
            st.session_state.last_update = time.time()
            st.rerun()
    
    with tab2:
        edited_df = st.data_editor(
            st.session_state.turma,
            num_rows="dynamic",
            column_config={
                "Cor": st.column_config.TextColumn("Cor (código hexadecimal)"),
                "Categoria": st.column_config.SelectboxColumn(
                    "Categoria",
                    options=["Participativo", "Reservado", "Necessita Apoio"]
                ),
                "Laudo": st.column_config.SelectboxColumn( 
                    "Laudo",
                    options=["Nenhum", "TEA", "Altas habilidades", "Distúrbio de aprendizagem", 
                            "TDAH", "Baixa visão", "Surdez", "Outros"]
                ),
                "nota": st.column_config.NumberColumn("Nota"),
                "estrelas": st.column_config.NumberColumn("Estrelas (1-5)", min_value=1, max_value=5, step=1)
            },
            key=f"editor_{st.session_state.turma_atual}"
        )
        if st.button("💾 Salvar Alterações"):
            st.session_state.turmas[st.session_state.turma_atual] = edited_df
            st.session_state.last_update = time.time()
            st.rerun()

# ========== DESENHO DA SALA ==========
st.header("Mapa da Sala")
mapa_container = st.empty()

def desenhar_sala():
    fig = go.Figure()
    
    # Desenha as carteiras vazias
    for fileira in range(1, num_fileiras + 1):
        for carteira in range(1, num_carteiras + 1):
            fig.add_shape(
                type="rect",
                x0=fileira - 0.4,
                x1=fileira + 0.4,
                y0=carteira - 0.3,
                y1=carteira + 0.3,
                line=dict(color="#CCCCCC", width=2),
                fillcolor="#EEEEEE",
                layer="below"
            )
            fig.add_trace(go.Scatter(
                x=[fileira],
                y=[carteira],
                mode="text",
                text="🪑",
                textfont=dict(size=14),
                textposition="middle center",
                showlegend=False
            ))
    
    # Categorias para legenda
    for categoria, cor in COLOR_MAP.items():
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=15, color=cor, symbol="square"),
            name=categoria,
            legendgroup=categoria
        ))
    
    # Adiciona alunos
    for _, aluno in st.session_state.turma.iterrows():
        if aluno["Fileira"] <= num_fileiras and aluno["Carteira"] <= num_carteiras:
            categoria = str(aluno.get("Categoria", "Reservado"))
            cor = COLOR_MAP.get(categoria, "#CCCCCC")
            estrelas = int(aluno["estrelas"]) if pd.notna(aluno["estrelas"]) else 0
            estrelas = max(0, min(5, estrelas))
            estrelas_cheias = "★" * estrelas
            estrelas_vazias = "☆" * (5 - estrelas)
            texto_aluno = f"{aluno['Aluno']}<br><span style='color:gold;font-size:12px;'>{estrelas_cheias}{estrelas_vazias}</span>"
            
            fig.add_trace(go.Scatter(
                y=[aluno["Carteira"]],
                x=[aluno["Fileira"]],
                mode="markers+text",
                marker=dict(
                    size=70,
                    color=cor,
                    symbol="line-ew",
                    line=dict(width=24, color=cor)
                ),
                text=texto_aluno,
                textposition="middle center",
                textfont=dict(color="white", size=12, family="Arial"),
                hovertext=f"{aluno['Aluno']} (F{aluno['Fileira']} C{aluno['Carteira']})<br>Categoria: {categoria}<br>Laudo: {aluno.get('Laudo', 'Nenhum')}",
                customdata=[[aluno["Fileira"], [aluno["Carteira"]]]],
                name=aluno["Aluno"],
                showlegend=False
            ))

    fig.update_layout(
        title=f"<b>Sala: {num_carteiras} Carteiras</b> x {num_fileiras} Fileiras",
        yaxis=dict(
            title="Carteiras",
            tickmode="array",
            tickvals=list(range(1, num_carteiras + 1)),
            range=[0.5, num_carteiras + 0.5],
            showgrid=False
        ),
        xaxis=dict(
            title="Fileiras",
            tickmode="array",
            tickvals=list(range(1, num_fileiras + 1)),
            range=[0.5, num_fileiras + 0.5],
            showgrid=False
        ),
        height=700,
        plot_bgcolor="white",
        legend=dict(
            title_text="Categorias",
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

# Renderiza o mapa e captura eventos
with mapa_container:
    fig = desenhar_sala()
    selected_points = plotly_events(
        fig, 
        click_event=True,
        key=f"plotly_events_{st.session_state.turma_atual}_{st.session_state.last_update}"
    )
    
    if selected_points:
        fileira = selected_points[0]["x"]
        carteira = selected_points[0]["y"]
        
        aluno_idx = st.session_state.turma[
            (st.session_state.turma["Fileira"] == fileira) & 
            (st.session_state.turma["Carteira"] == carteira)
        ].index
        
        if not aluno_idx.empty:
            estrelas = min(5, max(1, round(selected_points[0]["pointNumber"] + 1)))
            st.session_state.turma.loc[aluno_idx, "estrelas"] = estrelas
            st.session_state.last_update = time.time()
            st.rerun()

# ========== RESET ==========
if st.button("🔄 Resetar Turma"):
    st.session_state.turmas[st.session_state.turma_atual] = pd.DataFrame(columns=[
        "Aluno", "Fileira", "Carteira", "Categoria", "Laudo", "Cor", "nota", "estrelas"
    ])
    st.session_state.last_update = time.time()
    st.rerun()

# Salva as turmas no arquivo
with open("turmas.pkl", "wb") as f:
    pickle.dump(st.session_state.turmas, f)