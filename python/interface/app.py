"""SmartCampus: seis salas com planta SVG interativa."""

import sys
from pathlib import Path
from mqtt_sync import CampusMQTTSync

import streamlit as st


# ============================================================
# IMPORTS
# ============================================================

PYTHON_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(PYTHON_DIR))

from populate import create_campus
from interactive_floorplan import render_interactive_floorplan


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SmartCampus",
    page_icon="🏫",
    layout="wide"
)


# ============================================================
# CAMPUS
# ============================================================

@st.cache_resource
def get_campus():

    campus = create_campus()

    campus.mqtt_sync = CampusMQTTSync(campus)

    return campus

campus = get_campus()


# ============================================================
# NAVIGATION
# ============================================================

st.session_state.setdefault(
    "selected_room",
    None
)


def open_room(room_id):

    st.session_state.selected_room = room_id

    st.rerun()


def go_back():

    st.session_state.selected_room = None

    st.rerun()


# ============================================================
# BUILDING LIVE DATA
# ============================================================

@st.fragment(run_every="1s")
def show_building_live():

    rooms = campus.get_all_rooms()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Salas",
        len(rooms)
    )

    col2.metric(
        "Pessoas no edifício",
        campus.total_people()
    )

    col3.metric(
        "Capacidade total",
        campus.total_capacity()
    )

    st.divider()

    st.html("""
    <style>
        [class*="st-key-alarm_room_"] {
            background-color: rgba(239, 68, 68, 0.20) !important;
            border: 2px solid #ef4444 !important;
            border-radius: 14px;
            box-shadow: 0 0 14px rgba(239, 68, 68, 0.18);
        }

        [class*="st-key-alarm_room_"] h3 {
            color: #ef4444 !important;
        }
    </style>
    """)

    columns = st.columns(3)

    for index, room in enumerate(rooms):

        with columns[index % 3]:

            with st.container(
                border=True,
                key=(
                    f"alarm_room_{room.room_id}"
                    if room.alarm_on
                    else f"normal_room_{room.room_id}"
                )
            ):

                st.subheader(
                    f"🚪 Sala {room.room_id}"
                )

                if room.alarm_on:

                    st.error("🚨 ALARME ATIVO")

                st.metric(
                    "Ocupação",
                    f"{room.people_count}/{room.capacity}"
                )

                st.write(
                    f"🌡️ {room.temperature:.1f} °C · "
                    f"💧 {room.humidity:.1f}% · "
                    f"CO₂ {room.co2:.0f} ppm"
                )

                mode = room.ac_mode.removeprefix("ac_")

                ac_label = {
                    "off": "Desligado",
                    "cool": "Frio",
                    "heat": "Quente"
                }.get(mode, "Frio")

                st.caption(
                    f"💡 {'Ligadas' if room.lights_on else 'Desligadas'} · "
                    f"❄️ {ac_label} · "
                    f"🚪 {'Trancada' if room.door_locked else 'Destrancada'}"
                )

                if st.button(
                    f"Entrar na sala {room.room_id} →",
                    key=f"open_{room.room_id}",
                    use_container_width=True
                ):

                    open_room(room.room_id)


# ============================================================
# BUILDING PAGE
# ============================================================

def show_building():

    st.title("🏫 SmartCampus")

    st.write(
        "Sistema inteligente de gestão de edifícios universitários"
    )

    st.divider()

    st.header("Salas do edifício")

    st.caption(
        "Seleciona uma das seis salas."
    )

    show_building_live()


# ============================================================
# CLASSROOM LIVE DATA
# ============================================================

@st.fragment(run_every="1s")
def show_room_live(room_id):

    room = campus.get_room(room_id)

    if room is None:

        st.error("Sala não encontrada.")

        return

    # --------------------------------------------------------
    # INTERACTIVE FLOORPLAN
    # --------------------------------------------------------

    st.subheader("Planta interativa da sala")

    render_interactive_floorplan(
        room,
        campus
    )

    if room.alarm_on:

        st.error(
            f"🚨 ALARME ATIVO — "
            f"{room.alarm_reason or 'Alarme ativado'}"
        )

    st.caption(
        "Clica nas luzes, no AC ou na porta. "
    )

    st.divider()

    # --------------------------------------------------------
    # OCCUPANCY
    # --------------------------------------------------------

    people, capacity = st.columns(2)

    people.metric(
        "👥 Ocupantes",
        room.people_count
    )

    capacity.metric(
        "🏫 Capacidade",
        room.capacity
    )

    if room.capacity:

        occupancy = (
            room.people_count / room.capacity
        )

    else:
        occupancy = 0

    st.progress(
        max(0.0, min(1.0, occupancy)),
        text=f"Ocupação: {occupancy:.0%}"
    )

    # --------------------------------------------------------
    # ENVIRONMENTAL DATA
    # --------------------------------------------------------

    st.subheader("🌡️ Condições ambientais")

    t, h, co2 = st.columns(3)

    t.metric(
        "Temperatura",
        f"{room.temperature:.1f} °C"
    )

    h.metric(
        "Humidade",
        f"{room.humidity:.1f}%"
    )

    co2.metric(
        "CO₂",
        f"{room.co2:.0f} ppm"
    )

    # ========================================================
    # MANUAL ROOM CONTROL
    # ========================================================

    st.divider()

    st.subheader("🛠️ Controlo manual da sala")

    if room.manual_mode:
        st.warning("⚙️ Simulação automática pausada nesta sala.")
    else:
        st.success("🟢 Simulação automática ativa.")

    with st.expander("Editar valores da sala", expanded=False):

        with st.form(key=f"manual_values_{room_id}"):

            people_input = st.number_input(
                "👥 Número de pessoas",
                min_value=0,
                max_value=room.capacity,
                value=int(room.people_count),
                step=1
            )

            temperature_input = st.number_input(
                "🌡️ Temperatura atual (°C)",
                min_value=-10.0,
                max_value=50.0,
                value=float(room.temperature),
                step=0.5
            )

            humidity_input = st.number_input(
                "💧 Humidade (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(room.humidity),
                step=1.0
            )

            co2_input = st.number_input(
                "🌫️ CO₂ (ppm)",
                min_value=0.0,
                max_value=10000.0,
                value=float(room.co2),
                step=50.0
            )

            apply_values = st.form_submit_button(
                "✅ Aplicar valores",
                use_container_width=True
            )

        if apply_values:

            success = campus.mqtt_sync.send_command(
                room_id,
                "SET_ROOM_VALUES",
                {
                    "count": int(people_input),
                    "temperature": float(temperature_input),
                    "humidity": float(humidity_input),
                    "co2": float(co2_input)
                }
            )

            if success:
                st.toast(
                    "Valores enviados ao simulador!",
                    icon="✅"
                )
            else:
                st.error("Erro ao enviar comando MQTT.")

        if room.manual_mode:

            if st.button(
                "🔄 Voltar à simulação automática",
                key=f"auto_mode_{room_id}",
                use_container_width=True
            ):

                success = campus.mqtt_sync.send_command(
                    room_id,
                    "SET_ROOM_AUTO",
                    {}
                )

                if success:
                    st.toast(
                        "Pedido de reativação enviado!",
                        icon="🔄"
                    )
                else:
                    st.error("Erro ao enviar comando MQTT.")

    # ========================================================
    # TARGET TEMPERATURE
    # ========================================================

    st.divider()

    st.subheader("🎯 Temperatura pretendida")

    st.metric(
        "Temperatura definida",
        f"{room.target_temperature:.1f} °C"
    )

    with st.form(key=f"temperature_form_{room_id}"):

        target_temp = st.slider(
            "Escolher temperatura",
            min_value=16.0,
            max_value=30.0,
            value=float(room.target_temperature),
            step=0.5,
            format="%.1f °C",
            key=f"target_temp_{room_id}"
        )

        apply_temp = st.form_submit_button(
            "Aplicar temperatura",
            use_container_width=True
        )

    if apply_temp:

        success = campus.mqtt_sync.send_command(
            room_id,
            "SET_AC",
            {
                "mode": room.ac_mode,
                "temperature": target_temp
            }
        )

        if success:
            st.toast("Comando de temperatura enviado!", icon="✅")
        else:
            st.error("Não foi possível enviar o comando MQTT.")

    # --------------------------------------------------------
    # EQUIPMENT STATES
    # --------------------------------------------------------

    st.subheader("⚙️ Equipamentos")

    lights, ac, door = st.columns(3)

    # Luzes
    lights.write(
        f"💡 Luzes: "
        f"**{'Ligadas' if room.lights_on else 'Desligadas'}**"
    )

    # Ar condicionado
    mode = room.ac_mode.removeprefix("ac_")

    ac_label = {
        "off": "Desligado",
        "cool": "Frio",
        "heat": "Quente"
    }.get(mode, "Frio")

    ac.write(
        f"❄️ Ar condicionado: **{ac_label}**"
    )

    # Porta
    door.write(
        f"🚪 Porta: "
        f"**{'🔴 Trancada' if room.door_locked else '🟢 Aberta'}**"
    )


# ============================================================
# CLASSROOM PAGE
# ============================================================

def show_classroom(room_id):

    st.title(f"🚪 Sala {room_id}")

    if st.button("⬅️ Voltar ao edifício"):

        go_back()

    st.divider()

    show_room_live(room_id)


# ============================================================
# MAIN
# ============================================================

if st.session_state.selected_room is None:

    show_building()

else:

    show_classroom(
        st.session_state.selected_room
    )