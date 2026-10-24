import streamlit as st
import sys
from pathlib import Path

# Caminho para a pasta python/
PYTHON_DIR = Path(__file__).resolve().parent.parent

# Permitir importar ficheiros da pasta python/
sys.path.insert(0, str(PYTHON_DIR))

# Importar a função que cria o Campus com as 6 salas
from populate import create_campus

# ------------------------
# PAGE CONFIGURATION
# ------------------------

st.set_page_config(
    page_title="SmartCampus",
    page_icon="🏫",
    layout="wide"
)


# ------------------------
# CAMPUS INITIALIZATION
# ------------------------

@st.cache_resource
def get_campus():
    return create_campus()


campus = get_campus()


# ------------------------
# HEADER
# ------------------------

st.title("🏫 SmartCampus")

st.write("Sistema inteligente de gestão de edifícios universitários")

st.divider()


# ------------------------
# CAMPUS STATISTICS
# ------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Salas", len(campus.get_all_rooms()))

with col2:
    st.metric("Pessoas no edifício", campus.total_people())

with col3:
    st.metric("Capacidade total", campus.total_capacity())

st.divider()


# ------------------------
# CLASSROOMS
# ------------------------

st.header("Salas do edifício")

rooms = campus.get_all_rooms()

columns = st.columns(3)

for index, room in enumerate(rooms):

    with columns[index % 3]:

        with st.container(border=True):

            st.subheader(f"🚪 Sala {room.room_id}")

            st.metric(
                "Ocupação",
                f"{room.people_count}/{room.capacity}"
            )

            st.write(f"🌡️ Temperatura: {room.temperature} °C")

            st.write(f"💧 Humidade: {room.humidity}%")

            st.write(f"🌫️ CO₂: {room.co2} ppm")

            st.divider()

            st.write(
                f"💡 Luzes: {'Ligadas' if room.lights_on else 'Desligadas'}"
            )

            st.write(
                f"❄️ Ar condicionado: {'Ligado' if room.ac_on else 'Desligado'}"
            )

            st.write(
                f"🔒 Porta: {'Trancada' if room.door_locked else 'Destrancada'}"
            )