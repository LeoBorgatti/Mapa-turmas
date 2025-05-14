from streamlit_plotly_events import plotly_events
import streamlit as st
from PIL import Image
import io
import plotly.graph_objects as go
import pandas as pd
import os
import pickle
import sys
import time
import base64
import numpy as np

# Definir colunas padrão que devem existir
DEFAULT_COLUMNS = {
    "Aluno": [],
    "Fileira": [],
    "Carteira": [],
    "Categoria": [],
    "Laudo": [],
    "Cor": [],
    "nota": [],
    "estrelas": [],
    "Foto": []
}

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
            
            # Garantir que todas as turmas tenham as colunas necessárias
            for turma_name, turma in st.session_state.turmas.items():
                # Adicionar colunas faltantes com valores padrão
                for col in DEFAULT_COLUMNS:
                    if col not in turma.columns:
                        if col == 'estrelas':
                            turma[col] = 3  # Valor padrão para estrelas
                        elif col == 'Foto':
                            turma[col] = None
                        else:
                            turma[col] = DEFAULT_COLUMNS[col]
                
                # Garantir que estrelas seja numérico
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
                "estrelas": [3, 4],
                "Foto": [None, None]
            })
        }
    
    st.session_state.turma_atual = "Turma 1"
    st.session_state.last_update = time.time()
    st.session_state.uploader_counter = 0

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

st.set_page_config(layout="wide")
st.title("✏️ Mapa da Sala Customizável")

# Controle de turmas
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    nova_turma = st.text_input("Nome da nova turma")
    if st.button("➕ Criar turma") and nova_turma:
        if nova_turma not in st.session_state.turmas:
            st.session_state.turmas[nova_turma] = pd.DataFrame({
                "Aluno": [],
                "Fileira": [],
                "Carteira": [],
                "Categoria": [],
                "Laudo": [],
                "Cor": [],
                "nota": [],
                "estrelas": [],
                "Foto": []
            })
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

st.session_state.turma = st.session_state.turmas[st.session_state.turma_atual]

# Controles para definir o tamanho da sala
col1, col2 = st.columns(2)
with col1:
    num_carteiras = st.number_input("Número de Carteiras por Fileira", 
                                   min_value=1, max_value=10, 
                                   value=st.session_state.get('num_carteiras', 6),
                                   key='num_carteiras')
with col2:
    num_fileiras = st.number_input("Número de Fileiras", 
                                  min_value=1, max_value=10, 
                                  value=st.session_state.get('num_fileiras', 5),
                                  key='num_fileiras')
COLOR_MAP = {
    "Participativo": "#00CC96",
    "Reservado": "#636EFA",
    "Necessita Apoio": "#EF553B"
}

def criar_estrelas(num_estrelas):
    # Garante que num_estrelas seja um inteiro válido entre 1 e 5
    try:
        num_estrelas = int(num_estrelas) if not pd.isna(num_estrelas) else 3
    except (ValueError, TypeError):
        num_estrelas = 3
    num_estrelas = max(1, min(5, num_estrelas))
    estrelas_cheias = "★" * num_estrelas
    estrelas_vazias = "☆" * (5 - num_estrelas)
    return f"{estrelas_cheias}{estrelas_vazias}"

# EDITOR DE TURMA
with st.expander("📝 Gerenciar Turma", expanded=True):
    tab1, tab2 = st.tabs(["Adicionar Aluno", "Editar Turma"])
    
    with tab1:
        categoria = st.selectbox("Categoria", list(COLOR_MAP.keys()), key="categoria_aluno")
        laudo = st.selectbox("Laudo", ["Nenhum", "TEA", "TDAH", "Outros"], key="laudo_aluno")
        novo_aluno = st.text_input("Nome do Aluno")
        col1, col2 = st.columns(2)
        with col1:
            fileira = st.number_input("Fileira", 1, num_fileiras, 1)
        with col2:
            carteira = st.number_input("Carteira", 1, num_carteiras, 1)
        nota = st.number_input("Nota")
        estrelas = st.number_input("Estrelas (1-5)", 1, 5, 3)
        
        uploaded_file = st.file_uploader("Foto do Aluno", type=["jpg", "jpeg", "png"])
        foto_base64 = None
        if uploaded_file:
            image = Image.open(uploaded_file)
            image.thumbnail((200, 200))
            foto_base64 = image_to_base64(image)
        
        if st.button("✅ Adicionar Aluno"):
            novo_registro = pd.DataFrame([{
                "Aluno": novo_aluno,
                "Fileira": fileira,
                "Carteira": carteira,
                "Categoria": categoria,
                "Laudo": laudo,
                "Cor": COLOR_MAP[categoria],
                "nota": nota,
                "estrelas": estrelas,
                "Foto": foto_base64
            }])
            st.session_state.turmas[st.session_state.turma_atual] = pd.concat([
                st.session_state.turma, novo_registro
            ], ignore_index=True)
            st.session_state.last_update = time.time()
            st.rerun()
    
    with tab2:
        # Garantir que todas as colunas existam
        for col in DEFAULT_COLUMNS:
            if col not in st.session_state.turma.columns:
                if col == 'estrelas':
                    st.session_state.turma[col] = 3
                elif col == 'Foto':
                    st.session_state.turma[col] = None
                else:
                    st.session_state.turma[col] = DEFAULT_COLUMNS[col]
        
        edited_df = st.session_state.turma.copy()
        novas_fotos = {}

        for idx, aluno in edited_df.iterrows():
            st.subheader(f"Aluno: {aluno['Aluno']}")
            col1, col2 = st.columns(2)
            with col1:
                if pd.notna(aluno['Foto']) and aluno['Foto']:
                    try:
                        st.image(io.BytesIO(base64.b64decode(aluno['Foto'])), width=100)
                    except:
                        st.write("Foto inválida")
                else:
                    st.write("Sem foto")
            
            with col2:
                uploader_key = f"foto_{st.session_state.turma_atual}_{idx}_{st.session_state.uploader_counter}"
                nova_foto = st.file_uploader("Atualizar foto", ["jpg", "jpeg", "png"], key=uploader_key)
                st.session_state.uploader_counter += 1
                
                if nova_foto:
                    image = Image.open(nova_foto)
                    image.thumbnail((200, 200))
                    novas_fotos[idx] = image_to_base64(image)
        
        # Converter estrelas para inteiro antes da edição
        edited_df['estrelas'] = pd.to_numeric(edited_df['estrelas'], errors='coerce').fillna(3).astype(int)
        
        edited_df = st.data_editor(
            edited_df.drop(columns=['Foto'], errors='ignore'),
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
                "nota": st.column_config.NumberColumn(
                    "Nota",
                    min_value=0,
                    max_value=10,
                    step=0.5
                ),
                "estrelas": st.column_config.NumberColumn(
                    "Estrelas (1-5)",
                    min_value=1,
                    max_value=5,
                    step=1
                )
            },
            key=f"editor_{st.session_state.turma_atual}",
            hide_index=True
        )
        
        if st.button("💾 Salvar Alterações"):
            edited_df['Foto'] = st.session_state.turma['Foto']
            for idx, foto in novas_fotos.items():
                edited_df.at[idx, 'Foto'] = foto
            # Garantir que estrelas sejam inteiros válidos
            edited_df['estrelas'] = pd.to_numeric(edited_df['estrelas'], errors='coerce').fillna(3).clip(1, 5).astype(int)
            st.session_state.turmas[st.session_state.turma_atual] = edited_df
            st.session_state.last_update = time.time()
            st.rerun()

# DESENHO DA SALA
st.header("Mapa da Sala")
mapa_container = st.empty()

def desenhar_sala():
    fig = go.Figure()
    
   # Obter os valores atuais dos controles
    num_carteiras = st.session_state.get('num_carteiras', 6)
    num_fileiras = st.session_state.get('num_fileiras', 5)
    
    # Carteiras vazias
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
    
    # Legenda
    for categoria, cor in COLOR_MAP.items():
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=15, color=cor, symbol="square"),
            name=categoria,
            legendgroup=categoria
        ))
    
    # Alunos
    for _, aluno in st.session_state.turma.iterrows():
        if aluno["Fileira"] <= num_fileiras and aluno["Carteira"] <= num_carteiras:
            categoria = str(aluno.get("Categoria", "Reservado"))
            cor = COLOR_MAP.get(categoria, "#CCCCCC")
            
            # Tratamento robusto para valores de estrelas
            estrelas = aluno.get("estrelas", 3)
            try:
                estrelas = int(float(estrelas)) if pd.notna(estrelas) else 3
            except (ValueError, TypeError):
                estrelas = 3
            estrelas = max(1, min(5, estrelas))
            
            # Elemento principal (fundo colorido)
            fig.add_trace(go.Scatter(
                y=[aluno["Carteira"]],
                x=[aluno["Fileira"]-0.1],
                mode="markers",
                marker=dict(
                    size=70,
                    color=cor,
                    symbol="line-ew",
                    line=dict(width=24, color=cor),
                    
                ),
                hovertext=f"{aluno['Aluno']} (F{aluno['Fileira']} C{aluno['Carteira']})",
                showlegend=False
            ))
            
            # Nome do aluno
            fig.add_trace(go.Scatter(
                y=[aluno["Carteira"]],
                x=[aluno["Fileira"]],
                mode="text",
                text=aluno["Aluno"],
                textposition="middle left",
                textfont=dict(color="white", size=15, family="Arial"),
                showlegend=False
            ))
            
            # Estrelas
            fig.add_trace(go.Scatter(
                y=[aluno["Carteira"]-0.15],
                x=[aluno["Fileira"]],
                mode="text",
                text=criar_estrelas(estrelas),
                textposition="bottom left",
                textfont=dict(color="gold", size=10),
                showlegend=False
            ))
            
            # Foto (se existir)
            if pd.notna(aluno.get("Foto")) and aluno["Foto"]:
                fig.add_layout_image(
                    dict(
                        source=f"data:image/png;base64,{aluno['Foto']}",
                        xref="x",
                        yref="y",
                        x=aluno["Fileira"] + 0.35,
                        y=aluno["Carteira"],
                        sizex=0.5,
                        sizey=0.5,
                        xanchor="right",
                        yanchor="middle",
                        sizing="contain",
                        layer="above"
                    )
                )
    
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

# Renderização
with mapa_container:
    fig = desenhar_sala()
    selected_points = plotly_events(
        fig, 
        click_event=True,
        key=f"plotly_{st.session_state.turma_atual}_{st.session_state.last_update}"
    )
    
    if selected_points:
        fileira = selected_points[0]["x"]
        carteira = selected_points[0]["y"]
        
        aluno_idx = st.session_state.turma[
            (st.session_state.turma["Fileira"] == fileira) & 
            (st.session_state.turma["Carteira"] == carteira)
        ].index
        
        if not aluno_idx.empty:
            nova_estrela = min(5, max(1, round(selected_points[0]["pointNumber"] + 1)))
            st.session_state.turma.loc[aluno_idx, "estrelas"] = nova_estrela
            st.session_state.last_update = time.time()
            st.rerun()

# RESET
if st.button("🔄 Resetar Turma"):
    st.session_state.turmas[st.session_state.turma_atual] = pd.DataFrame({
        "Aluno": [],
        "Fileira": [],
        "Carteira": [],
        "Categoria": [],
        "Laudo": [],
        "Cor": [],
        "nota": [],
        "estrelas": [],
        "Foto": []
    })
    st.session_state.last_update = time.time()
    st.rerun()

# Salvar dados
with open("turmas.pkl", "wb") as f:
    pickle.dump(st.session_state.turmas, f)