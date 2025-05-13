import streamlit as st
import plotly.graph_objects as go
import pandas as pd

# Configuração inicial
st.set_page_config(layout="wide")
st.title("🏫 Mapa Visual da Sala de Aula")

# Dados iniciais (se não existirem)
if "turma" not in st.session_state:
    st.session_state.turma = pd.DataFrame({
        "Aluno": ["João", "Maria", "Pedro", "Ana"],
        "Grupo": ["A", "B", "A", "B"],
        "Posição X": [1, 3, 1, 3],  # Coordenadas no layout
        "Posição Y": [1, 1, 2, 2],
        "Cor": ["blue", "red", "blue", "red"]
    })

# Selecionar layout
layout = st.selectbox(
    "Escolha o layout:",
    ["Tradicional (Fileiras)", "Em U", "Grupos (Peers Instruction)"]
)

# Função para desenhar a sala
def desenhar_sala():
    fig = go.Figure()

    # Adiciona "carteiras" conforme o layout
    if layout == "Tradicional (Fileiras)":
        for i in range(5):  # Fileiras
            for j in range(6):  # Carteiras por fileira
                fig.add_trace(go.Scatter(
                    x=[j + 1], y=[i + 1],
                    mode="markers+text",
                    marker=dict(size=25, color="lightgray"),
                    text="🪑", textposition="middle center",
                    name=f"L{i+1}C{j+1}"
                ))
    elif layout == "Em U":
        # Layout semicircular
        for i, angle in enumerate(range(0, 180, 30)):
            x = 5 + 3 * pd.np.cos(pd.np.radians(angle))
            y = 5 + 3 * pd.np.sin(pd.np.radians(angle))
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode="markers+text",
                marker=dict(size=25, color="lightgray"),
                text="🪑", textposition="middle center"
            ))
    else:  # Grupos
        for grupo_x in [2, 5, 8]:  # Posições dos grupos
            fig.add_trace(go.Scatter(
                x=[grupo_x, grupo_x + 1],
                y=[1, 1],
                mode="markers+text",
                marker=dict(size=25, color="lightgray"),
                text="🪑", textposition="middle center"
            ))

    # Adiciona alunos
    for _, aluno in st.session_state.turma.iterrows():
        fig.add_trace(go.Scatter(
            x=[aluno["Posição X"]], y=[aluno["Posição Y"]],
            mode="markers+text",
            marker=dict(size=25, color=aluno["Cor"]),
            text=aluno["Aluno"], textposition="middle center",
            name=aluno["Aluno"]
        ))

    # Ajusta o visual do gráfico
    fig.update_layout(
        title=f"Layout: {layout}",
        xaxis=dict(showgrid=False, range=[0, 10]),
        yaxis=dict(showgrid=False, range=[0, 10]),
        showlegend=False,
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

# Editor de dados
with st.expander("✏️ Editar Turma"):
    st.data_editor(
        st.session_state.turma,
        num_rows="dynamic",
        column_config={
            "Cor": st.column_config.ColorPickerColumn("Cor do Marcador")
        }
    )

desenhar_sala()