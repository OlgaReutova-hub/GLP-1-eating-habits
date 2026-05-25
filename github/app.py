"""Пищевое поведение на инкретинах — оценка поступления нутриентов по типовым паттернам."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "menus.json"
OPTIFAST_PATH = Path(__file__).parent / "data" / "Optifast.Json"

ACCENT = "#f57c00"
ACCENT_DARK = "#e65100"
ACCENT_LIGHT = "#fff3e0"

MEAL_LABELS = {
    "breakfast": "Завтрак",
    "lunch": "Обед",
    "snack": "Перекус",
    "dinner": "Ужин",
    "late_snack": "Поздний перекус",
}

MACRO_KEYS = ("protein_g", "fat_g", "carbs_g", "fiber_g", "cholesterol_mg")

INDICATOR_COLORS = {
    "green": "#2e7d32",
    "yellow": "#f9a825",
    "red": "#c62828",
}

MENU_DISCLAIMER = (
    "Значения — демонстрационные усреднённые оценки по типовым блюдам.\n\n"
    "Нормы потребления микро- и макронутриентов — Методические рекомендации "
    'MP 2.3.1.0253-21 «Нормы физиологических потребностей в энергии и пищевых '
    'веществах для различных групп населения Российской Федерации» '
    "(утв. Федеральной службой по надзору в сфере защиты прав потребителей "
    "и благополучия человека 22 июля 2021 г.)."
)


@lru_cache(maxsize=1)
def load_data() -> dict:
    with DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_optifast_data() -> dict:
    with OPTIFAST_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap');

        .stApp {{
            background: linear-gradient(180deg, #fff8f0 0%, #ffffff 240px);
            font-family: 'Manrope', sans-serif;
        }}

        .app-heading {{
            color: {ACCENT_DARK};
            font-size: clamp(1.5rem, 3.5vw, 2.25rem);
            font-weight: 700;
            margin: 0 0 1.25rem 0;
        }}

        .section-label {{
            color: #212121;
            font-weight: 600;
            font-size: 0.95rem;
            margin: 0.75rem 0 0.45rem 0;
        }}

        .menu-card {{
            background: #ffffff;
            border: 1px solid #ffe0b2;
            border-radius: 14px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.75rem;
            box-shadow: 0 2px 8px rgba(245, 124, 0, 0.08);
        }}

        .menu-card h4 {{
            color: {ACCENT};
            margin: 0 0 0.5rem 0;
            font-size: 1rem;
        }}

        .menu-card ul {{
            margin: 0;
            padding-left: 1.15rem;
            color: #3e2723;
        }}

        .menu-features {{
            background: linear-gradient(135deg, {ACCENT_LIGHT} 0%, #ffe0b2 100%);
            border: 1px solid #ffb74d;
            border-left: 4px solid {ACCENT};
            border-radius: 12px;
            padding: 0.9rem 1.1rem;
            margin: 0.75rem 0 1rem 0;
            font-size: 0.88rem;
            color: #4e342e;
            line-height: 1.45;
        }}

        .menu-features h4 {{
            color: {ACCENT_DARK};
            font-size: 0.95rem;
            font-weight: 700;
            margin: 0 0 0.55rem 0;
        }}

        .menu-features ul {{
            margin: 0;
            padding-left: 1.15rem;
        }}

        .menu-disclaimer {{
            font-size: 0.78rem;
            color: #607d8b;
            line-height: 1.45;
            margin-top: 0.75rem;
        }}

        .nutrients-panel {{
            background: #ffffff;
            border: 1px solid #ffe0b2;
            border-radius: 12px;
            padding: 0.85rem 1rem;
        }}

        .nutrients-panel h4 {{
            color: {ACCENT_DARK};
            font-size: 0.95rem;
            margin: 0.75rem 0 0.5rem 0;
            font-weight: 700;
        }}

        .nutrients-panel h4:first-child {{
            margin-top: 0;
        }}

        .nutrient-row {{
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 0.35rem 0.75rem;
            font-size: 0.88rem;
        }}

        .nutrient-bar-wrap {{
            grid-column: 1 / -1;
            height: 7px;
            background: #fff3e0;
            border-radius: 999px;
            overflow: hidden;
        }}

        .nutrient-norm {{
            font-size: 0.75rem;
            color: #78909c;
            margin: 0 0 0.55rem 0;
        }}

        .summary-pill {{
            display: inline-block;
            background: {ACCENT_LIGHT};
            color: {ACCENT_DARK};
            border: 1px solid #ffcc80;
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            margin: 0.15rem 0.35rem 0.15rem 0;
            font-size: 0.82rem;
            font-weight: 600;
        }}

        .hint-box {{
            background: #fff8e1;
            border-left: 4px solid #f9a825;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            color: #5d4037;
            font-size: 0.9rem;
        }}

        div[data-testid="stButton"] > button {{
            border-radius: 10px;
            font-weight: 600;
            white-space: normal;
        }}

        .st-key-show_menu_btn button {{
            background: {ACCENT} !important;
            color: #ffffff !important;
            border: 2px solid {ACCENT_DARK} !important;
        }}

        .st-key-show_menu_btn button:disabled {{
            background: #ffe0b2 !important;
            color: #ffffff !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def find_scenario(data: dict, scenario_id: str) -> dict | None:
    return next((s for s in data["scenarios"] if s["id"] == scenario_id), None)


def get_percent(entry: dict, gender: str) -> int:
    return int(entry.get(f"{gender}_percent", 0))


def indicator_from_percent(percent: int) -> str:
    if percent >= 90:
        return "green"
    if percent >= 60:
        return "yellow"
    return "red"


def get_indicator(entry: dict, gender: str) -> str:
    key = f"{gender}_indicator"
    if key in entry:
        return str(entry[key])
    return indicator_from_percent(get_percent(entry, gender))


def resolve_nutrient_display(
    entry: dict,
    nutrient_key: str,
    gender: str,
    optifast_nutrients: dict | None,
) -> tuple[float, int, str]:
    """actual, percent, indicator — с опциональным добавлением OPTIFAST."""
    base_actual = float(entry.get("actual", 0))
    norm = float(entry.get(f"norm_{gender}", 0) or 0)

    if optifast_nutrients is None:
        actual = base_actual
        percent = get_percent(entry, gender)
        indicator = get_indicator(entry, gender)
        return actual, percent, indicator

    actual = base_actual + float(optifast_nutrients.get(nutrient_key, 0))
    if norm > 0:
        percent = int(round(actual / norm * 100))
    else:
        percent = 0
    return actual, percent, indicator_from_percent(percent)


def format_unit(key: str) -> str:
    if key.endswith("_g"):
        return "г"
    if key.endswith("_mg"):
        return "мг"
    if key.endswith("_mcg"):
        return "мкг"
    return ""


def build_nutrient_rows(
    scenario: dict,
    gender: str,
    keys: tuple[str, ...],
    optifast_nutrients: dict | None = None,
) -> str:
    rows: list[str] = []
    for key in keys:
        entry = scenario["deficits"].get(key)
        if not entry:
            continue
        actual, percent, indicator = resolve_nutrient_display(
            entry, key, gender, optifast_nutrients
        )
        percent = min(percent, 150)
        bar_width = min(percent, 100)
        color = INDICATOR_COLORS.get(indicator, ACCENT)
        unit = format_unit(key)
        norm = float(entry.get(f"norm_{gender}", 0) or 0)
        label = entry["label"]
        rows.append(
            f'<div class="nutrient-row">'
            f"<span>{label}</span>"
            f'<span style="color:{ACCENT_DARK};font-weight:600;">'
            f"{actual:g} {unit} · {percent}%</span>"
            f'<div class="nutrient-bar-wrap">'
            f'<div style="width:{bar_width}%;height:100%;background:{color};'
            f'border-radius:999px;"></div></div></div>'
            f'<div class="nutrient-norm">норма: {norm:g} {unit}</div>'
        )
    return "".join(rows)


def build_menu_html(scenario: dict) -> str:
    cards: list[str] = []
    for meal_key, title in MEAL_LABELS.items():
        items = scenario["meals"].get(meal_key, [])
        if not items:
            continue
        li = "".join(f"<li>{item}</li>" for item in items)
        cards.append(f'<div class="menu-card"><h4>{title}</h4><ul>{li}</ul></div>')
    return "".join(cards)


def build_features_html(scenario: dict) -> str:
    features = scenario.get("characteristic_features", [])
    if not features:
        return ""
    li = "".join(f"<li>{item}</li>" for item in features)
    return (
        '<div class="menu-features">'
        "<h4>Характерные особенности этого пищевого паттерна</h4>"
        f"<ul>{li}</ul></div>"
    )


def select_scenario(scenario_id: str) -> None:
    st.session_state.scenario_id = scenario_id
    st.session_state.show_menu = False


def render_pattern_buttons(scenarios: list[dict]) -> None:
    st.markdown(
        '<p class="section-label">Пищевые предпочтения</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(scenarios))
    for col, scenario in zip(cols, scenarios):
        scenario_id = scenario["id"]
        label = scenario["meal_type_label"]
        selected = st.session_state.scenario_id == scenario_id
        with col:
            st.button(
                label,
                key=f"btn_{scenario_id}",
                use_container_width=True,
                type="primary" if selected else "secondary",
                on_click=select_scenario,
                args=(scenario_id,),
            )


def main() -> None:
    st.set_page_config(
        page_title="Пищевое поведение на инкретинах",
        page_icon="🍊",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    if "scenario_id" not in st.session_state:
        st.session_state.scenario_id = None
    if "show_menu" not in st.session_state:
        st.session_state.show_menu = False

    inject_styles()
    data = load_data()
    scenarios = data["scenarios"]
    labels = data["meta"]["nutrient_labels"]
    micro_keys = tuple(k for k in labels if k not in MACRO_KEYS)
    indicator_logic = data["meta"].get("indicator_logic", {})

    st.markdown(
        '<h1 class="app-heading">Пищевое поведение на инкретинах</h1>',
        unsafe_allow_html=True,
    )

    st.markdown('<p class="section-label">Пол</p>', unsafe_allow_html=True)
    st.radio(
        "Пол",
        options=["female", "male"],
        format_func=lambda g: "Женщина" if g == "female" else "Мужчина",
        horizontal=True,
        label_visibility="collapsed",
        key="gender",
        on_change=lambda: st.session_state.update(show_menu=False),
    )

    render_pattern_buttons(scenarios)

    ready = st.session_state.scenario_id is not None
    col_btn, col_hint = st.columns([1, 2])
    with col_btn:
        if st.button(
            "Показать меню",
            key="show_menu_btn",
            use_container_width=True,
            disabled=not ready,
        ):
            st.session_state.show_menu = True

    if not ready:
        with col_hint:
            st.markdown(
                '<div class="hint-box">Выберите пищевые предпочтения, '
                "затем нажмите «Показать меню».</div>",
                unsafe_allow_html=True,
            )

    if not st.session_state.show_menu or not ready:
        return

    scenario = find_scenario(data, st.session_state.scenario_id)
    if not scenario:
        st.error("Сценарий не найден.")
        return

    gender = st.session_state.gender
    gender_label = "женщина" if gender == "female" else "мужчина"

    st.markdown(
        f'<span class="summary-pill">{scenario["meal_type_label"]}</span>'
        f'<span class="summary-pill">~{scenario["kcal"]} ккал</span>'
        f'<span class="summary-pill">{gender_label}</span>',
        unsafe_allow_html=True,
    )

    col_menu, col_nutrients = st.columns([1.1, 1], gap="large")

    with col_menu:
        st.markdown("### Суточный рацион")
        st.html(build_menu_html(scenario))
        features = build_features_html(scenario)
        if features:
            st.html(features)
        st.markdown(
            f'<div class="menu-disclaimer">{MENU_DISCLAIMER.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )

    with col_nutrients:
        optifast_on = st.toggle(
            "Диета + 1 саше OPTIFAST"
            if st.session_state.get("optifast_mode", False)
            else "Диета",
            key="optifast_mode",
        )
        mode_label = "Рацион + Оптифаст" if optifast_on else "Рацион"
        st.markdown("### Макро- и микронутриенты")
        st.markdown(
            f'<p class="section-label">{mode_label}</p>',
            unsafe_allow_html=True,
        )
        optifast_nutrients = None
        if optifast_on:
            optifast_nutrients = load_optifast_data().get("nutrients", {})
        panel = (
            '<div class="nutrients-panel"><h4>Макронутриенты</h4>'
            f"{build_nutrient_rows(scenario, gender, MACRO_KEYS, optifast_nutrients)}"
            "<h4>Микронутриенты</h4>"
            f"{build_nutrient_rows(scenario, gender, micro_keys, optifast_nutrients)}"
            "</div>"
        )
        st.html(panel)
        st.caption(
            f"🟢 {indicator_logic.get('green', '')} · "
            f"🟡 {indicator_logic.get('yellow', '')} · "
            f"🔴 {indicator_logic.get('red', '')}"
        )


if __name__ == "__main__":
    main()
