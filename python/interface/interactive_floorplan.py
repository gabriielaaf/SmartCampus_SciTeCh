"""SVG interativo com eventos enviados aos objetos Classroom."""

import streamlit as st

from floorplan import draw_floorplan


# ============================================================
# INTERACTIVE COMPONENT
# ============================================================

_floorplan_component = st.components.v2.component(

    name="smartcampus_floorplan_v2",

    html="""
        <div class="sc-plan">
            <div class="sc-stage"></div>
            <p class="sc-hint" aria-live="polite"></p>
        </div>
    """,

    # ========================================================
    # CSS
    # ========================================================

    css="""
        .sc-plan {
            width: 100%;
        }

        .sc-stage {
            width: 100%;
            overflow-x: auto;
            border-radius: 16px;
        }

        .sc-stage svg {
            width: 100%;
            min-width: 680px;
            height: auto;
            display: block;
        }

        .sc-hint {
            color: #8699ac;
            font-size: 13px;
            margin: 6px 0 0;
        }
    """,

    # ========================================================
    # JAVASCRIPT
    # ========================================================

    js="""
        export default function(component) {

            const {
                parentElement,
                data,
                setTriggerValue
            } = component;

            const stage = parentElement.querySelector(
                '.sc-stage'
            );

            const hint = parentElement.querySelector(
                '.sc-hint'
            );

            if (!stage) return;

            // -----------------------------------------------
            // RENDER FROM PYTHON MODEL
            // -----------------------------------------------

            if (stage._renderedSVG !== data.svg) {

                stage.innerHTML = data.svg;
                stage._renderedSVG = data.svg;

            }


            // -----------------------------------------------
            // UPDATE STATUS TEXT
            // -----------------------------------------------

            function writeStatus(svg, name, value) {

                svg.querySelectorAll(
                    `[data-status="${name}"]`
                ).forEach(element => {

                    element.textContent = value;

                });

            }


            // -----------------------------------------------
            // UPDATE VISUAL STATE
            // -----------------------------------------------

            function updateAppearance(svg, name, value) {

                // LIGHTS
                if (name === 'lights') {

                    svg.dataset.lights = String(value);

                    svg.style.setProperty(
                        '--light',
                        value ? '#dda121' : '#94a3b8'
                    );

                    svg.style.setProperty(
                        '--light-glow',
                        value ? '1' : '0'
                    );

                    writeStatus(
                        svg,
                        'lights',
                        value ? 'Ligadas' : 'Desligadas'
                    );

                }

                // AIR CONDITIONER
                else if (name === 'ac') {

                    svg.dataset.acMode = value;

                    const colors = {
                        off: '#94a3b8',
                        cool: '#0284c7',
                        heat: '#ea8333'
                    };

                    svg.style.setProperty(
                        '--ac-color',
                        colors[value]
                    );

                    svg.style.setProperty(
                        '--airflow',
                        value === 'off' ? '0' : '1'
                    );

                    const label = {
                        off: 'Desligado',
                        cool: 'Frio',
                        heat: 'Quente'
                    }[value];

                    writeStatus(svg, 'ac', label);
                    writeStatus(svg, 'ac-footer', label);

                }

                // DOOR POSITION
                else if (name === 'door') {

                    svg.dataset.doorClosed = String(value);

                    writeStatus(
                        svg,
                        'door',
                        value ? 'Fechada' : 'Aberta'
                    );

                }

                // DOOR LOCK
                else if (name === 'locked') {

                    svg.dataset.locked = String(value);

                    writeStatus(
                        svg,
                        'lock',
                        value
                            ? 'Destrancar porta'
                            : 'Trancar porta'
                    );

                    writeStatus(
                        svg,
                        'lock-footer',
                        value
                            ? 'Trancada'
                            : 'Destrancada'
                    );

                }

                // DOOR COLOR
                if (
                    name === 'door' ||
                    name === 'locked'
                ) {

                    const locked =
                        svg.dataset.locked === 'true';

                    const closed =
                        svg.dataset.doorClosed === 'true';

                    const color = locked
                        ? '#df5362'
                        : closed
                            ? '#c28b28'
                            : '#07956f';

                    svg.style.setProperty(
                        '--door-color',
                        color
                    );

                }

            }


            // -----------------------------------------------
            // HANDLE USER ACTION
            // -----------------------------------------------

            function activate(target) {

                const svg = stage.querySelector('svg');

                if (!svg) return;

                const element = target?.closest?.(
                    '[data-action]'
                );

                // Clique fora de um equipamento
                if (!element) {

                    svg.querySelector('.ac-menu')
                        ?.classList.remove('open');

                    return;
                }

                const action = element.dataset.action;

                const menu = svg.querySelector('.ac-menu');


                // -------------------------------------------
                // OPEN AC MENU
                // -------------------------------------------

                if (action === 'ac_menu') {

                    menu?.classList.toggle('open');

                    hint.textContent =
                        'Escolhe Desligado, Frio ou Quente.';

                    return;
                }

                menu?.classList.remove('open');


                // -------------------------------------------
                // LIGHTS
                // -------------------------------------------

                if (action === 'lights_toggle') {

                    const next =
                        svg.dataset.lights !== 'true';

                    updateAppearance(
                        svg,
                        'lights',
                        next
                    );

                    hint.textContent =
                        `Luzes ${next ? 'ligadas' : 'desligadas'}.`;

                }


                // -------------------------------------------
                // AIR CONDITIONER
                // -------------------------------------------

                else if (
                    [
                        'ac_off',
                        'ac_cool',
                        'ac_heat'
                    ].includes(action)
                ) {

                    const mode = action.slice(3);

                    updateAppearance(
                        svg,
                        'ac',
                        mode
                    );

                    const label = mode === 'off'
                        ? 'desligado'
                        : mode === 'cool'
                            ? 'frio'
                            : 'quente';

                    hint.textContent =
                        `Ar condicionado: ${label}.`;

                }


                // -------------------------------------------
                // OPEN / CLOSE DOOR
                // -------------------------------------------

                else if (action === 'door_toggle') {

                    const locked = svg.dataset.locked !== 'true';

                    updateAppearance(
                        svg,
                        'locked',
                        locked
                    );

                    updateAppearance(
                        svg,
                        'door',
                        locked
                    );

                    hint.textContent = locked
                        ? 'Porta trancada e fechada.'
                        : 'Porta aberta.';

                }


                // -------------------------------------------
                // LOCK / UNLOCK DOOR
                // -------------------------------------------

                else {
                    return;
                }


                // -------------------------------------------
                // SEND EVENT TO PYTHON
                // -------------------------------------------

                setTriggerValue(
                    'action',
                    action
                );

            }


            // -----------------------------------------------
            // MOUSE CLICKS
            // -----------------------------------------------

            stage.onclick = event => {

                activate(event.target);

            };


            // -----------------------------------------------
            // KEYBOARD
            // -----------------------------------------------

            stage.onkeydown = event => {

                if (
                    event.key !== 'Enter' &&
                    event.key !== ' '
                ) {
                    return;
                }

                if (
                    !event.target.closest?.('[data-action]')
                ) {
                    return;
                }

                event.preventDefault();

                activate(event.target);

            };

        }
    """
)


# ============================================================
# PYTHON CALLBACK
# ============================================================

def render_interactive_floorplan(room, campus):

    room_id = room.room_id

    widget_key = f"interactive_floorplan_{room_id}"

    def handle_action():

        result = st.session_state.get(widget_key)

        action = getattr(
            result,
            "action",
            None
        )

        current = campus.get_room(room_id)

        if current is None:
            return

        # -----------------------------------------------
        # LIGHTS
        # -----------------------------------------------

        if action == "lights_toggle":

            current.set_lights(
                not current.lights_on
            )

        # -----------------------------------------------
        # AIR CONDITIONER
        # -----------------------------------------------

        elif action in (
            "ac_off",
            "ac_cool",
            "ac_heat"
        ):

            current.set_ac(action)

        # -----------------------------------------------
        # DOOR
        # -----------------------------------------------

        elif action == "door_toggle":

            current.set_door_lock(
                not current.door_locked
            )

    # ========================================================
    # RENDER COMPONENT
    # ========================================================

    _floorplan_component(

        data={
            "svg": draw_floorplan(room)
        },

        key=widget_key,

        on_action_change=handle_action

    )