"""Planta SVG interativa. Apenas lê um Classroom."""

from html import escape


def _desk(x: int, y: int) -> str:

    return f"""
    <g transform="translate({x} {y})">

      <rect width="155" height="49"
            rx="8"
            fill="#dcc6a5"
            stroke="#a68b68"
            stroke-width="2"/>

      <path d="M78 6V43" stroke="#bea887"/>

      <!-- Computadores -->

      <rect x="24" y="10" width="32" height="22"
            rx="3" fill="#34465b"/>

      <rect x="99" y="10" width="32" height="22"
            rx="3" fill="#34465b"/>

      <rect x="28" y="14" width="24" height="14"
            fill="#a9d9ea"/>

      <rect x="103" y="14" width="24" height="14"
            fill="#a9d9ea"/>

      <path
          d="M40 32v6m-10 0h20M115 32v6m-10 0h20"
          stroke="#526b82"
          stroke-width="2"/>

      <!-- Cadeiras -->

      <rect x="22" y="55" width="36" height="25"
            rx="10" fill="#dce5ed"
            stroke="#8298aa" stroke-width="2"/>

      <rect x="97" y="55" width="36" height="25"
            rx="10" fill="#dce5ed"
            stroke="#8298aa" stroke-width="2"/>

    </g>
    """


def _lamp(x: int, n: int) -> str:

    return f"""
    <g class="device"
       data-action="lights_toggle"
       tabindex="0"
       role="button"
       aria-label="Alternar as três luzes pelo foco {n}">

      <title>Alternar todas as luzes</title>

      <circle cx="{x}" cy="293" r="46"
              fill="url(#glow)"
              class="light-glow"/>

      <circle cx="{x}" cy="293" r="28"
              class="hotspot"/>

      <circle cx="{x}" cy="293" r="15"
              fill="#fff"
              stroke="var(--light)"
              stroke-width="3"/>

      <circle cx="{x}" cy="293" r="7"
              fill="var(--light)"/>

    </g>
    """


def draw_floorplan(room) -> str:

    # ========================================================
    # CLASSROOM STATE
    # ========================================================

    code = escape(str(room.room_id))

    people = max(0, int(room.people_count))
    capacity = max(0, int(room.capacity))

    lights = bool(room.lights_on)

    alarm = bool(room.alarm_on)

    alarm_color = "#dc2626" if alarm else "#64748b"

    # Compatibilidade com código que ainda usa ac_on
    mode = room.ac_mode.removeprefix("ac_")

    if room.ac_on and mode == "off":
        mode = "cool"

    locked = bool(room.door_locked)

    closed = locked


    # ========================================================
    # FURNITURE AND LIGHTS
    # ========================================================

    desks = "".join(
        _desk(x, y)
        for y in (352, 456)
        for x in (248, 513, 778)
    )

    lamps = "".join(
        _lamp(x, i)
        for i, x in enumerate(
            (362, 600, 838), 1
        )
    )

    light_color = (
        "#dda121" if lights else "#94a3b8"
    )

    ac_color = {
        "off": "#94a3b8",
        "cool": "#0284c7",
        "heat": "#ea8333",
    }[mode]

    door_color = "#df5362" if locked else "#07956f"

    ac_label = {
        "off": "Desligado",
        "cool": "Frio",
        "heat": "Quente",
    }[mode]

    # ========================================================
    # SVG
    # ========================================================

    return f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         viewBox="0 0 1200 740"
         role="group"
         aria-label="Planta interativa da sala {code}"

         data-lights="{str(lights).lower()}"
         data-ac-mode="{mode}"
         data-door-closed="{str(closed).lower()}"
         data-locked="{str(locked).lower()}"
         data-alarm="{str(alarm).lower()}"

         style="
            --light:{light_color};
            --light-glow:{1 if lights else 0};
            --ac-color:{ac_color};
            --airflow:{1 if mode != 'off' else 0};
            --door-color:{door_color};
            --alarm-color:{alarm_color}
         ">

      <!-- ================================================= -->
      <!-- CSS -->
      <!-- ================================================= -->

      <style>

        text {{
            font-family: Arial, Helvetica, sans-serif;
        }}

        .device {{
            cursor: pointer;
            outline: none;
        }}

        .hotspot {{
            fill: transparent;
        }}

        .device:hover .hotspot,
        .device:focus-visible .hotspot {{
            fill: #0284c71a;
            stroke: #0284c7;
            stroke-width: 3;
        }}

        .light-glow {{
            opacity: var(--light-glow);
        }}

        /* A porta roda fisicamente */

        .door-leaf {{
            transform-origin: 174px 610px;
            transition: transform .35s ease;
        }}

        [data-door-closed="true"] .door-leaf {{
            transform: rotate(90deg);
        }}

        /* Ar condicionado */

        .ac-airflow {{
            opacity: var(--airflow);
            stroke: var(--ac-color);
        }}

        /* Menu AC */

        .ac-menu {{
            display: none;
        }}

        .ac-menu.open {{
            display: block;
        }}

        .mode-choice rect {{
            fill: #fff;
            stroke: #cbd5e1;
            stroke-width: 2;
        }}

        .mode-choice:hover rect,
        .mode-choice:focus-visible rect {{
            fill: #e6f5fc;
            stroke: #0284c7;
        }}

        @media (prefers-reduced-motion: reduce) {{
            .door-leaf {{
                transition: none;
            }}
        }}

        .alarm-panel {{
            fill: #ffffff;
            transition: fill 0.2s ease;
        }}

        [data-alarm="true"] .alarm-panel {{
            fill: #fee2e2;
        }}

      </style>

      <!-- ================================================= -->
      <!-- DEFINITIONS -->
      <!-- ================================================= -->

      <defs>

        <pattern id="floorDots"
                 width="22" height="22"
                 patternUnits="userSpaceOnUse">

          <circle cx="1" cy="1" r="1"
                  fill="#cbd5e1"/>

        </pattern>

        <radialGradient id="glow">

          <stop stop-color="#efbd50"
                stop-opacity=".36"/>

          <stop offset="1"
                stop-color="#efbd50"
                stop-opacity="0"/>

        </radialGradient>

      </defs>

      <!-- ================================================= -->
      <!-- BACKGROUND -->
      <!-- ================================================= -->

      <rect width="1200" height="740"
            rx="20" fill="#f3f7fa"/>

      <!-- Header -->

      <text x="54" y="49"
            font-size="14"
            fill="#65788c"
            letter-spacing="2">

        SMARTCAMPUS / PISO 01

      </text>

      <text x="54" y="96"
            font-size="38"
            font-weight="700"
            fill="#182b3f">

        Sala {code}

      </text>

      <!-- Occupancy -->

      <rect x="940" y="45"
            width="204" height="60"
            rx="13"
            fill="#fff"
            stroke="#d3deeb"/>

      <text x="960" y="68"
            font-size="12"
            fill="#62768a">
        OCUPAÇÃO
      </text>

      <text x="960" y="91"
            font-size="23"
            font-weight="700"
            fill="#24394d">

        {people} / {capacity}

      </text>

      <!-- ================================================= -->
      <!-- FLOOR AND WALLS -->
      <!-- ================================================= -->

      <rect x="67" y="139"
            width="1066" height="484"
            fill="#fff"/>

      <rect x="80" y="152"
            width="1040" height="456"
            fill="#fafdfd"/>

      <rect x="80" y="152"
            width="1040" height="456"
            fill="url(#floorDots)"/>

      <path
          d="M80 609V152H1120V609H276M174 609H80"
          fill="none"
          stroke="#364c60"
          stroke-width="15"
          stroke-linejoin="round"/>

      <!-- WINDOWS -->

      <path
          d="M313 152H473M716 152H876"
          stroke="#fafdfd"
          stroke-width="19"/>

      <path
          d="M313 152H473M716 152H876"
          stroke="#49add0"
          stroke-width="9"/>

      <!-- BOARD -->

      <rect x="480" y="177"
            width="220" height="27"
            rx="4"
            fill="#14514b"/>

      <text x="590" y="196"
            text-anchor="middle"
            font-size="13"
            fill="#e5fcf2">
        QUADRO
      </text>

      <!-- TEACHER DESK -->

      <rect x="186" y="209"
            width="160" height="54"
            rx="7"
            fill="#d3b28a"
            stroke="#9f815f"
            stroke-width="2"/>

      <text x="266" y="285"
            text-anchor="middle"
            font-size="13"
            fill="#6c7a8b">
        DOCENTE
      </text>

        <!-- ================================================= -->
        <!-- ALARM - CLICKABLE -->
        <!-- ================================================= -->

        <g class="device"
        data-action="alarm_toggle"
        tabindex="0"
        role="button"
        aria-label="Ativar ou desativar alarme">

            <title>
                Clicar para ativar ou desativar o alarme
            </title>

            <!-- Painel -->

            <rect
                x="717" y="45"
                width="198" height="60"
                rx="13"
                class="alarm-panel"
                stroke="var(--alarm-color)"
                stroke-width="2"
            />

            <!-- Ícone de sirene -->

            <path
                d="M745 79h32l-6-8v-8a10 10 0 0 0-20 0v8z"
                fill="none"
                stroke="var(--alarm-color)"
                stroke-width="3"
                stroke-linejoin="round"
            />

            <circle
                cx="761" cy="85"
                r="3"
                fill="var(--alarm-color)"
            />

            <!-- Texto -->

            <text
                x="794" y="70"
                font-size="12"
                font-weight="700"
                fill="#475569"
            >
                ALARME
            </text>

            <text
                x="794" y="91"
                font-size="16"
                font-weight="700"
                fill="var(--alarm-color)"
                data-status="alarm"
            >
                {'ATIVO' if alarm else 'Desligado'}
            </text>

            <!-- Área clicável -->

            <rect
                x="717" y="45"
                width="198" height="60"
                rx="13"
                class="hotspot"
            />

        </g>

      <!-- ================================================= -->
      <!-- AIR CONDITIONER -->
      <!-- ================================================= -->

      <g class="device"
         data-action="ac_menu"
         tabindex="0"
         role="button"
         aria-label="Escolher modo de ar condicionado">

        <title>
          Escolher Desligado, Frio ou Quente
        </title>

        <rect x="979" y="185"
              width="116" height="53"
              rx="9"
              fill="#edf6fa"
              stroke="var(--ac-color)"
              stroke-width="3"/>

        <path
            d="M995 202H1078M995 211H1078"
            stroke="var(--ac-color)"
            stroke-width="2"/>

        <circle cx="1079" cy="195"
                r="4"
                fill="var(--ac-color)"/>

        <rect x="968" y="172"
              width="138" height="80"
              rx="10"
              class="hotspot"/>

      </g>

      <!-- Airflow -->

      <path
          d="M1000 240l-6 17
             m31-17l-6 17
             m31-17l-6 17"
          class="ac-airflow"
          fill="none"
          stroke-width="3"
          stroke-linecap="round"/>

      <text x="1036" y="277"
            font-size="12"
            text-anchor="middle"
            fill="#677e91">

        AC: <tspan data-status="ac">{ac_label}</tspan>

      </text>

      <!-- ================================================= -->
      <!-- LIGHTS -->
      <!-- ================================================= -->

      {lamps}

      <!-- ================================================= -->
      <!-- DESKS -->
      <!-- ================================================= -->

      {desks}

      <!-- ================================================= -->
      <!-- DOOR -->
      <!-- ================================================= -->

      <!-- Folha da porta -->

      <g class="door-leaf">

        <path
            d="M174 610V508"
            fill="none"
            stroke="var(--door-color)"
            stroke-width="8"
            stroke-linecap="round"/>

      </g>

      <!-- Arco de abertura -->

      <path
          d="M174 508A102 102 0 0 1 276 610"
          fill="none"
          stroke="var(--door-color)"
          stroke-dasharray="6 7"
          stroke-width="2"/>

      <circle cx="174" cy="610"
              r="6"
              fill="var(--door-color)"/>

      <!-- Área clicável da porta -->

      <g class="device"
         data-action="door_toggle"
         tabindex="0"
         role="button"
         aria-label="Abrir ou trancar a porta">

        <title>
          Clicar para abrir ou fechar a porta
        </title>

        <rect x="146" y="510"
              width="140" height="111"
              rx="10"
              class="hotspot"/>

      </g>

      <text x="168" y="652"
            font-size="14"
            fill="#475569">

        Porta:
        <tspan data-status="door">
          {'Fechada' if closed else 'Aberta'}
        </tspan>

      </text>

      <!-- ================================================= -->
      <!-- AC MODE MENU -->
      <!-- ================================================= -->

      <g class="ac-menu"
         aria-label="Modos do ar condicionado">

        <rect x="728" y="264"
              width="380" height="92"
              rx="15"
              fill="#e6eef5"
              stroke="#698ba8"
              stroke-width="2"/>

        <text x="749" y="287"
              font-size="13"
              fill="#354b5f">

          MODO DO AR CONDICIONADO

        </text>

        <!-- OFF -->

        <g data-action="ac_off"
           class="device mode-choice"
           role="button"
           tabindex="0"
           aria-label="Desligar ar condicionado">

          <rect x="746" y="296"
                width="109" height="45"
                rx="8"/>

          <text x="800" y="323"
                font-size="13"
                text-anchor="middle"
                fill="#334155">
            Desligado
          </text>

        </g>

        <!-- COOL -->

        <g data-action="ac_cool"
           class="device mode-choice"
           role="button"
           tabindex="0"
           aria-label="Ar condicionado frio">

          <rect x="863" y="296"
                width="109" height="45"
                rx="8"/>

          <text x="917" y="323"
                font-size="13"
                text-anchor="middle"
                fill="#0284c7">
            Frio
          </text>

        </g>

        <!-- HEAT -->

        <g data-action="ac_heat"
           class="device mode-choice"
           role="button"
           tabindex="0"
           aria-label="Ar condicionado quente">

          <rect x="980" y="296"
                width="109" height="45"
                rx="8"/>

          <text x="1034" y="323"
                font-size="13"
                text-anchor="middle"
                fill="#d97706">
            Quente
          </text>

        </g>

      </g>

      <!-- ================================================= -->
      <!-- STATUS BAR -->
      <!-- ================================================= -->

      <text x="66" y="710"
            font-size="14"
            fill="#60758a">

        Luzes:
        <tspan data-status="lights">
          {'Ligadas' if lights else 'Desligadas'}
        </tspan>

        · AC:
        <tspan data-status="ac-footer">
          {ac_label}
        </tspan>

        · Fechadura:
        <tspan data-status="lock-footer">
          {'Trancada' if locked else 'Destrancada'}
        </tspan>

      </text>

      <text x="1125" y="712"
            text-anchor="end"
            font-size="12"
            fill="#8497a9">

        PLANTA ILUSTRATIVA

      </text>

    </svg>
    """