import base64
import html
import json
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from extractor import MedicalExtractor


st.set_page_config(
    page_title="E-MedBrief",
    layout="wide"
)


def to_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(path.suffix.lower(), "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"data:{mime};base64,{encoded}"


heart_url = to_data_uri(Path("images/heart_bg.png"))
heart_css = f'url("{heart_url}")' if heart_url else "none"


ICON_PULSE = '<path d="M3 12h4l2-6 4 12 2-6h6"/>'
ICON_PILL = '<path d="M10.5 20.5a4.95 4.95 0 0 1-7-7l10-10a4.95 4.95 0 0 1 7 7l-10 10z"/><path d="M8.5 8.5l7 7"/>'
ICON_FLASK = '<path d="M10 2v7.5a2 2 0 0 1-.2.9L4.7 20.5a1 1 0 0 0 .9 1.5h12.8a1 1 0 0 0 .9-1.5l-5.1-10.1a2 2 0 0 1-.2-.9V2"/><path d="M8.5 2h7"/><path d="M7 16h10"/>'
ICON_CROSS = '<path d="M12 5v14M5 12h14"/>'


def svg_inline(inner: str, size: int = 16) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )


def svg_uri(inner: str, color: str) -> str:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )
    return "data:image/svg+xml;utf8," + quote(svg)


icon_pulse = svg_uri(ICON_PULSE, "#16264A")
icon_pill = svg_uri(ICON_PILL, "#16264A")
icon_flask = svg_uri(ICON_FLASK, "#16264A")


TITLE_KEYS = ("name", "bezeichnung", "medikament", "wirkstoff", "parameter", "laborwert", "test")


def _pretty(key) -> str:
    return str(key).replace("_", " ").strip().capitalize()


def _clean(value) -> str:
    return "" if value is None else str(value).strip()


def render_items(items, icon_inner, value_keys=(), unit_keys=()) -> str:
    cards = []
    for item in items:
        value = unit = meta = title = ""

        if isinstance(item, dict):
            fields = {k: _clean(v) for k, v in item.items() if _clean(v)}
            lower = {k.lower(): k for k in fields}

            title_key = next((lower[t] for t in TITLE_KEYS if t in lower), None)
            if title_key is None and fields:
                title_key = next(iter(fields))
            if title_key:
                title = fields.pop(title_key)

            value_key = next((lower[t] for t in value_keys if t in lower and lower[t] in fields), None)
            if value_key:
                value = fields.pop(value_key)

            unit_key = next((lower[t] for t in unit_keys if t in lower and lower[t] in fields), None)
            if unit_key:
                unit = fields.pop(unit_key)

            meta_items = "".join(
                f'<span class="meta"><em>{html.escape(_pretty(k))}</em>{html.escape(v)}</span>'
                for k, v in fields.items()
            )
            if meta_items:
                meta = f'<div class="item-meta">{meta_items}</div>'
        else:
            title = _clean(item)

        value_html = ""
        if value:
            unit_html = f"<small>{html.escape(unit)}</small>" if unit else ""
            value_html = f'<div class="item-value">{html.escape(value)}{unit_html}</div>'

        cards.append(
            f'<div class="item-card">'
            f'<div class="item-icon">{svg_inline(icon_inner, 20)}</div>'
            f'<div class="item-body"><div class="item-title">{html.escape(title)}</div>{meta}</div>'
            f'{value_html}'
            f'</div>'
        )
    return "".join(cards)

def show_notice(kind: str, message: str) -> None:
    """Show a high-contrast, readable message."""
    if kind not in {"warning", "error", "success", "info"}:
        kind = "info"
    st.markdown(
        f'<div class="notice notice--{kind}">{html.escape(message)}</div>',
        unsafe_allow_html=True,
    )


st.markdown(f"""
<style>
    :root {{
        --paper: #F5F6F8;
        --surface: #FFFFFF;
        --ink: #101828;
        --navy: #16264A;
        --navy-hover: #23396B;
        --soft: #667085;
        --line: #E4E7EC;
        --green: #2E8B73;
        --tint: #ECEFF5;
        --shadow-sm: 0 1px 2px rgba(16, 24, 40, 0.04), 0 4px 14px rgba(16, 24, 40, 0.04);
    }}

    html, body, [class*="css"] {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    ::selection {{ background: rgba(22, 38, 74, 0.18); }}

    /* ---------- Hintergrund ---------- */
    .stApp {{
        background-color: var(--paper);
        background-image: radial-gradient(rgba(16, 24, 40, 0.05) 1px, transparent 1px);
        background-size: 28px 28px;
        color: var(--ink);
    }}

    /* Statische Akzentflächen: weniger Rechenlast als eine ständig animierte Fläche. */
    .stApp::after {{
        content: "";
        position: fixed;
        inset: 0;
        background: radial-gradient(
            circle at 90% 12%, rgba(22, 38, 74, 0.055), transparent 40%
        );
        pointer-events: none;
        z-index: 0;
    }}

    .block-container {{
        position: relative;
        z-index: 1;
        max-width: 1040px;
        padding-top: 4.5rem !important;
        padding-bottom: 5rem;
    }}

    #MainMenu, footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent; }}

    h1, h2, h3 {{
        color: var(--ink);
        letter-spacing: -0.025em;
        font-weight: 700 !important;
    }}

    h3 {{
        font-size: 1.45rem !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.6rem !important;
    }}

    /* ---------- Kopfzeile ---------- */
    .brand {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2.4rem;
    }}

    .brand-left {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .logo {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 11px;
        background: var(--navy);
        color: #FFFFFF;
    }}

    .brand-title {{
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--ink);
        letter-spacing: -0.02em;
    }}

    .status {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border: 1px solid var(--line);
        background: var(--surface);
        border-radius: 999px;
        color: var(--soft);
        font-size: 0.8rem;
        font-weight: 500;
    }}

    .status i {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--green);
    }}

    /* ---------- Hero: die eine kräftige Fläche ---------- */
    .input-hero {{
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(520px 280px at 100% 0%, rgba(255, 255, 255, 0.07) 0%, transparent 70%),
            var(--navy);
        border-radius: 28px;
        padding: 54px 56px;
        margin-bottom: 2rem;
    }}

    .input-hero::after {{
        content: "";
        position: absolute;
        top: 50%;
        right: 28px;
        width: 290px;
        height: 290px;
        margin-top: -145px;
        background-image: {heart_css};
        background-repeat: no-repeat;
        background-size: contain;
        background-position: center;
        opacity: 0.10;
        filter: grayscale(100%) brightness(200%);
        pointer-events: none;
    }}

    .hero-kicker {{
        display: inline-block;
        color: #C9D3E6;
        border: 1px solid rgba(255, 255, 255, 0.18);
        font-size: 0.82rem;
        font-weight: 500;
        padding: 7px 15px;
        border-radius: 999px;
        margin-bottom: 1.6rem;
    }}

    .hero-title {{
        position: relative;
        color: #FFFFFF;
        font-size: 3.4rem;
        font-weight: 700;
        line-height: 1.07;
        letter-spacing: -0.04em;
        margin-bottom: 1.3rem;
        max-width: 640px;
    }}

    .hero-text {{
        position: relative;
        color: #AEBBD3;
        font-size: 1.06rem;
        line-height: 1.7;
        max-width: 600px;
        margin: 0 0 1.9rem 0;
    }}

    .chips {{
        position: relative;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }}

    .chip {{
        display: inline-flex;
        align-items: center;
        gap: 9px;
        padding: 8px 16px 8px 13px;
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.14);
        border-radius: 999px;
        color: #E8EDF7;
        font-size: 0.86rem;
        font-weight: 500;
    }}

    .chip svg {{ opacity: 0.9; }}

    /* ---------- Eingabe ---------- */
    label[data-testid="stWidgetLabel"] p {{
        font-weight: 600 !important;
        color: var(--ink) !important;
        font-size: 0.92rem !important;
    }}

    textarea {{
        background-color: var(--surface) !important;
        color: var(--ink) !important;
        border-radius: 18px !important;
        border: 1px solid var(--line) !important;
        padding: 20px 22px !important;
        font-size: 0.98rem !important;
        line-height: 1.7 !important;
        box-shadow: var(--shadow-sm) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }}

    textarea::placeholder {{ color: #98A2B3 !important; }}

    textarea:focus {{
        border-color: var(--navy) !important;
        box-shadow: 0 0 0 4px rgba(22, 38, 74, 0.10) !important;
    }}

    /* ---------- Buttons ---------- */
    button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {{
        background: var(--navy) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 999px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.97rem !important;
        box-shadow: none !important;
        transition: background 0.2s ease, transform 0.18s ease !important;
    }}

    button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {{
        background: var(--navy-hover) !important;
        transform: translateY(-1px) !important;
        color: #FFFFFF !important;
    }}

    /* "Neuer Arztbrief": weißer Button mit stets dunkler Schrift. */
    button[kind="secondary"],
    button[data-testid="stBaseButton-secondary"] {{
        background: #FFFFFF !important;
        color: #16264A !important;
        -webkit-text-fill-color: #16264A !important;
        border: 1px solid #AAB5C8 !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.5rem !important;
        box-shadow: none !important;
    }}

    button[kind="secondary"] *,
    button[data-testid="stBaseButton-secondary"] * {{
        color: #16264A !important;
        -webkit-text-fill-color: #16264A !important;
        opacity: 1 !important;
    }}

    button[kind="secondary"]:hover,
    button[data-testid="stBaseButton-secondary"]:hover {{
        background: #ECEFF5 !important;
        border-color: #16264A !important;
    }}

    /* Neuer Arztbrief: nur dieser Button – dunkler Hintergrund, weiße Schrift. */
    .st-key-neuer_arztbrief_button button {{
        background-color: #16264A !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        border: 1px solid #16264A !important;
    }}

    .st-key-neuer_arztbrief_button button *,
    .st-key-neuer_arztbrief_button button p {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        opacity: 1 !important;
    }}

    .st-key-neuer_arztbrief_button button:hover {{
        background-color: #23396B !important;
        border-color: #23396B !important;
    }}

    /* ---------- Gut lesbare Hinweise ---------- */
    .notice {{
        padding: 15px 18px;
        border-radius: 14px;
        border: 1px solid;
        margin: 14px 0;
        font-size: 0.95rem;
        font-weight: 600;
        line-height: 1.6;
    }}
    .notice--warning {{ background: #FFF7E8; border-color: #E6C080; color: #78440D; }}
    .notice--error   {{ background: #FFF1F2; border-color: #E5A3AE; color: #8E2437; }}
    .notice--success {{ background: #EDF8F1; border-color: #B5DDC4; color: #185D3B; }}
    .notice--info    {{ background: #EEF4FC; border-color: #B8CAE4; color: #193C65; }}

    /* ---------- Analyse-Animation: nur der Spinner dreht ---------- */
    .loading-card {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 18px 20px;
        margin: 16px 0;
        border: 1px solid #CAD4E4;
        border-radius: 16px;
        background: #FFFFFF;
        color: #16264A;
        font-size: 0.96rem;
        font-weight: 600;
    }}
    .loading-wheel {{
        display: block;
        width: 24px;
        height: 24px;
        flex: 0 0 24px;
        border: 3px solid #DCE3EE;
        border-top-color: #16264A;
        border-radius: 50%;
        animation: loading-spin 0.85s linear infinite;
    }}
    @keyframes loading-spin {{
        to {{ transform: rotate(360deg); }}
    }}

    /* ---------- Kennzahlen ---------- */
    div[data-testid="stMetric"] {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 24px 28px 22px 28px;
        box-shadow: var(--shadow-sm);
    }}

    div[data-testid="stMetric"]::before {{
        content: "";
        display: block;
        width: 40px;
        height: 40px;
        margin-bottom: 16px;
        border-radius: 12px;
        background-color: var(--tint);
        background-image: url("{icon_pulse}");
        background-repeat: no-repeat;
        background-position: center;
        background-size: 20px 20px;
    }}

    div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stMetric"]::before {{
        background-image: url("{icon_pill}");
    }}

    div[data-testid="stHorizontalBlock"] > div:nth-child(3) div[data-testid="stMetric"]::before {{
        background-image: url("{icon_flask}");
    }}

    div[data-testid="stMetricLabel"] p {{
        color: var(--soft) !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: var(--navy) !important;
        font-weight: 700 !important;
        font-size: 3rem !important;
        letter-spacing: -0.045em;
        line-height: 1.1;
    }}

    /* ---------- Diagnosen ---------- */
    .diagnosis-card {{
        position: relative;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 17px 24px 17px 52px;
        margin-bottom: 12px;
        color: var(--ink);
        font-size: 0.98rem;
        font-weight: 500;
        line-height: 1.55;
        box-shadow: var(--shadow-sm);
        transition: border-color 0.2s ease;
    }}

    .diagnosis-card::before {{
        content: "";
        position: absolute;
        left: 24px;
        top: 50%;
        width: 9px;
        height: 9px;
        margin-top: -4.5px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 0 5px rgba(46, 139, 115, 0.12);
    }}

    .diagnosis-card:hover {{
        border-color: #C5CCD8;
    }}

    /* ---------- Medikamente / Laborwerte als Karten ---------- */
    .item-card {{
        display: flex;
        align-items: center;
        gap: 16px;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 16px 20px;
        margin-bottom: 10px;
        box-shadow: var(--shadow-sm);
        transition: border-color 0.2s ease;
    }}

    .item-card:hover {{
        border-color: #C5CCD8;
    }}

    .item-icon {{
        flex: none;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 42px;
        height: 42px;
        border-radius: 13px;
        background: var(--tint);
        color: var(--navy);
    }}

    .item-body {{
        flex: 1;
        min-width: 0;
    }}

    .item-title {{
        color: var(--ink);
        font-size: 1rem;
        font-weight: 600;
        line-height: 1.35;
        letter-spacing: -0.01em;
    }}

    .item-meta {{
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }}

    .meta {{
        display: inline-flex;
        align-items: baseline;
        gap: 6px;
        padding: 3px 10px;
        background: #F3F5F8;
        border-radius: 8px;
        color: var(--ink);
        font-size: 0.8rem;
        font-weight: 500;
    }}

    .meta em {{
        font-style: normal;
        color: var(--soft);
        font-weight: 500;
    }}

    .item-value {{
        flex: none;
        text-align: right;
        color: var(--navy);
        font-size: 1.55rem;
        font-weight: 700;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }}

    .item-value small {{
        display: block;
        margin-top: 3px;
        color: var(--soft);
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0;
    }}

    /* ---------- Tabellen (nur noch für Fallbacks) ---------- */
    div[data-testid="stDataFrame"] {{
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid var(--line);
        box-shadow: var(--shadow-sm);
    }}

    /* ---------- Expander ---------- */
    details {{
        background: var(--surface);
        border-radius: 16px;
        border: 1px solid var(--line) !important;
        padding: 0.5rem 0.8rem;
        box-shadow: none;
    }}

    summary {{
        font-weight: 600;
        color: var(--ink);
    }}

    hr {{
        border-color: var(--line);
        margin: 3rem 0 2rem 0;
    }}

    /* ---------- Fußzeile ---------- */
    .footer {{
        text-align: center;
        color: #98A2B3;
        font-size: 0.82rem;
        margin-top: 5rem;
    }}

    /* ---------- Mobil ---------- */
    @media (max-width: 700px) {{
        .input-hero {{ padding: 32px 26px; border-radius: 22px; }}
        .input-hero::after {{ display: none; }}
        .hero-title {{ font-size: 2.2rem; }}
        .hero-text {{ font-size: 1rem; }}
        div[data-testid="stMetricValue"] {{ font-size: 2.5rem !important; }}
    }}

    @media (prefers-reduced-motion: reduce) {{
        .loading-wheel {{ animation-duration: 2s; }}
    }}
    /* Kennzahlen: alle Texte auf den weißen Karten dunkel darstellen. */
    [data-testid="stMetric"],
    [data-testid="stMetric"] * {{
        color: #16264A !important;
        -webkit-text-fill-color: #16264A !important;
        opacity: 1 !important;
    }}

</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="brand">
    <div class="brand-left">
        <div class="logo">{svg_inline(ICON_CROSS, 20)}</div>
        <div class="brand-title">E-MedBrief</div>
    </div>
    <div class="status"><i></i>Bereit</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="input-hero">
    <div class="hero-kicker">Intelligente Auswertung von Arztbriefen</div>
    <div class="hero-title">Arztbrief intelligent analysieren</div>
    <div class="hero-text">
    E-MedBrief unterstützt Sie dabei, wichtige Informationen aus Arztbriefen automatisch zu extrahieren. Diagnosen, Medikamente und Laborwerte werden übersichtlich aufbereitet – für eine schnellere Orientierung und weniger manuellen Aufwand.
    </div>
    <div class="chips">
        <span class="chip">{svg_inline(ICON_PULSE)}Diagnosen</span>
        <span class="chip">{svg_inline(ICON_PILL)}Medikamente</span>
        <span class="chip">{svg_inline(ICON_FLASK)}Laborwerte</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Clear input and previous results before Streamlit renders the widgets again.
def reset_arztbrief():
    st.session_state["arztbrief_input"] = ""
    st.session_state.pop("ergebnis", None)
    st.session_state.pop("analysierter_text", None)


# The form prevents reruns while typing.
with st.form("arztbrief_form", clear_on_submit=False):
    arztbrief_text = st.text_area(
        "Arztbrief eingeben",
        height=240,
        placeholder="Fügen Sie hier den Arztbrief ein ...",
        key="arztbrief_input",
    )
    submitted = st.form_submit_button(
        "Medizinische Informationen extrahieren",
        type="primary",
    )

st.button(
    "Neuer Arztbrief",
    type="secondary",
    on_click=reset_arztbrief,
    key="neuer_arztbrief_button",
)

if submitted:
    # Do not show old results while starting a new analysis.
    st.session_state.pop("ergebnis", None)
    st.session_state.pop("analysierter_text", None)

    if not arztbrief_text.strip():
        show_notice("warning", "Bitte geben Sie einen Arztbrief ein.")
    else:
        loader = st.empty()
        loader.markdown(
            '<div class="loading-card">'
            '<span class="loading-wheel" aria-hidden="true"></span>'
            '<span>Arztbrief wird analysiert...</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        try:
            extractor = MedicalExtractor(model_name="llama3.1")
            ergebnis = extractor.extract_medical_info(arztbrief_text)
            st.session_state["ergebnis"] = ergebnis.model_dump()
            st.session_state["analysierter_text"] = arztbrief_text
        except Exception as exc:
            show_notice("error", f"Fehler bei der Analyse: {exc}")
        finally:
            loader.empty()

if "ergebnis" in st.session_state:

    if st.session_state.get("analysierter_text") != arztbrief_text:
        show_notice("info", "Der Arztbrief wurde geändert. Bitte starten Sie die Analyse erneut.")
    else:
        data = st.session_state["ergebnis"]

        st.divider()
        show_notice("success", "Analyse abgeschlossen!")
        st.subheader("Extrahierte Informationen")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Diagnosen", len(data["diagnosen"]))
        with col2:
            st.metric("Medikamente", len(data["medikamente"]))
        with col3:
            st.metric("Laborwerte", len(data["laborwerte"]))

        st.write("")

        st.subheader("Diagnosen")
        if data["diagnosen"]:
            for diagnose in data["diagnosen"]:
                st.markdown(
                    f'<div class="diagnosis-card">{html.escape(diagnose)}</div>',
                    unsafe_allow_html=True
                )
        else:
            show_notice("info", "Keine Diagnosen gefunden.")

        st.write("")

        col_med, col_lab = st.columns(2, gap="large")

        with col_med:
            st.subheader("Medikamente")
            if data["medikamente"]:
                st.markdown(
                    render_items(data["medikamente"], ICON_PILL),
                    unsafe_allow_html=True
                )
            else:
                show_notice("info", "Keine Medikamente gefunden.")

        with col_lab:
            st.subheader("Laborwerte")
            if data["laborwerte"]:
                st.markdown(
                    render_items(
                        data["laborwerte"],
                        ICON_FLASK,
                        value_keys=("wert", "value", "ergebnis", "messwert"),
                        unit_keys=("einheit", "unit"),
                    ),
                    unsafe_allow_html=True
                )
            else:
                show_notice("info", "Keine Laborwerte gefunden.")

        st.write("")

        with st.expander("Technische JSON-Ausgabe"):
            st.json(data)

        st.download_button(
            label="JSON herunterladen",
            data=json.dumps(data, indent=2, ensure_ascii=False),
            file_name="medextract_ergebnis.json",
            mime="application/json"
        )


st.markdown("""
<div class="footer">
    E-MedBrief [Version 1.0] · Analyse-Tool für Ihre medizinischen Berichte
</div>
""", unsafe_allow_html=True)