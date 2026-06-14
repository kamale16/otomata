"""
visualizer.py — Visualisasi diagram FSM menggunakan Graphviz
Menghasilkan gambar graf DFA yang bisa ditampilkan di Streamlit
"""

import graphviz
from fsm import STATE_COLORS, ACCEPT_STATES, REJECT_STATE, START_STATE


def build_fsm_diagram(current_state: str) -> graphviz.Digraph:
    """
    Membangun diagram DFA menggunakan Graphviz.
    State aktif diberi highlight khusus.
    """
    dot = graphviz.Digraph(
        name="EventBot FSM",
        graph_attr={
            "rankdir": "LR",
            "bgcolor": "#0D0D1A",
            "fontname": "Courier New",
            "fontcolor": "#E8E8FF",
            "pad": "0.3",
            "nodesep": "0.4",
            "ranksep": "0.7",
        },
        node_attr={
            "fontname": "Courier New",
            "fontsize": "9",
            "style": "filled",
        },
        edge_attr={
            "fontname": "Courier New",
            "fontsize": "8",
            "fontcolor": "#AAAADD",
            "color": "#6C63FF88",
            "arrowsize": "0.7",
        },
    )

    # State groupings by rank (untuk layout yang rapi)
    with dot.subgraph() as s:
        s.attr(rank="same")
        s.node("START")

    with dot.subgraph() as s:
        s.attr(rank="same")
        s.node("MENU_UTAMA")

    # Tambahkan semua node
    all_states = [
        "START", "MENU_UTAMA",
        "REGISTRASI_NAMA", "REGISTRASI_EMAIL", "REGISTRASI_TELEPON",
        "REGISTRASI_TIKET", "REGISTRASI_KONFIRMASI",
        "LIHAT_JADWAL", "CEK_TIKET", "INFO_VENUE", "FAQ",
        "ACCEPT", "REJECT",
    ]

    for state in all_states:
        base_color = STATE_COLORS.get(state, "#6C63FF")

        is_active = (state == current_state)
        is_accept = state in ACCEPT_STATES
        is_reject = state == REJECT_STATE
        is_start  = state == START_STATE

        if is_active:
            fillcolor = "#FFFFFF"
            fontcolor = "#0D0D1A"
            penwidth  = "3"
            color     = base_color
        elif is_accept:
            fillcolor = "#43D9AD33"
            fontcolor = "#43D9AD"
            penwidth  = "2"
            color     = "#43D9AD"
        elif is_reject:
            fillcolor = "#FF658433"
            fontcolor = "#FF6584"
            penwidth  = "2"
            color     = "#FF6584"
        elif is_start:
            fillcolor = "#8888CC33"
            fontcolor = "#8888CC"
            penwidth  = "2"
            color     = "#8888CC"
        else:
            fillcolor = base_color + "22"
            fontcolor = base_color
            penwidth  = "1"
            color     = base_color + "88"

        # Shape: double circle untuk accept, diamond untuk reject
        if is_accept:
            shape = "doublecircle"
        elif is_reject:
            shape = "diamond"
        elif is_start:
            shape = "circle"
        else:
            shape = "circle"

        label = state.replace("REGISTRASI_", "REG_")

        dot.node(
            state,
            label=label,
            shape=shape,
            fillcolor=fillcolor,
            fontcolor=fontcolor,
            color=color,
            penwidth=penwidth,
        )

    # Panah masuk ke START (konvensi DFA)
    dot.node("__start__", label="", shape="point", color="#8888CC", width="0.1")
    dot.edge("__start__", "START", color="#8888CC")

    # Tambahkan edges dari FSM
    from fsm import EventBotFSM
    tmp = EventBotFSM()
    edges = tmp.get_transitions_for_viz()

    for src, dst, label in edges:
        is_active_edge = (src == current_state)
        color    = "#FFFFFF" if is_active_edge else "#6C63FF88"
        penwidth = "2" if is_active_edge else "1"
        dot.edge(src, dst, label=label, color=color, penwidth=penwidth)

    return dot


def render_fsm_svg(current_state: str) -> str:
    """Render FSM diagram sebagai SVG string."""
    dot = build_fsm_diagram(current_state)
    svg_bytes = dot.pipe(format="svg")
    return svg_bytes.decode("utf-8")
